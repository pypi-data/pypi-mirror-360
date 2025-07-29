from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Self, final

from frozendict import frozendict

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHookAsync,
    BaseBamlHookContext,
    BaseBamlHookSync,
)
from baml_agents._baml_client_proxy._hooks._types import Mutable


@final
class OnAfterCallSuccessHookContext(BaseBamlHookContext):
    params: frozendict[str, Any]

    @classmethod
    def from_base_context(
        cls, *, ctx: "BaseBamlHookContext", params: Mapping[str, Any]
    ) -> Self:
        return cls(**ctx.model_dump(), params=frozendict(params))


class OnAfterCallSuccessHookAsync(BaseBamlHookAsync, ABC):
    @abstractmethod
    async def on_after_call_success(
        self,
        *,
        ctx: OnAfterCallSuccessHookContext,
        result: Mutable,
    ) -> None:
        pass


class OnAfterCallSuccessHookSync(BaseBamlHookSync, ABC):
    @abstractmethod
    def on_after_call_success(
        self,
        *,
        ctx: OnAfterCallSuccessHookContext,
        result: Mutable,
    ) -> None:
        pass
