from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import ClassVar, List, Literal, Optional, Union

from catalystwan.core.models.serialize import serialize
from catalystwan.core.types import AliasPath, Variable


def test_model_serialize_json():
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

    m = Model(
        template_name="name",
        template_description="desc",
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
    assert serialized == expected


def test_model_serialize():
    @dataclass
    class Submodel:
        int_field: int = field(metadata={"object_type": "object"})

    @dataclass
    class Model:
        submodel_field: Submodel = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "submodel_field"]),
                "object_type": "tree",
            }
        )
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

    m = Model(
        template_name="name",
        template_description="desc",
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
        "template_name": "name",
        "template_description": "desc",
        "device_type": [],
        "template_type": "type",
    }
    assert serialized == expected


def test_model_serialize_exclude_none():
    @dataclass
    class Submodel:
        int_field: int = field(metadata={"object_type": "object"})
        optional_field: Optional[str] = field(metadata={"object_type": "object"})

    @dataclass
    class Model:
        submodel_field: Submodel = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "submodel_field"]),
                "object_type": "tree",
            }
        )
        int_field: int = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "int_field"]),
                "object_type": "object",
            }
        )
        optional_field: Optional[str] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "optional_field"]),
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

    m = Model(
        template_name="name",
        template_description="desc",
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
        "template_name": "name",
        "template_description": "desc",
        "device_type": [],
        "template_type": "type",
    }
    assert serialized == expected


def test_model_serialize_not_exclude_none():
    @dataclass
    class Submodel:
        int_field: int = field(metadata={"object_type": "object"})
        optional_field: Optional[str] = field(metadata={"object_type": "object"})

    @dataclass
    class Model:
        submodel_field: Submodel = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "submodel_field"]),
                "object_type": "tree",
            }
        )
        int_field: int = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "int_field"]),
                "object_type": "object",
            }
        )
        optional_field: Optional[str] = field(
            metadata={
                "alias": AliasPath(["templateDefinition", "optional_field"]),
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

    m = Model(
        template_name="name",
        template_description="desc",
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
        "template_name": "name",
        "template_description": "desc",
        "device_type": [],
        "template_type": "type",
    }
    assert serialized == expected
