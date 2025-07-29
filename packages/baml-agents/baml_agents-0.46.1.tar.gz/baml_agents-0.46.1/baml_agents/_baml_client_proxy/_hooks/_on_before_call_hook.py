from abc import ABC, abstractmethod
from typing import Any, final

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHookAsync,
    BaseBamlHookContext,
    BaseBamlHookSync,
)


@final
class OnBeforeCallHookContext(BaseBamlHookContext):
    pass


class OnBeforeCallHookAsync(BaseBamlHookAsync, ABC):
    @abstractmethod
    async def on_before_call(
        self,
        *,
        ctx: OnBeforeCallHookContext,
        params: dict[str, Any],
    ) -> None:
        pass


class OnBeforeCallHookSync(BaseBamlHookSync, ABC):
    @abstractmethod
    def on_before_call(
        self,
        *,
        ctx: OnBeforeCallHookContext,
        params: dict[str, Any],
    ) -> None:
        pass
