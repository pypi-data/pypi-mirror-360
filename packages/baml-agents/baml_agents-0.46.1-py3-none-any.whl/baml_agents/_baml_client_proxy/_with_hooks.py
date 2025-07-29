from typing import TYPE_CHECKING, TypeVar

from baml_agents._baml_client_proxy._baml_client_proxy import BamlClientProxy

if TYPE_CHECKING:
    from collections.abc import Sequence

    from baml_agents._baml_client_proxy._hooks._base_hook import BaseBamlHook

T_BamlClient = TypeVar("T_BamlClient")


def with_hooks(
    b: T_BamlClient,
    hooks: "Sequence[BaseBamlHook]",
) -> T_BamlClient:
    """
    Applies lifecycle hooks to a BAML client instance by wrapping it.

    Args:
        b: The original baml_client instance.
        hooks: A list of BamlHook instances.

    Returns:
        A BamlClient wrapper instance that provides the same interface
        as the original client but executes hooks.

    """
    if isinstance(b, BamlClientProxy):
        return b.add_hooks(hooks)
    return BamlClientProxy(b, hooks=hooks)  # type: ignore
