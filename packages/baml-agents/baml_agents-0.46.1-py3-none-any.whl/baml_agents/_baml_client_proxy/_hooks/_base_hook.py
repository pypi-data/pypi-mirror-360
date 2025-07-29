from abc import ABC, abstractmethod
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field


class BaseBamlHookContext(BaseModel):
    baml_function_name: str
    baml_function_return_type: type

    # Shared mutable state dictionary for communication between hooks
    shared_state_between_hooks: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @classmethod
    def from_base_context(cls, *, ctx: "BaseBamlHookContext") -> Self:
        return cls(**ctx.model_dump())


class BaseBamlHook:
    def __call__(self) -> Self:
        """
        # If your hook maintains state, consider using a factory class
        # instead of directly instantiating the hook. This approach ensures
        # that each call results in a new, clean hook state.
        """
        return self


class BamlHookFactory(ABC, BaseBamlHook):
    @abstractmethod
    def __call__(self) -> BaseBamlHook:
        """
        If your hook maintains state, consider using a factory class
        instead of directly instantiating the hook. This approach ensures
        that each call results in a new, clean hook state.
        """


class BaseBamlHookSync(BaseBamlHook): ...


class BaseBamlHookAsync(BaseBamlHook): ...
