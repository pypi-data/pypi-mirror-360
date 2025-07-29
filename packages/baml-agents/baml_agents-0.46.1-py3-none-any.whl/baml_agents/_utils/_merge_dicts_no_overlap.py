from typing import Any


def merge_dicts_no_overlap(
    a: dict[Any, Any], b: dict[Any, Any], error_message: str | None = None
) -> dict[Any, Any]:
    """Merge two dicts, error on key collisions."""
    overlap = set(a) & set(b)
    if overlap:
        error_message = "Collision on keys"
        raise KeyError(f"{error_message}: {overlap}")
    return {**a, **b}
