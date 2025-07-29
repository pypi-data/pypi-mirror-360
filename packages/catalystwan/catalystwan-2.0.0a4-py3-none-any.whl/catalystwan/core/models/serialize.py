from dataclasses import Field, fields, is_dataclass
from typing import Any, Dict, List, Optional, Protocol, Union, cast

from catalystwan.core.encoder import serialize_model_value
from catalystwan.core.types import MODEL_TYPES, AliasPath, DataclassInstance, is_variable


class ValueWrapperCallable(Protocol):
    def __call__(self, field: Field, field_value: Any, to_json: bool): ...


class ModelSerializer:
    def __init__(self, model: DataclassInstance):
        self.model = model
        try:
            self.model_type: MODEL_TYPES = model._catalystwan_model_type  # type: ignore[attr-defined]
        except AttributeError:
            self.model_type = "base"
        # Values need to be wrapped in a specific form, depending on the model type
        self.VALUE_WRAPPERS: Dict[MODEL_TYPES, ValueWrapperCallable] = {
            "base": self.__value_wrapper_base,
            "feature_template": self.__value_wrapper_ft,
            "parcel": self.__value_wrapper_parcel,
        }

    def serialize(
        self, by_alias: bool = True, to_json: bool = False, exclude_none: bool = True
    ) -> Dict[str, Any]:
        return_dict: Dict[str, Any] = {}
        for field in fields(self.model):
            return_value = getattr(self.model, field.name)
            # skip None values, if needed
            if exclude_none and return_value is None:
                continue

            return_value = self.__value_serializer(
                field, return_value, by_alias, to_json, exclude_none
            )
            if by_alias:
                alias: Optional[Union[str, AliasPath]] = field.metadata.get("alias")
                field_name = alias or field.name
                key_path = field_name if isinstance(field_name, AliasPath) else [field_name]
                self.__insert_key(return_dict, key_path, return_value)
            else:
                return_dict[field.name] = return_value
        return return_dict

    def __value_serializer(
        self,
        field: Field,
        field_value: Any,
        by_alias: bool,
        to_json: bool,
        exclude_none: bool,
    ) -> Any:
        return_value: Any
        if is_dataclass(field_value):
            return_value = serialize(
                model=cast(DataclassInstance, field_value),
                by_alias=by_alias,
                to_json=to_json,
                exclude_none=exclude_none,
            )
        elif isinstance(field_value, list):
            if len(field_value) == 0 or not is_dataclass(field_value[0]):
                return_value = serialize_model_value(field_value, to_json)
            else:
                return_value = [
                    serialize(
                        model=v,
                        by_alias=by_alias,
                        to_json=to_json,
                        exclude_none=exclude_none,
                    )
                    for v in field_value
                ]
        else:
            return_value = serialize_model_value(field_value, to_json)

        return self.__value_wrapper(field=field, field_value=return_value, to_json=to_json)

    @property
    def __value_wrapper(self) -> ValueWrapperCallable:
        return self.VALUE_WRAPPERS[self.model_type]

    def __value_wrapper_base(self, field: Field, field_value: Any, to_json: bool):
        return field_value

    def __value_wrapper_ft(self, field: Field, field_value: Any, to_json: bool) -> Any:
        if not field.metadata.get("wrap", True) or not to_json:
            return field_value
        if is_variable(field_value):
            return {
                "vipType": "variable",
                "vipValue": field_value,
                "vipObjectType": field.metadata.get("object_type"),
            }
        else:
            return {
                "vipType": "constant",
                "vipValue": field_value,
                "vipObjectType": field.metadata.get("object_type"),
            }

    def __value_wrapper_parcel(self, field: Field, field_value: Any, to_json: bool) -> Any:
        if (
            not field.metadata.get("wrap", True)
            or (isinstance(field_value, (list, dict)) or is_dataclass(field_value))
            or not to_json
        ):
            return field_value
        if is_variable(field_value):
            return {"option_type": "variable", "value": field_value}
        elif field_value == field.default:
            return {"option_type": "default", "value": field_value}
        else:
            return {"option_type": "global", "value": field_value}

    def __insert_key(self, d: Dict[str, Any], key_path: List[str], value: Any):
        nested = d
        for key in key_path[:-1]:
            nested = nested.setdefault(key, {})
        nested[key_path[-1]] = value


def serialize(
    model: DataclassInstance,
    by_alias: bool = True,
    to_json: bool = False,
    exclude_none: bool = True,
) -> Dict[str, Any]:
    if not is_dataclass(model):
        raise Exception

    return ModelSerializer(model=model).serialize(
        by_alias=by_alias, to_json=to_json, exclude_none=exclude_none
    )
