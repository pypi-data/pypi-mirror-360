from collections.abc import Iterable


def sole(collection: Iterable):
    """
    Return the sole (one and only) element from the collection.

    Args:
        collection: An iterable with exactly one element

    Returns:
        The single element

    Raises:
        ValueError: If collection doesn't contain exactly one element

    """
    iterator = iter(collection)
    try:
        first_item = next(iterator)
    except StopIteration as e:
        raise ValueError("Expected exactly one element, found 0") from e
    try:
        next(iterator)
        raise ValueError("Expected exactly one element, found more than 1")
    except StopIteration:
        return first_item
