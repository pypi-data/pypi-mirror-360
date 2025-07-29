from abc import ABC, abstractmethod
from typing import Any, final

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHookAsync,
    BaseBamlHookContext,
    BaseBamlHookSync,
)


@final
class OnPartialResponseParsedHookContext(BaseBamlHookContext):
    partial_result: Any


class OnPartialResponseParsedHookAsync(BaseBamlHookAsync, ABC):
    @abstractmethod
    async def on_partial_response_parsed(
        self,
        *,
        ctx: OnPartialResponseParsedHookContext,
    ) -> None:
        pass


class OnPartialResponseParsedHookSync(BaseBamlHookSync, ABC):
    @abstractmethod
    def on_partial_response_parsed(
        self,
        *,
        ctx: OnPartialResponseParsedHookContext,
    ) -> None:
        pass
