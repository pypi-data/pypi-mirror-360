from typing import Any

from baml_py import ClientRegistry, Collector
from baml_py.type_builder import TypeBuilder

from baml_agents._baml_client_proxy._hooks._on_before_call_hook import (
    OnBeforeCallHookSync,
)


class WithOptions(OnBeforeCallHookSync):
    def __init__(
        self,
        *,
        type_builder: TypeBuilder | None = None,
        collector: Collector | None = None,
        client_registry: ClientRegistry | None = None,
    ) -> None:
        super().__init__()
        self._client_registry = client_registry
        self._type_builder = type_builder
        self._collector = collector

    def on_before_call(self, *, params: dict[str, Any], **_) -> None:
        for key, value in {
            "client_registry": self._client_registry,
            "type_builder": self._type_builder,
            "collector": self._collector,
        }.items():
            params["baml_options"][key] = value
