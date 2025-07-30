from typing import Any, Optional, Type, TypeVar, cast, get_args

L = TypeVar('L', bound=Any)

def map_to_literal(value: str, literal_type: Type[L], default: Optional[L] = None) -> L:
    """
    Maps a string to a value of the specified Literal type.

    Args:
        value: The string value to map
        literal_type: The Literal type to map to
        default: Default value to return if mapping fails (must be a valid value of the Literal type)

    Returns:
        A value of the specified Literal type
    """
    normalized_value = value.strip().upper()
    allowed_values = get_args(literal_type)

    # Check if normalized value is in allowed values
    if normalized_value in allowed_values:
        return cast(L, normalized_value)

    # Return default if provided and valid
    if default is not None and default in allowed_values:
        return default
    raise ValueError(f"Value '{value}' is not a valid value for {literal_type}. Allowed values are: {allowed_values}.")
