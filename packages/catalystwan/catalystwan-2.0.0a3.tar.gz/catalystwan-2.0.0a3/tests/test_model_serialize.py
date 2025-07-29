from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import Literal, Optional, Union

from catalystwan.core.models.serialize import serialize


def test_model_serialize_json():
    @dataclass
    class Submodel:
        int_field: int

    @dataclass
    class Model:
        int_field: int
        bool_field: bool
        str_field: str
        literal_field: Literal["test", 1]
        union_field: Union[IPv6Address, IPv4Address]
        submodel_field: Submodel
        alias_field: str = field(metadata={"alias": "alias"})

    m = Model(
        int_field=1,
        bool_field=True,
        str_field="test",
        literal_field="test",
        union_field=IPv4Address("10.0.0.1"),
        submodel_field=Submodel(int_field=1),
        alias_field="a",
    )

    serialized = serialize(m, to_json=True)
    expected = {
        "int_field": 1,
        "bool_field": True,
        "str_field": "test",
        "literal_field": "test",
        "union_field": "10.0.0.1",
        "submodel_field": {
            "int_field": 1,
        },
        "alias": "a",
    }
    assert serialized == expected


def test_model_serialize():
    @dataclass
    class Submodel:
        int_field: int

    @dataclass
    class Model:
        int_field: int
        bool_field: bool
        str_field: str
        literal_field: Literal["test", 1]
        union_field: Union[IPv6Address, IPv4Address]
        submodel_field: Submodel
        alias_field: str = field(metadata={"alias": "alias"})

    m = Model(
        int_field=1,
        bool_field=True,
        str_field="test",
        literal_field="test",
        union_field=IPv4Address("10.0.0.1"),
        submodel_field=Submodel(int_field=1),
        alias_field="a",
    )

    serialized = serialize(m)
    expected = {
        "int_field": 1,
        "bool_field": True,
        "str_field": "test",
        "literal_field": "test",
        "union_field": IPv4Address("10.0.0.1"),
        "submodel_field": {
            "int_field": 1,
        },
        "alias": "a",
    }
    assert serialized == expected


def test_model_serialize_exclude_none():
    @dataclass
    class Submodel:
        int_field: int
        optional_field: Optional[str]

    @dataclass
    class Model:
        int_field: int
        optional_field: Optional[str]
        submodel_field: Submodel

    m = Model(
        int_field=1,
        optional_field=None,
        submodel_field=Submodel(int_field=1, optional_field=None),
    )

    serialized = serialize(m)
    expected = {
        "int_field": 1,
        "submodel_field": {
            "int_field": 1,
        },
    }
    assert serialized == expected


def test_model_serialize_include_none():
    @dataclass
    class Submodel:
        int_field: int
        optional_field: Optional[str]

    @dataclass
    class Model:
        int_field: int
        optional_field: Optional[str]
        submodel_field: Submodel

    m = Model(
        int_field=1,
        optional_field=None,
        submodel_field=Submodel(int_field=1, optional_field=None),
    )

    serialized = serialize(m, exclude_none=False)
    expected = {
        "int_field": 1,
        "optional_field": None,
        "submodel_field": {
            "int_field": 1,
            "optional_field": None,
        },
    }
    assert serialized == expected
