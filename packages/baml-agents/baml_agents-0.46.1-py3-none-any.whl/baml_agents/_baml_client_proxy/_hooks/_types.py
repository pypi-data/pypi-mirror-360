from dataclasses import dataclass
from typing import Any


@dataclass
class Mutable:
    """
    A wrapper for a value that can be mutated across multiple hooks.
    This allows hooks to modify the value in place, ensuring changes
    are propagated to subsequent hooks.
    """

    value: Any
