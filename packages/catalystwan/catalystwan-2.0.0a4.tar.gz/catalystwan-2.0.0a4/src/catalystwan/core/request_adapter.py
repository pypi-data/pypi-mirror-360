from __future__ import annotations

import logging
from copy import copy
from dataclasses import dataclass, field, fields, is_dataclass
from string import Formatter
from typing import Any, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union, cast

from catalystwan.abc import RequestAdapterInterface, ResponseInterface, SessionInterface
from catalystwan.abc.types import HTTP_METHOD, JSON
from catalystwan.core.exceptions import (
    CatalystwanModelValidationError,
    CatalystwanResponseTypeError,
)
from catalystwan.core.models.deserialize import deserialize
from catalystwan.core.models.serialize import serialize
from catalystwan.core.models.utils import count_matching_keys
from catalystwan.core.types import DataclassInstance
from typing_extensions import get_args, get_origin

DataclassType = TypeVar("DataclassType", bound=DataclassInstance)
ReturnType = TypeVar("ReturnType")
Payload = TypeVar("Payload")


@dataclass
class JsonContent:
    # data extracted from a specific key
    extracted_data: JSON
    # raw version of the data
    raw_data: JSON


# Used for data extraction from a response, when it takes a specific form.
# data_key is the key to pull data from, if required_keys are present
@dataclass
class ResponseDataPath:
    data_key: str
    required_keys: List[str] = field(default_factory=list)

    def is_data_available(self, data: Dict[str, Any]) -> bool:
        keys = self.required_keys + [self.data_key]
        return all(key in data for key in keys)

    def get_data(self, data: Dict[str, Any]) -> JSON:
        return data[self.data_key]


