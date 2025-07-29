from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, Literal, Optional, Union

from catalystwan.core.models.deserialize import deserialize
from catalystwan.core.types import AliasPath, Variable


def test_simple_deserialize():
    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int = field(metadata={"alias": AliasPath(["data", "int_field"])})
        bool_field: bool = field(metadata={"alias": AliasPath(["data", "bool_field"])})
        str_field: str = field(metadata={"alias": AliasPath(["data", "str_field"])})
        variable_field: Union[int, Variable] = field(
            metadata={"alias": AliasPath(["data", "variable_field"])}
        )
        union_field: Union[IPv6Address, IPv4Address] = field(
            metadata={"alias": AliasPath(["data", "union_field"])}
        )
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        literal_field: Literal["test", 1] = field(
            default="test", metadata={"alias": AliasPath(["data", "literal_field"])}
        )
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    data = {
        "name": "name",
        "int_field": 1,
        "bool_field": True,
        "str_field": "test",
        "literal_field": "test",
        "variable_field": r"{{ var }}",
        "union_field": IPv4Address("10.0.0.1"),
    }
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.bool_field is True
    assert m.str_field == "test"
    assert m.literal_field == "test"
    assert m.parcel_name == "name"
    assert m.parcel_description is None
    assert m.variable_field == r"{{ var }}"
    assert m.union_field == IPv4Address("10.0.0.1")


def test_simple_payload_deserialize():
    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int = field(metadata={"alias": AliasPath(["data", "int_field"])})
        bool_field: bool = field(metadata={"alias": AliasPath(["data", "bool_field"])})
        str_field: str = field(metadata={"alias": AliasPath(["data", "str_field"])})
        variable_field: Union[int, Variable] = field(
            metadata={"alias": AliasPath(["data", "variable_field"])}
        )
        union_field: Union[IPv6Address, IPv4Address] = field(
            metadata={"alias": AliasPath(["data", "union_field"])}
        )
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        literal_field: Literal["test", 1] = field(
            default="test", metadata={"alias": AliasPath(["data", "literal_field"])}
        )
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    data = {
        "name": "name",
        "data": {
            "int_field": {"value": 1, "option_type": "global"},
            "bool_field": {"value": True, "option_type": "global"},
            "str_field": {"value": "test", "option_type": "global"},
            "literal_field": {"value": "test", "option_type": "default"},
            "variable_field": {"value": r"{{ var }}", "option_type": "variable"},
            "union_field": {"value": "10.0.0.1", "option_type": "global"},
        },
    }
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.bool_field is True
    assert m.str_field == "test"
    assert m.literal_field == "test"
    assert m.parcel_name == "name"
    assert m.parcel_description is None
    assert m.variable_field == r"{{ var }}"
    assert m.union_field == IPv4Address("10.0.0.1")


def test_submodel():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    data = {
        "parcel_name": "name",
        "parcel_description": "desc",
        "submodel_field": {"int_field": 1},
    }

    m = deserialize(Model, **data)

    assert m.parcel_name == "name"
    assert m.parcel_description == "desc"
    assert isinstance(m.submodel_field, Submodel) is True
    assert m.submodel_field.int_field == 1


def test_submodel_payload():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    data = {
        "name": "name",
        "description": "desc",
        "data": {
            "submodel_field": {
                "int_field": {
                    "value": 1,
                    "option_type": "global",
                }
            }
        },
    }

    m = deserialize(Model, **data)

    assert m.parcel_name == "name"
    assert m.parcel_description == "desc"
    assert isinstance(m.submodel_field, Submodel) is True
    assert m.submodel_field.int_field == 1
