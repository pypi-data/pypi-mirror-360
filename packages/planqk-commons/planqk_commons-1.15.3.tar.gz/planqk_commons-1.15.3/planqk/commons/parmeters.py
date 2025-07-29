import json
from inspect import Signature, Parameter
from typing import Any, Dict, get_origin, get_args, Union, Optional

from pydantic import BaseModel


def files_to_parameters(input_files: Dict[str, str], signature: Signature) -> Dict[str, Any]:
    """
    Maps input files to parameters of a function signature. If a parameter is not found in the input files, the default
    value of the parameter is used. If the parameter is optional and has no default value, it is set to None.

    :param input_files: The input files to be mapped to the parameters. The keys are the parameter names. The values are the file paths.
    :param signature: The signature of the function to which the input files should be mapped.
    :return: A dictionary containing the parameters of the function with the input files mapped to them.
    """
    parameters = {}

    for parameter in signature.parameters.values():
        parameter_name = parameter.name

        if parameter_name not in input_files:
            try:
                parameters[parameter_name] = map_default(parameter)
            except TypeError:
                pass
            continue

        parameters[parameter_name] = map_input_file(input_files[parameter_name], parameter)

    return parameters


def map_input_file(input_file: str, parameter: Parameter) -> Any:
    """
    Maps an input file to a parameter of a function signature.

    :param input_file: The path to the input file.
    :param parameter: The parameter to which the input file should be mapped.
    :return: The value of the input file as the type of the parameter.
    """
    parameter_type = parameter.annotation

    origin = get_origin(parameter_type)
    if origin:
        parameter_type = origin

    with open(input_file, "r") as file:
        file_content = file.read()

    return str_to_parameter_type(file_content, parameter_type)


def map_default(parameter: Parameter) -> Any:
    """
    Maps the default value of a parameter to the parameter type.

    :param parameter: The parameter for which the default value should be mapped.
    :return: The default value of the parameter.
    """
    parameter_type = parameter.annotation

    # use default value if available
    if parameter.default != parameter.empty:
        return parameter.default

    # if optional w/o default, set to None
    elif is_optional_type(parameter_type):
        return None

    # if it is a Pydantic model, try to create an empty instance (using defaults if available)
    elif issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json("{}")

    raise TypeError(f"Could not find a default value for parameter '{parameter.name}' of type '{parameter_type}'")


def str_to_parameter_type(data: str, parameter_type: Any) -> Any:
    """
    Converts a string to a parameter type.

    :param data: The string to be converted.
    :param parameter_type: The type to which the string should be converted.
    :return: The value of the string as the type of the parameter.
    """
    if issubclass(parameter_type, str):
        return data

    if issubclass(parameter_type, bool):
        return bool(data)

    if issubclass(parameter_type, int):
        return int(data)

    if issubclass(parameter_type, float):
        return float(data)

    if issubclass(parameter_type, (list, dict)):
        return json.loads(data)

    if issubclass(parameter_type, BaseModel):
        return parameter_type.model_validate_json(data)

    raise ValueError(f"Type {parameter_type} is not supported")


def is_simple_type(value: Any) -> bool:
    """
    Checks if the value is a simple type (str, int, float, bool).
    """
    return isinstance(value, (str, int, float, bool))


def is_container_type(value: Any) -> bool:
    """
    Checks if the value is a container type (list, tuple, Union, Optional).
    """
    return value is list or value is tuple or value is Union or value is Optional


def is_optional_type(value: Any) -> bool:
    """
    Checks if the value is an optional type (Union with None or Optional).
    """
    origin = get_origin(value)
    if origin is Union:
        args = get_args(value)
        return len(args) == 2 and type(None) in args
    return origin is Optional