class RequestAdapter(RequestAdapterInterface):
    known_data_paths: List[ResponseDataPath] = [
        ResponseDataPath(data_key="data", required_keys=["header"]),
        ResponseDataPath(data_key="devices", required_keys=["header"]),
    ]

    def __init__(self, session: SessionInterface, logger: Optional[logging.Logger] = None):
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def request(
        self,
        method: HTTP_METHOD,
        url: str,
        payload: Union[Payload, JSON] = None,
        params: Optional[dict] = None,
        return_type: Optional[Type[ReturnType]] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> Union[ReturnType, JSON, bytes, None]:
        if params:
            path_keys = [
                field_name
                for _, field_name, _, _ in Formatter().parse(url)
                if field_name is not None
            ]
            url = url.format_map({path_key: params.pop(path_key) for path_key in path_keys})
        if is_dataclass(payload):
            payload = serialize(cast(DataclassInstance, payload), to_json=True)
        response = self.session.request(
            method=method,
            url=url,
            json=payload,
            params=params,
            headers=headers,
            **kwargs,
        )

        content = self.__get_content(response)
        return self.__prepare_return_type(return_type, content)

    def __prepare_return_type(
        self, return_type: Optional[Type[ReturnType]], content: Union[JsonContent, str, bytes, None]
    ) -> Union[ReturnType, JSON, bytes, None]:
        if is_dataclass(return_type):
            return cast(
                ReturnType, self.__get_dataclass(return_type=return_type, model_payload=content)
            )
        # If we are expecting a list, it should be found within the extracted_data - the response was either a list from
        # the beginning or we extracted it from an appropriate key
        elif (
            get_origin(return_type) is list
            and type(content) is JsonContent
            and type(content.extracted_data) is list
        ):
            return [
                self.__parse_list(get_args(return_type)[0], value)
                for value in content.extracted_data
            ]
        else:
            extracted_data: Union[JSON, bytes, None]
            if isinstance(content, JsonContent):
                extracted_data = content.extracted_data
            else:
                extracted_data = content
            if type(extracted_data) is not return_type and return_type is not None:
                self.logger.warning(
                    f"Server returned unexpected data. Expected: {return_type}, received {type(extracted_data)}"
                )
            return extracted_data

    def __get_content(self, response: ResponseInterface) -> Union[JsonContent, str, bytes, None]:
        content_type: str = response.headers.get("content-type", "")
        if not content_type:
            return None
        if content_type.startswith("application/json"):
            return self.__extract_json_data(response.json())
        if content_type.startswith("text"):
            return response.text
        else:
            return response.content

    def __parse_list(
        self, arg_type: Type[ReturnType], values: Union[JSON]
    ) -> Union[ReturnType, JSON]:
        if is_dataclass(arg_type):
            model_payload = self.__extract_json_data(values)
            return cast(
                ReturnType, self.__get_dataclass(return_type=arg_type, model_payload=model_payload)
            )
        elif get_origin(arg_type) is list:
            if not isinstance(values, list):
                raise CatalystwanResponseTypeError(
                    f"Expected type: list. Type received: {type(values)}"
                )
            return [self.__parse_list(get_args(arg_type)[0], value) for value in values]
        else:
            return values

    def __extract_json_data(self, data: JSON) -> JsonContent:
        if not isinstance(data, dict):
            return JsonContent(extracted_data=data, raw_data=data)
        for known_data_path in self.known_data_paths:
            if known_data_path.is_data_available(data):
                return JsonContent(extracted_data=known_data_path.get_data(data), raw_data=data)
        return JsonContent(extracted_data=data, raw_data=data)

    def __get_dataclass(
        self, return_type: Type[DataclassType], model_payload: Union[JsonContent, str, bytes, None]
    ) -> DataclassType:
        # Get a dataclass using payload from a response.
        # This method includes a bit of brute-force trickery, to fight inconsistent schemas.
        # Sometimes the schema requires are to pull data from a specific key, while at other times it doesn't.
        # This method tries to check which version - extracted or raw - matches better.
        @dataclass
        class ModelPayload:
            name: str
            data: JSON
            priority: int

        @dataclass
        class ModelReturn:
            model: DataclassType
            payload: ModelPayload

        if not isinstance(model_payload, JsonContent):
            raise CatalystwanResponseTypeError(
                f"Expected data for {return_type} model. Received data of type {type(model_payload)} instead."
            )

        data_sources = [
            ModelPayload(data=model_payload.extracted_data, name="extracted_data", priority=1),
            ModelPayload(data=model_payload.raw_data, name="raw_data", priority=0),
        ]

        field_names = [f.metadata.get("alias") or f.name for f in fields(return_type)]
        # Empty dataclass, return as is
        if not field_names:
            return return_type()

        valid_models: List[ModelReturn] = []
        for data_source in data_sources:
            try:
                if isinstance(data_source.data, dict):
                    valid_models.append(
                        ModelReturn(
                            model=deserialize(return_type, **data_source.data), payload=data_source
                        )
                    )
                else:
                    self.logger.debug(
                        f"Failed to create model {return_type} using {data_source.name} source. Reason: data of type {type(data_source.data)} is invalid"
                    )
            except CatalystwanModelValidationError:
                self.logger.debug(
                    f"Failed to create model {return_type} using {data_source.name} source."
                )

        if not valid_models:
            raise CatalystwanResponseTypeError(
                f"Failed to create model {return_type} from given data."
            )
        if len(valid_models) == 1:
            return valid_models[0].model

        # return model that matches best with the input
        valid_models.sort(
            key=lambda x: (
                count_matching_keys(x.model, cast(dict, x.payload.data)),
                x.payload.priority,
            ),
            reverse=True,
        )
        return valid_models[0].model

    def param_checker(self, required_params: List[Tuple[Any, Any]], excluded_params: List[Any]):
        for param in excluded_params:
            if param is not None:
                return False
        for param_value, expected_type in required_params:
            if param_value is None:
                return False
            origin = get_origin(expected_type)
            if origin is Any:
                continue
            elif origin is None:
                if type(param_value) is not expected_type:
                    return False
            elif origin is Literal:
                if param_value not in get_args(expected_type):
                    return False
            # This part assumes List and Unions are not overly complex, allowing get_args to flatten the list of types
            elif origin is list:
                if type(param_value) is not list:
                    return False
                args = get_args(expected_type)
                if Any in args:
                    continue
                if type(param_value) not in args:
                    return False
            elif origin is Union:
                if type(param_value) not in get_args(expected_type):
                    return False
            else:
                continue
        return True

    def __copy__(self) -> RequestAdapter:
        return RequestAdapter(session=copy(self.session), logger=self.logger)
