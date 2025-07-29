from collections.abc import Sequence
from typing import Any

from baml_agents._baml_client_proxy._hooks._base_hook import (
    BaseBamlHook,
    BaseBamlHookAsync,
    BaseBamlHookContext,
)
from baml_agents._baml_client_proxy._hooks._implementations._with_options import (
    WithOptions,
)
from baml_agents._baml_client_proxy._hooks._on_after_call_success_hook import (
    OnAfterCallSuccessHookAsync,
    OnAfterCallSuccessHookContext,
    OnAfterCallSuccessHookSync,
)
from baml_agents._baml_client_proxy._hooks._on_before_call_hook import (
    OnBeforeCallHookAsync,
    OnBeforeCallHookContext,
    OnBeforeCallHookSync,
)
from baml_agents._baml_client_proxy._hooks._types import Mutable


class BaseHookEngine:
    def __init__(
        self,
        *,
        hooks: Sequence["BaseBamlHook"],
        baml_function_name: str,
        baml_function_params: dict,
    ):
        self._hooks: list[BaseBamlHook] = [hook() for hook in hooks]

        # Move WithOptions to the start of the list
        # Because otherwise it might overwrite baml options set by other hooks
        # leading to silent bugs and unexpected behavior
        self._hooks.sort(key=lambda hook: not isinstance(hook, WithOptions))

        self._ctx = BaseBamlHookContext(
            baml_function_name=baml_function_name,
            baml_function_return_type=str,
        )
        self._mutable_params: dict[str, Any] = baml_function_params

    @property
    def params(self) -> dict[str, Any]:
        return self._mutable_params


class HookEngineSync(BaseHookEngine):
    def __init__(
        self,
        *,
        hooks: Sequence["BaseBamlHook"],
        baml_function_name: str,
        baml_function_params: dict,
    ):
        for hook in hooks:
            if isinstance(hook, BaseBamlHookAsync):
                raise TypeError(
                    f"Async hook ({type(hook).__name__}) provided in a sync context "
                    f"for function '{baml_function_name}'"
                )
        super().__init__(
            hooks=hooks,
            baml_function_name=baml_function_name,
            baml_function_params=baml_function_params,
        )

    def on_before_call(self) -> None:
        for hook in self._hooks:
            if isinstance(hook, OnBeforeCallHookSync):
                ctx = OnBeforeCallHookContext.from_base_context(ctx=self._ctx)
                hook.on_before_call(ctx=ctx, params=self.params)

    def on_after_call_success(self, result: Mutable) -> None:
        for hook in self._hooks:
            if isinstance(hook, OnAfterCallSuccessHookSync):
                ctx = OnAfterCallSuccessHookContext.from_base_context(
                    ctx=self._ctx, params=self.params
                )
                hook.on_after_call_success(ctx=ctx, result=result)


class HookEngineAsync(BaseHookEngine):
    async def on_before_call(self) -> None:
        for hook in self._hooks:
            if isinstance(hook, OnBeforeCallHookSync):
                ctx = OnBeforeCallHookContext.from_base_context(ctx=self._ctx)
                hook.on_before_call(ctx=ctx, params=self.params)
            if isinstance(hook, OnBeforeCallHookAsync):
                ctx = OnBeforeCallHookContext.from_base_context(ctx=self._ctx)
                await hook.on_before_call(ctx=ctx, params=self.params)

    async def on_after_call_success(self, result: Mutable) -> None:
        for hook in self._hooks:
            if isinstance(hook, OnAfterCallSuccessHookSync):
                ctx = OnAfterCallSuccessHookContext.from_base_context(
                    ctx=self._ctx, params=self.params
                )
                hook.on_after_call_success(ctx=ctx, result=result)
            if isinstance(hook, OnAfterCallSuccessHookAsync):
                ctx = OnAfterCallSuccessHookContext.from_base_context(
                    ctx=self._ctx, params=self.params
                )
                await hook.on_after_call_success(ctx=ctx, result=result)
