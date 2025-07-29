from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, final

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHookAsync,
    BaseBamlHookContext,
    BaseBamlHookSync,
)

PartialCallback = Callable[[Any], Awaitable[None]] | None


@final
class HandleLlmInteractionHookContext(BaseBamlHookContext):
    pass


class HandleLlmInteractionHookAsync(BaseBamlHookAsync, ABC):
    @abstractmethod
    async def handle_llm_interaction(
        self,
        context: HandleLlmInteractionHookContext,
    ) -> Any: ...


class HandleLlmInteractionHookSync(BaseBamlHookSync, ABC):
    @abstractmethod
    def handle_llm_interaction(
        self,
        context: HandleLlmInteractionHookContext,
    ) -> Any: ...
