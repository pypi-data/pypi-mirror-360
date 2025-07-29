from typing import Any, TypeVar

from pydantic import PydanticUserError, TypeAdapter

T = TypeVar("T")

def parse(type_to_check: type[T], value: Any) -> T:
    """
    Parse the value and check if it is valid for the given type.
    """
    try:
        type_adapter = TypeAdapter(type_to_check,
                                config={"arbitrary_types_allowed": True})
    except PydanticUserError:
        type_adapter = TypeAdapter(type_to_check)
    
    return type_adapter.validate_python(value)

def parse_json(type_to_check: type[T], value: str) -> T:
    """
    Parse the value (in json format) and check if it is valid for the given type.
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