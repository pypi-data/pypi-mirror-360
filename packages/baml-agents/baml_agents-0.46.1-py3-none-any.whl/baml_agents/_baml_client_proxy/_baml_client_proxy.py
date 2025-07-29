import functools
import inspect
from collections.abc import Callable, Sequence
from typing import Any, Generic, Self, TypeVar

from baml_agents._baml_client_proxy._hook_engine import HookEngineAsync, HookEngineSync
from baml_agents._baml_client_proxy._hooks._base_hook import BaseBamlHook
from baml_agents._baml_client_proxy._hooks._types import Mutable
from baml_agents._utils._merge_dicts_no_overlap import merge_dicts_no_overlap
from baml_agents._utils._sole import sole

T_BamlClient = TypeVar("T_BamlClient")


class BamlClientProxy(Generic[T_BamlClient]):
    """
    A wrapper that intercepts attribute access for a given object.
    It distinguishes between regular and async methods and returns
    a corresponding wrapper that simply calls the original method.
    Non-callable attributes are returned directly.
    """

    def __init__(
        self,
        b: T_BamlClient,
        /,
        *,
        hooks: Sequence[BaseBamlHook] | None = None,
        root_target: T_BamlClient | None = None,
    ):
        object.__setattr__(self, "_passthrough_target", b)
        object.__setattr__(self, "_hooks", hooks)
        object.__setattr__(self, "_root_target", root_target or b)

    def add_hooks(self, hooks: Sequence[BaseBamlHook]) -> Self:
        current_hooks = object.__getattribute__(self, "_hooks")
        if current_hooks is None:
            object.__setattr__(self, "_hooks", hooks)
        else:
            object.__setattr__(self, "_hooks", current_hooks + hooks)
        return self

    def __getattribute__(self, name: str) -> Any:
        # 1. Access internal attributes of the wrapper directly.
        # Use object.__getattribute__ to prevent recursion.
        if name == "request":
            return BamlClientProxy(
                object.__getattribute__(self, "_passthrough_target").request,
                hooks=object.__getattribute__(self, "_hooks"),
                root_target=object.__getattribute__(self, "_passthrough_target"),
            )

        if name in {
            "parse_stream",
            "request",
            "stream",
            "stream_request",
            "with_options",
            "add_hooks",
            "__class__",
            "__init__",
            "__getattribute__",
            "__setattr__",
            "__delattr__",
            "__dict__",
            "__dir__",
            "__repr__",
            "__str__",
            # Async/Awaitable checks often look for these
            "__await__",
            "__aiter__",
            "__anext__",
            "__aenter__",
            "__aexit__",
        }:
            try:
                # Get attributes of the wrapper itself first
                return object.__getattribute__(self, name)
            except AttributeError:
                # If the wrapper doesn't have it (e.g., __await__),
                # fall through to get it from the target below.
                pass

        # 2. Get the target object and the requested attribute from it.
        target = object.__getattribute__(self, "_passthrough_target")
        try:
            attr = getattr(target, name)
        except AttributeError:
            # If the target doesn't have the attribute, raise AttributeError naturally.
            # Re-raise the specific error from getattr.
            raise AttributeError(
                f"'{type(target).__name__}' object has no attribute '{name}'"
            ) from None

        # 3. If the attribute is not callable, return it directly.
        if name == "with_options" or not callable(attr):
            return attr

        # 4. If the attribute is callable, determine if it's async or sync.
        if inspect.iscoroutinefunction(attr):
            # Create an ASYNC wrapper
            async def async_wrapper(*args, **kwargs):
                params: dict[str, Any] = object.__getattribute__(
                    self, "_get_baml_function_params"
                )(attr, args, kwargs)
                hook_engine = (
                    HookEngineAsync(
                        hooks=hooks,
                        baml_function_name=name,
                        baml_function_params=params,
                    )
                    if (hooks := object.__getattribute__(self, "_hooks"))
                    else None
                )

                if hook_engine:
                    await hook_engine.on_before_call()

                    result = await attr(**hook_engine.params)

                    await hook_engine.on_after_call_success(Mutable(value=result))
                else:
                    result = await attr(*args, **kwargs)

                return result

            # Copy metadata
            return functools.wraps(attr)(async_wrapper)

        # Create a SYNC wrapper
        def sync_wrapper(*args, **kwargs):
            params: dict[str, Any] = object.__getattribute__(
                self, "_get_baml_function_params"
            )(attr, args, kwargs)
            hook_engine = (
                HookEngineSync(
                    hooks=hooks,
                    baml_function_name=name,
                    baml_function_params=params,
                )
                if (hooks := object.__getattribute__(self, "_hooks"))
                else None
            )

            if hook_engine:
                hook_engine.on_before_call()

                result = attr(**hook_engine.params)

                mutable_result = Mutable(value=result)
                hook_engine.on_after_call_success(mutable_result)
                result = mutable_result.value
            else:
                result = attr(*args, **kwargs)

            return result

        # Copy metadata
        return functools.wraps(attr)(sync_wrapper)

    # Optional: Proxy __dir__ to make introspection work better
    def __dir__(self):
        target = object.__getattribute__(self, "_passthrough_target")
        # Combine wrapper's dir and target's dir
        return sorted(set(object.__dir__(self)) | set(dir(target)))

    # Optional: Custom repr
    def __repr__(self):
        target = object.__getattribute__(self, "_passthrough_target")
        return f"<_PassthroughWrapper wrapping {target!r}>"

    def _get_baml_function_return_type_name(self, baml_function_name) -> str:
        baml_client = object.__getattribute__(self, "_root_target")
        return (
            getattr(baml_client, baml_function_name).__annotations__["return"].__name__
        )

    def _get_baml_function_params(
        self,
        baml_function: Callable,
        baml_function_args: tuple,
        baml_function_kwargs: dict,
    ) -> dict[str, Any]:
        signature = inspect.signature(baml_function)
        bound = signature.bind(*baml_function_args, **baml_function_kwargs)
        bound.apply_defaults()

        default_baml_options = sole(
            getattr(object.__getattribute__(self, "_root_target"), attr)
            for attr in dir(object.__getattribute__(self, "_root_target"))
            if attr.endswith("__baml_options")
        )
        baml_options = merge_dicts_no_overlap(
            default_baml_options,
            bound.arguments.get("baml_options", {}),
            error_message="Overwriting baml options may lead to silently breaking behaviors from other hooks",
        )

        return {
            **bound.arguments,
            "baml_options": baml_options,
        }

    def with_options(self, *__, **_):
        raise AttributeError(
            "Use instead: b = with_hooks(b, [WithOptions(client_registry=..., type_builder=..., collector=...)])"
        )

    @property
    def parse_stream(self) -> Any:
        raise NotImplementedError("parse_stream is not implemented in BamlClientProxy")

    @property
    def request(self) -> Any:
        raise NotImplementedError("request is not implemented in BamlClientProxy")

    @property
    def stream(self) -> Any:
        raise NotImplementedError("stream is not implemented in BamlClientProxy")

    @property
    def stream_request(self) -> Any:
        raise NotImplementedError(
            "stream_request is not implemented in BamlClientProxy"
        )
