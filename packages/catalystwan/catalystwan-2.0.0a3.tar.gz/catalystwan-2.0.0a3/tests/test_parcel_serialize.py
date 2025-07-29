from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, Literal, Optional, Union

from catalystwan.core.models.serialize import serialize
from catalystwan.core.types import AliasPath, Variable


def test_model_serialize_json():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
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

    m = Model(
        parcel_name="name",
        parcel_description="desc",
        int_field=1,
        bool_field=True,
        str_field="test",
        literal_field="test",
        submodel_field=Submodel(int_field=1),
        variable_field=r"{{ var }}",
        union_field=IPv4Address("10.0.0.1"),
    )

    serialized = serialize(m, to_json=True)
    expected = {
        "name": "name",
        "description": "desc",
        "data": {
            "int_field": {"value": 1, "option_type": "global"},
            "bool_field": {"value": True, "option_type": "global"},
            "str_field": {"value": "test", "option_type": "global"},
            "literal_field": {"value": "test", "option_type": "default"},
            "variable_field": {"value": r"{{ var }}", "option_type": "variable"},
            "union_field": {"value": "10.0.0.1", "option_type": "global"},
            "submodel_field": {
                "int_field": {"value": 1, "option_type": "global"},
            },
        },
    }
    assert serialized == expected


def test_model_serialize():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
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

    m = Model(
        parcel_name="name",
        parcel_description="desc",
        int_field=1,
        bool_field=True,
        str_field="test",
        literal_field="test",
        submodel_field=Submodel(int_field=1),
        variable_field=r"{{ var }}",
        union_field=IPv4Address("10.0.0.1"),
    )

    serialized = serialize(m, by_alias=False, to_json=False)
    expected = {
        "int_field": 1,
        "bool_field": True,
        "str_field": "test",
        "literal_field": "test",
        "variable_field": r"{{ var }}",
        "union_field": IPv4Address("10.0.0.1"),
        "submodel_field": {
            "int_field": 1,
        },
        "parcel_name": "name",
        "parcel_description": "desc",
    }
    assert serialized == expected


def test_model_serialize_exclude_none():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int
        optional_field: Optional[str]

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
        int_field: int = field(metadata={"alias": AliasPath(["data", "int_field"])})
        optional_field: Optional[str] = field(
            metadata={"alias": AliasPath(["data", "optional_field"])}
        )
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    m = Model(
        parcel_name="name",
        parcel_description="desc",
        int_field=1,
        optional_field=None,
        submodel_field=Submodel(int_field=1, optional_field=None),
    )

    serialized = serialize(m, by_alias=False, to_json=False)
    expected = {
        "int_field": 1,
        "submodel_field": {
            "int_field": 1,
        },
        "parcel_name": "name",
        "parcel_description": "desc",
    }
    assert serialized == expected


def test_model_serialize_include_none():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        int_field: int
        optional_field: Optional[str]

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "parcel"

        submodel_field: Submodel = field(metadata={"alias": AliasPath(["data", "submodel_field"])})
        int_field: int = field(metadata={"alias": AliasPath(["data", "int_field"])})
        optional_field: Optional[str] = field(
            metadata={"alias": AliasPath(["data", "optional_field"])}
        )
        parcel_name: str = field(metadata={"alias": "name", "wrap": False})
        parcel_description: Optional[str] = field(
            default=None, metadata={"alias": "description", "wrap": False}
        )

    m = Model(
        parcel_name="name",
        parcel_description="desc",
        int_field=1,
        optional_field=None,
        submodel_field=Submodel(int_field=1, optional_field=None),
    )

    serialized = serialize(m, by_alias=False, to_json=False, exclude_none=False)
    expected = {
        "int_field": 1,
        "optional_field": None,
        "submodel_field": {
            "int_field": 1,
            "optional_field": None,
        },
        "parcel_name": "name",
        "parcel_description": "desc",
    }
    assert serialized == expected
