from dataclasses import Field
from typing import Any, ClassVar, Dict, Literal, Protocol, Union

from typing_extensions import Annotated


def is_variable(s: Any):
    return isinstance(s, str) and s.startswith(r"{{") and s.endswith(r"}}")


def to_variable(s: str):
    if is_variable(s):
        return s
    return r"{{" + s + r"}}"


Variable = Annotated[str, is_variable, to_variable]


class AliasPath(list): ...


def get_alias(alias: Union[str, AliasPath, None]):
    if isinstance(alias, AliasPath):
        return alias[-1]
    return alias


MODEL_TYPES = Literal["base", "feature_template", "parcel"]


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Field]]
