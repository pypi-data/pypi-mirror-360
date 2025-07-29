from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, List, Literal, Union

from catalystwan.core.models.deserialize import deserialize
from catalystwan.core.types import AliasPath, Variable


def test_simple_deserialize():
    @dataclass
    class Model:
        int_field: int = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "int_field"]),
                "object_type": "object",
            }
        )
        bool_field: bool = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "bool_field"]),
                "object_type": "object",
            }
        )
        str_field: str = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "str_field"]),
                "object_type": "object",
            }
        )
        variable_field: Union[int, Variable] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "variable_field"]),
                "object_type": "object",
            }
        )
        union_field: Union[IPv6Address, IPv4Address] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "union_field"]),
                "object_type": "object",
            }
        )
        template_name: str = field(metadata={"alias": "templateName", "wrap": False})
        template_description: str = field(metadata={"alias": "templateDescription", "wrap": False})
        template_type: str = field(
            default="type",
            init=False,
            metadata={"alias": "templateType", "wrap": False},
        )
        device_type: List[str] = field(
            default_factory=list, metadata={"alias": "deviceType", "wrap": False}
        )
        literal_field: Literal["test", 1] = field(
            default="test",
            metadata={
                "alias": AliasPath(["templateDefinition", "literal_field"]),
                "object_type": "object",
            },
        )

    data = {
        "template_name": "name",
        "template_description": "desc",
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
    assert m.template_name == "name"
    assert m.template_description == "desc"
    assert m.template_type == "type"
    assert m.device_type == []
    assert m.variable_field == r"{{ var }}"
    assert m.union_field == IPv4Address("10.0.0.1")


def test_simple_payload_deserialize():
    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "feature_template"

        int_field: int = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "int_field"]),
                "object_type": "object",
            }
        )
        bool_field: bool = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "bool_field"]),
                "object_type": "object",
            }
        )
        str_field: str = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "str_field"]),
                "object_type": "object",
            }
        )
        variable_field: Union[int, Variable] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "variable_field"]),
                "object_type": "object",
            }
        )
        union_field: Union[IPv6Address, IPv4Address] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "union_field"]),
                "object_type": "object",
            }
        )
        template_name: str = field(metadata={"alias": "templateName", "wrap": False})
        template_description: str = field(metadata={"alias": "templateDescription", "wrap": False})
        template_type: str = field(
            default="type",
            init=False,
            metadata={"alias": "templateType", "wrap": False},
        )
        device_type: List[str] = field(
            default_factory=list, metadata={"alias": "deviceType", "wrap": False}
        )
        literal_field: Literal["test", 1] = field(
            default="test",
            metadata={
                "alias": AliasPath(["templateDefinition", "literal_field"]),
                "object_type": "object",
            },
        )

    data = {
        "templateName": "name",
        "templateDescription": "desc",
        "deviceType": [],
        "templateType": "type",
        "templateDefinition": {
            "int_field": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": 1,
            },
            "bool_field": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": True,
            },
            "str_field": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": "test",
            },
            "literal_field": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": "test",
            },
            "variable_field": {
                "vipObjectType": "object",
                "vipType": "variable",
                "vipValue": r"{{ var }}",
            },
            "union_field": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": "10.0.0.1",
            },
        },
    }
    m = deserialize(Model, **data)

    assert m.int_field == 1
    assert m.bool_field is True
    assert m.str_field == "test"
    assert m.literal_field == "test"
    assert m.template_name == "name"
    assert m.template_description == "desc"
    assert m.template_type == "type"
    assert m.device_type == []
    assert m.variable_field == r"{{ var }}"
    assert m.union_field == IPv4Address("10.0.0.1")


def test_submodel():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "feature_template"

        int_field: int = field(metadata={"object_type": "object"})

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "feature_template"

        submodel_field: Submodel = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "submodel_field"]),
                "object_type": "tree",
            }
        )

        template_name: str = field(metadata={"alias": "templateName", "wrap": False})
        template_description: str = field(metadata={"alias": "templateDescription", "wrap": False})
        template_type: str = field(
            default="type",
            init=False,
            metadata={"alias": "templateType", "wrap": False},
        )
        device_type: List[str] = field(
            default_factory=list, metadata={"alias": "deviceType", "wrap": False}
        )

    data = {
        "template_name": "name",
        "template_description": "desc",
        "submodel_field": {"int_field": 1},
    }

    m = deserialize(Model, **data)

    assert m.template_name == "name"
    assert m.template_description == "desc"
    assert m.template_type == "type"
    assert m.device_type == []
    assert isinstance(m.submodel_field, Submodel) is True
    assert m.submodel_field.int_field == 1


def test_submodel_payload():
    @dataclass
    class Submodel:
        _catalystwan_model_type: ClassVar[str] = "feature_template"

        int_field: int = field(metadata={"object_type": "object"})

    @dataclass
    class Model:
        _catalystwan_model_type: ClassVar[str] = "feature_template"

        submodel_field: Submodel = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "submodel_field"]),
                "object_type": "tree",
            }
        )

        template_name: str = field(metadata={"alias": "templateName", "wrap": False})
        template_description: str = field(metadata={"alias": "templateDescription", "wrap": False})
        template_type: str = field(
            default="type",
            init=False,
            metadata={"alias": "templateType", "wrap": False},
        )
        device_type: List[str] = field(
            default_factory=list, metadata={"alias": "deviceType", "wrap": False}
        )

    data = {
        "templateName": "name",
        "templateDescription": "desc",
        "deviceType": [],
        "templateType": "type",
        "templateDefinition": {
            "submodel_field": {
                "vipObjectType": "tree",
                "vipType": "constant",
                "vipValue": {
                    "int_field": {
                        "vipObjectType": "object",
                        "vipType": "constant",
                        "vipValue": 1,
                    },
                },
            },
        },
    }

    m = deserialize(Model, **data)

    assert m.template_name == "name"
    assert m.template_description == "desc"
    assert m.template_type == "type"
    assert m.device_type == []
    assert isinstance(m.submodel_field, Submodel) is True
    assert m.submodel_field.int_field == 1
