from typing import TypeVar

# Define a TypeVar. T can be any type.
T = TypeVar("T")


def must(value: T | None, message: str = "Value must not be None") -> T:
    """
    Asserts that the value is not None and returns it.
    Raises a ValueError if the value is None.

    This function is useful for type narrowing where a variable might be
    Optional[T] but, at a certain point in the logic, it's known (or asserted)
    to be T.

    Args:
        value: The value to check, typed as Optional[T] (i.e., T | None).
        message: Optional custom error message if the value is None.

    Returns:
        The value itself, now confirmed to be of type T (not None).

    Raises:
        ValueError: If the input value is None.

    """
    if value is None:
        raise ValueError(message)
    return value
