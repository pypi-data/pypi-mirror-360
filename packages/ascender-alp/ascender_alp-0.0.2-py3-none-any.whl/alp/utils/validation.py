from typing import Any, TypeVar

from pydantic import PydanticUserError, TypeAdapter

T = TypeVar("T")

def isvalid(type_to_check: type, value: T) -> bool:
    """
    Check if the value is valid for the given type.

    Args:
        type_to_check (type): The type which `value` should be checked against.
        value (T): The value to parse and check.

    Returns:
        bool: _description_
    """
    try:
        type_adapter = TypeAdapter(type_to_check,
                                config={"arbitrary_types_allowed": True})
    except PydanticUserError:
        type_adapter = TypeAdapter(type_to_check)
    
    try:
        type_adapter.validate_python(value)
        return True
    
    except Exception as e:
        return False

def isvalid_json(type_to_check: type, value: T) -> bool:
    """
    Check if the value is valid for the given type.

    Args:
        type_to_check (type): The type which `value` should be checked against.
        value (T): _description_

    Returns:
        bool: _description_
    """
    try:
        type_adapter = TypeAdapter(type_to_check,
                                config={"arbitrary_types_allowed": True})
    except PydanticUserError:
        type_adapter = TypeAdapter(type_to_check)
    
    try:
        type_adapter.validate_json(value)
        return True
    
    except Exception as e:
        return False