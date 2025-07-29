from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Literal, Optional, Union
from uuid import UUID

import pytest
from catalystwan.core.models.deserialize import deserialize
from catalystwan.core.types import Variable


def test_simple_deserialize():
    @dataclass
    class Model:
        int_field: int
        bool_field: bool
        str_field: str
        literal_field: Literal["test", 1]

    data = {
        "int_field": 1,
        "bool_field": True,
        "str_field": "test",
        "literal_field": "test",
    }
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.bool_field is True
    assert m.str_field == "test"
    assert m.literal_field == "test"


def test_simple_cast():
    @dataclass
    class Model:
        int_field: int
        str_field: str
        literal_field: Literal["test", 1]

    data = {"int_field": "1", "str_field": 1, "literal_field": "1"}
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.str_field == "1"
    assert m.literal_field == 1


def test_optional():
    @dataclass
    class Model:
        int_field: Optional[int]
        str_field: Optional[str]
        bool_field: Optional[bool] = None

    data = {
        "int_field": "1",
        "str_field": None,
    }
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.str_field is None
    assert m.bool_field is None


def test_list():
    @dataclass
    class Model:
        list_field: List[int]

    data = {
        "list_field": [1, "2"],
    }
    m = deserialize(Model, **data)

    assert m.list_field == [1, 2]


def test_union():
    @dataclass
    class Model:
        union_field: Union[IPv6Address, IPv4Address]

    data = {"union_field": "10.0.0.1"}
    m = deserialize(Model, **data)

    assert m.union_field == IPv4Address("10.0.0.1")


def test_submodel():
    @dataclass
    class Submodel:
        int_field: int

    @dataclass
    class Model:
        submodel_field: Submodel

    data = {"submodel_field": {"int_field": 1}}

    m = deserialize(Model, **data)

    assert isinstance(m.submodel_field, Submodel) is True
    assert m.submodel_field.int_field == 1


def test_direct_init():
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

    m = Model(
        int_field=1,
        bool_field=True,
        str_field="test",
        literal_field="test",
        union_field=IPv4Address("10.0.0.1"),
        submodel_field=Submodel(int_field=1),
    )

    assert m.int_field == 1
    assert m.bool_field is True
    assert m.str_field == "test"
    assert m.literal_field == "test"
    assert m.union_field == IPv4Address("10.0.0.1")
    assert m.submodel_field.int_field == 1
    assert isinstance(m.submodel_field, Submodel)


@pytest.mark.parametrize(
    "value",
    [
        ("1"),
        (1),
        (1.2),
        ("True"),
        ("3a56601d-6132-4aea-98d0-605fa966ad48"),
        (UUID("3a56601d-6132-4aea-98d0-605fa966ad48")),
    ],
)
def test_union_match_identity(value):
    @dataclass
    class Model:
        union_field: Union[str, int, bool, float, UUID]

    m = deserialize(Model, union_field=value)
    assert m.union_field == value


def test_union_match_optional():
    @dataclass
    class Model:
        union_field: Optional[Union[str, int, bool, float, UUID]] = None

    m1 = deserialize(Model)
    m2 = deserialize(Model, union_field=None)
    m3 = deserialize(Model, union_field=[])

    assert m1.union_field is None
    assert m2.union_field is None
    assert m3.union_field is None


@pytest.mark.parametrize(
    "value",
    [
        ("1"),
        (1),
        ("True"),
        ("3a56601d-6132-4aea-98d0-605fa966ad48"),
        (UUID("3a56601d-6132-4aea-98d0-605fa966ad48")),
        ([1, "2", 3]),
        ([1.2, True, 1.3]),
    ],
)
def test_union_match_nested_identity(value):
    @dataclass
    class Model:
        union_field: Union[
            str, int, Union[UUID, Union[List[Union[str, int]], List[Union[float, bool]]]]
        ]

    m = deserialize(Model, union_field=value)

    assert m.union_field == value


def test_union_match_models():
    @dataclass
    class Submodel1:
        f1: int

    @dataclass
    class Submodel2:
        f1: int
        f2: int

    @dataclass
    class Model:
        union_field: Union[str, Submodel1, Submodel2]

    m1 = deserialize(Model, **{"union_field": {"f1": 1}})
    m2 = deserialize(Model, **{"union_field": {"f1": 1, "f2": 2}})
    m3 = deserialize(Model, **{"union_field": {"f1": 1, "f2": 2, "irrelevant_key": 0}})

    assert m1.union_field == Submodel1(1)
    assert m2.union_field == Submodel2(1, 2)
    assert m3.union_field == Submodel2(1, 2)


@pytest.mark.parametrize(
    "model_input,expected_value",
    [
        ("1", 1),
        ("3a56601d-6132-4aea-98d0-605fa966ad48", UUID("3a56601d-6132-4aea-98d0-605fa966ad48")),
        ("some_string", "{{some_string}}"),
    ],
)
def test_match_union_cast(model_input, expected_value):
    @dataclass
    class Model:
        union_field: Optional[Union[int, bool, UUID, Variable]]

    m = deserialize(Model, union_field=model_input)

    assert m.union_field == expected_value
