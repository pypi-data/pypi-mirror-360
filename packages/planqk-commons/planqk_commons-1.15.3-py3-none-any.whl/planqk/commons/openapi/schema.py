from inspect import Signature
from typing import Any, Dict, Tuple, get_origin, get_args

from pydantic import BaseModel

from planqk.commons.parmeters import is_container_type


def generate_parameter_schema(signature: Signature) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    parameter_schemas = {}
    schema_definitions = {}

    # generate schema for each parameter
    parameters = signature.parameters
    for parameter in parameters.values():
        parameter_type = parameter.annotation
        args = get_args(parameter_type)
        origin = get_origin(parameter_type)
        if origin:
            parameter_type = origin

        if len(args) > 0 and is_container_type(origin):
            # nested native lists are not supported
            # it only considers the first type of the given tuple definition
            item_type = args[0]
            if issubclass(item_type, BaseModel):
                schema, schema_definition = generate_pydantic_schema(item_type)
                parameter_schemas[parameter.name] = {"type": "array", "items": schema}
                if schema_definition is not None:
                    schema_definitions.update(schema_definition)
            else:
                parameter_schemas[parameter.name] = {"type": "array"}
        elif issubclass(parameter_type, BaseModel):
            schema, schema_definition = generate_pydantic_schema(parameter_type)
            parameter_schemas[parameter.name] = schema
            if schema_definition is not None:
                schema_definitions.update(schema_definition)
        elif issubclass(parameter_type, list) or issubclass(parameter_type, tuple):
            parameter_schemas[parameter.name] = {"type": "array"}
        elif issubclass(parameter_type, str):
            parameter_schemas[parameter.name] = {"type": "string"}
        # bool needs to be checked before int as otherwise it would be classified as int
        elif issubclass(parameter_type, bool):
            parameter_schemas[parameter.name] = {"type": "boolean"}
        elif issubclass(parameter_type, int):
            parameter_schemas[parameter.name] = {"type": "integer"}
        elif issubclass(parameter_type, float):
            parameter_schemas[parameter.name] = {"type": "number"}
        else:
            # for the rest we assume dict
            parameter_schemas[parameter.name] = {"type": "object", "additionalProperties": {"type": "string"}}

    return parameter_schemas, schema_definitions


def generate_return_schema(signature: Signature) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    return_schema = {}
    schema_definitions = {}

    # generate schema for the return type
    return_type = signature.return_annotation

    if return_type is None:
        return return_schema, schema_definitions

    args = get_args(return_type)
    origin = get_origin(return_type)
    if origin:
        return_type = origin

    if len(args) > 0 and is_container_type(origin):
        # nested native lists are not supported
        # it only considers the first type of the given tuple definition
        return_type = args[0]

    if issubclass(return_type, BaseModel):
        schema, schema_definition = generate_pydantic_schema(return_type)
        return_schema = schema
        if schema_definition is not None:
            schema_definitions.update(schema_definition)

    return return_schema, schema_definitions


def generate_pydantic_schema(parameter_type) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not issubclass(parameter_type, BaseModel):
        raise ValueError("Only Pydantic models are supported")

    schema_definition = None
    schema = parameter_type.model_json_schema(
        ref_template="#/components/schemas/{model}",
        mode="serialization"
    )

    if "$defs" in schema:
        schema_definition = schema.pop("$defs")

    return schema, schema_definition
