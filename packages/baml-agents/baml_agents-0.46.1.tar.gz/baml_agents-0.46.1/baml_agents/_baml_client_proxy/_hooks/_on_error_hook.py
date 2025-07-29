from abc import ABC, abstractmethod
from typing import final

from baml_agents._baml_client_proxy._hooks._base_hook import BaseBamlHookContext


@final
class OnErrorHookContext(BaseBamlHookContext):
    error: Exception


class OnErrorHookAsync(ABC):
    @abstractmethod
    async def on_error(self, *, ctx: OnErrorHookContext) -> None:
        pass


class OnErrorHookSync(ABC):
    @abstractmethod
    def on_error(self, *, ctx: OnErrorHookContext) -> None:
        pass
