import functools
import inspect
from collections.abc import Callable
from typing import Any


class PassthroughWrapper:
    """
    A wrapper that intercepts attribute access for a given object.
    It distinguishes between regular and async methods and returns
    a corresponding wrapper that simply calls the original method.
    Non-callable attributes are returned directly.
    """

    def __init__(
        self,
        obj: Any,
        /,
        *,
        mutate_args_kwargs: Callable | None = None,
        parent_target=None,
    ):
        # Use a different internal name to avoid potential clashes if wrapping
        # an object that also uses '_ai' or '_obj'.
        object.__setattr__(self, "_passthrough_target", obj)
        self._mutate_args_kwargs = (
            mutate_args_kwargs
            if mutate_args_kwargs is not None
            else lambda args, kwargs, _: (args, kwargs)
        )
        self._parent_target = parent_target

    def __getattribute__(self, name: str) -> Any:
        # 1. Access internal attributes of the wrapper directly.
        # Use object.__getattribute__ to prevent recursion.
        if name == "request":
            parent_target = getattr(self, "_passthrough_target", None)
            return PassthroughWrapper(
                object.__getattribute__(self, "_passthrough_target").request,
                mutate_args_kwargs=self._mutate_args_kwargs,
                parent_target=parent_target,
            )

        if name in {
            "_passthrough_target",
            "_mutate_args_kwargs",
            "_parent_target",
            "_get_baml_function_return_type_name",
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
        if not callable(attr):
            return attr

        mutate_func = object.__getattribute__(self, "_mutate_args_kwargs")

        # 4. If the attribute is callable, determine if it's async or sync.
        if inspect.iscoroutinefunction(attr):

            # Create an ASYNC wrapper
            async def async_wrapper(*args, **kwargs):
                # --- Future extension point (before call) ---
                baml_function_return_type_name = (
                    self._get_baml_function_return_type_name(name)
                )
                mutated_args, mutated_kwargs = mutate_func(
                    args, kwargs.copy(), baml_function_return_type_name
                )
                result = await attr(*mutated_args, **mutated_kwargs)
                # --- Future extension point (after call) ---
                return result

            # Copy metadata
            return functools.wraps(attr)(async_wrapper)

        # Create a SYNC wrapper
        def sync_wrapper(*args, **kwargs):
            # --- Future extension point (before call) ---
            baml_function_return_type_name = self._get_baml_function_return_type_name(
                name
            )
            mutated_args, mutated_kwargs = mutate_func(
                args, kwargs.copy(), baml_function_return_type_name
            )
            result = attr(*mutated_args, **mutated_kwargs)
            # --- Future extension point (after call) ---
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

    def _get_baml_function_return_type_name(self, name):
        baml_client = getattr(self, "_parent_target", None) or self
        return getattr(baml_client, name).__annotations__["return"].__name__

