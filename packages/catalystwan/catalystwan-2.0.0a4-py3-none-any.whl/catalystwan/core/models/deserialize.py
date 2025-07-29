from collections import deque
from copy import deepcopy
from dataclasses import dataclass, fields, is_dataclass
from functools import reduce
from inspect import isclass, unwrap
from typing import Any, Dict, List, Literal, Optional, Protocol, Tuple, Type, TypeVar, Union, cast

from catalystwan.core.exceptions import (
    CatalystwanModelInputException,
    CatalystwanModelValidationError,
)
from catalystwan.core.models.utils import count_matching_keys
from catalystwan.core.types import MODEL_TYPES, AliasPath, DataclassInstance
from typing_extensions import Annotated, get_args, get_origin, get_type_hints

T = TypeVar("T", bound=DataclassInstance)


class ValueExtractorCallable(Protocol):
    def __call__(self, field_value: Any) -> Any: ...


@dataclass
class ExtractedValue:
    value: Any
    exact_match: bool
    matched_keys: Optional[int] = None


class ModelDeserializer:
    def __init__(self, model: Type[T]) -> None:
        self.model = model
        try:
            self.model_type: MODEL_TYPES = model._catalystwan_model_type  # type: ignore[attr-defined]
        except AttributeError:
            self.model_type = "base"
        self._exceptions: List[
            Union[CatalystwanModelInputException, CatalystwanModelValidationError]
        ] = []
        # different models wrap their values in different ways, hence
        # the need for multiple extractors
        self.VALUE_EXTRACTORS: Dict[MODEL_TYPES, ValueExtractorCallable] = {
            "base": self.__value_extractor_base,
            "feature_template": self.__value_extractor_ft,
            "parcel": self.__value_extractor_parcel,
        }

    def deserialize(self, *args, **kwargs) -> Tuple[List[Any], Dict[str, Any]]:
        new_args, new_kwargs = self.__transform_model_input(
            self.model, self.__value_extractor, *args, **kwargs
        )
        # Input errors are aggregated and thrown out as a bundle
        self.__check_errors()
        return new_args, new_kwargs

    def __check_errors(self):
        if self._exceptions:
            # Put exceptions from current model first
            self._exceptions.sort(key=lambda x: isinstance(x, CatalystwanModelValidationError))
            current_model_errors = sum(
                isinstance(x, CatalystwanModelInputException) for x in self._exceptions
            )
            message = f"{current_model_errors} validation errors for {self.model.__name__}\n"
            for exc in self._exceptions:
                message += f"{exc}\n"
            raise CatalystwanModelValidationError(message)

    def __extract_type(self, field_type: Any, field_value: Any, field_name: str) -> ExtractedValue:
        origin = get_origin(field_type)
        # check for simple types and classes
        if origin is None:
            if field_type is Any or isinstance(field_value, field_type):
                return ExtractedValue(value=field_value, exact_match=True)
            # Do not cast bool values
            elif field_type is bool:
                ...
            # False/Empty values (like empty string or list) can match to None
            elif field_type is type(None):
                if not field_value:
                    return ExtractedValue(value=None, exact_match=False)
            elif is_dataclass(field_type):
                model_instance = deserialize(
                    cast(Type[DataclassInstance], field_type), **field_value
                )
                return ExtractedValue(
                    value=model_instance,
                    exact_match=False,
                    matched_keys=count_matching_keys(model_instance, field_value),
                )
            elif isclass(unwrap(field_type)):
                if isinstance(field_value, dict):
                    return ExtractedValue(value=field_type(**field_value), exact_match=False)
                else:
                    try:
                        return ExtractedValue(value=field_type(field_value), exact_match=False)
                    except ValueError:
                        raise CatalystwanModelInputException(
                            f"Unable to match or cast input value for {field_name} [expected_type={unwrap(field_type)}, input={field_value}, input_type={type(field_value)}]"
                        )
        # List is an exact match only if all of its elements are
        elif origin is list:
            if isinstance(field_value, list):
                values = []
                exact_match = True
                for value in field_value:
                    extracted_value = self.__extract_type(
                        get_args(field_type)[0], value, field_name
                    )
                    values.append(extracted_value.value)
                    if not extracted_value.exact_match:
                        exact_match = False
                return ExtractedValue(value=values, exact_match=exact_match)
        elif origin is Literal:
            for arg in get_args(field_type):
                try:
                    if type(arg)(field_value) == arg:
                        return ExtractedValue(
                            value=type(arg)(field_value), exact_match=type(arg) is type(field_value)
                        )
                except Exception:
                    continue
        elif origin is Annotated:
            validator, caster = field_type.__metadata__
            if validator(field_value):
                return ExtractedValue(value=field_value, exact_match=True)
            return ExtractedValue(value=caster(field_value), exact_match=False)
        # When parsing Unions, try to find the best match. Currently, it involves:
        # 1. Finding the exact match
        # 2. If not found, favors dataclasses - sorted by number of matched keys, then None values
        # 3. If no dataclasses are present, return the leftmost matched argument
        elif origin is Union:
            matches: List[ExtractedValue] = []
            for arg in get_args(field_type):
                try:
                    extracted_value = self.__extract_type(arg, field_value, field_name)
                    # exact match, return
                    if extracted_value.exact_match:
                        return extracted_value
                    else:
                        matches.append(extracted_value)
                except Exception:
                    continue
            # Only one element matched, return
            if len(matches) == 1:
                return matches[0]
            # Only non-exact matches left, sort and return first element
            elif len(matches) > 1:
                matches.sort(
                    key=lambda x: (x.matched_keys is not None, x.matched_keys, x.value is None),
                    reverse=True,
                )
                return matches[0]
        # Correct type not found, add exception
        raise CatalystwanModelInputException(
            f"Unable to match or cast input value for {field_name} [expected_type={unwrap(field_type)}, input={field_value}, input_type={type(field_value)}]"
        )

    def __transform_model_input(
        self, cls: Type[T], value_extractor: ValueExtractorCallable, *args, **kwargs
    ):
        args_copy = deque(deepcopy(args))
        kwargs_copy = deepcopy(kwargs)
        new_args = []
        new_kwargs = {}
        field_types = get_type_hints(cls, include_extras=True)
        for field in fields(cls):
            if not field.init:
                continue
            field_type = field_types[field.name]
            # check args first
            if len(args_copy) > 0:
                field_value = args_copy.popleft()
                try:
                    new_args.append(
                        self.__extract_type(
                            field_type, value_extractor(field_value), field.name
                        ).value
                    )
                except (
                    CatalystwanModelInputException,
                    CatalystwanModelValidationError,
                ) as e:
                    self._exceptions.append(e)
                continue

            alias = field.metadata.get("alias", None)
            alias_path = alias if isinstance(alias, AliasPath) else [alias]
            try:
                # get value from given dict path
                field_value = reduce(dict.get, alias_path, kwargs_copy)  # type: ignore[arg-type]
            except TypeError:
                field_value = None
            if field_value is None:
                if field.name in kwargs_copy:
                    field_value = kwargs_copy[field.name]
                else:
                    continue
            try:
                new_kwargs[field.name] = self.__extract_type(
                    field_type, value_extractor(field_value), field.name
                ).value
            except (
                CatalystwanModelInputException,
                CatalystwanModelValidationError,
            ) as e:
                self._exceptions.append(e)
        return new_args, new_kwargs

    @property
    def __value_extractor(self) -> ValueExtractorCallable:
        return self.VALUE_EXTRACTORS[self.model_type]

    def __value_extractor_base(self, field_value: Any) -> Any:
        return field_value

    def __value_extractor_ft(self, field_value: Any) -> Any:
        if isinstance(field_value, dict):
            if "vipType" in field_value and field_value["vipType"] == "ignore":
                return None
            if "vipValue" in field_value:
                return field_value["vipValue"]
        return field_value

    def __value_extractor_parcel(self, field_value: Any) -> Any:
        if (
            isinstance(field_value, dict)
            and "option_type" in field_value
            and "value" in field_value
        ):
            return field_value["value"]
        return field_value


def deserialize(catalystwan_model: Type[T], *args, **kwargs) -> T:
    new_args, new_kwargs = ModelDeserializer(catalystwan_model).deserialize(*args, **kwargs)

    return catalystwan_model(*new_args, **new_kwargs)
