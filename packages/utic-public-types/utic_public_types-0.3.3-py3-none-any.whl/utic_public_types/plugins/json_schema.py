import enum
from datetime import datetime
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Literal, Type, Union, get_args, get_origin

from pydantic import BaseModel, Secret, SecretStr
from pydantic.fields import PydanticUndefined


class SchemaMarker(enum.Enum):
    SECRET = "SECRET"


def _is_pydantic_type(type_: Type) -> bool:
    try:
        return issubclass(type_, BaseModel)
    except TypeError:
        return False


def _is_enum_type(type_: Type) -> bool:
    try:
        return issubclass(type_, enum.Enum)
    except TypeError:
        return False


def get_field_type(annotation) -> str:
    if annotation == str:
        return "string"
    elif annotation in (int, float):
        return "number"
    elif annotation == bool:
        return "boolean"
    elif annotation == type(None):
        return "null"
    else:
        raise NotImplementedError(f"Unsupported field type: {annotation}. Implement it!")


def generate_json_schema_field(annotation, markers: list[SchemaMarker] | None = None) -> dict:
    type_origin = get_origin(annotation)
    type_args = get_args(annotation)

    if annotation == Any:
        return {}
    if _is_pydantic_type(annotation):
        return generate_json_schema(annotation, markers=markers)
    elif type_origin == list:
        field_def = {"type": "array"}
        if len(type_args) == 1:
            field_def["items"] = generate_json_schema_field(type_args[0], markers=markers)
        return field_def
    elif type_origin == dict:
        return {
            "type": "object",
            "properties": generate_json_schema_field(type_args[1], markers=markers),
        }
    elif annotation == dict:
        return {"type": "object"}
    elif type_origin == Secret:
        return generate_json_schema_field(type_args[0], markers=[SchemaMarker.SECRET])
    elif annotation == SecretStr:
        return {"type": "string", "writeOnly": True, "format": "password"}
    elif type_origin == Literal:
        return {"type": "string", "enum": list(type_args)}
    elif _is_enum_type(annotation):
        return {"type": "string", "enum": [e.value for e in annotation]}
    elif annotation == Path:
        return {"type": "string", "format": "path"}
    elif type_origin == Annotated:
        return generate_json_schema_field(type_args[0], markers=markers)
    elif annotation == datetime:
        return {"type": "string", "format": "date-time"}
    elif type_origin in (UnionType, Union):
        if len(type_args) == 2 and type_args[1] == type(None):
            # special case here where it's a nullable field
            field_def = generate_json_schema_field(type_args[0], markers=markers)
            field_def["type"] = [field_def["type"], "null"]
            return field_def
        else:
            return {"anyOf": [generate_json_schema_field(arg) for arg in type_args]}
    else:
        return {"type": get_field_type(annotation)}


def generate_json_schema(model: Type[BaseModel], markers: list[SchemaMarker] | None = None) -> dict:
    """
    We opt for our own json schema rendering because the default
    pydantic one is not very flexible and doesn't support secret
    fields in a unified way with nesting
    """
    markers = markers or []

    output = {
        "type": "object",
        "properties": {},
    }

    required = []
    for field_name, field in model.model_fields.items():
        field_output = generate_json_schema_field(field.annotation)
        if field.title:
            field_output["title"] = field.title
        if field.description:
            field_output["description"] = field.description

        if field.is_required():
            required.append(field_name)

        if SchemaMarker.SECRET in markers:
            field_output["writeOnly"] = True
            field_output["format"] = "password"

        if field.default != PydanticUndefined:
            default_value = field.default
            if isinstance(default_value, BaseModel):
                default_value = default_value.model_dump()
            field_output["default"] = default_value

        output["properties"][field_name] = field_output

    output["required"] = required
    return output
