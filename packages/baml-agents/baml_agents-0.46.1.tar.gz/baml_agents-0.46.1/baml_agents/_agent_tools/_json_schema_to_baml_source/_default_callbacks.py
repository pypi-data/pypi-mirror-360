from typing import Any

from baml_agents._agent_tools._utils._snake_to_pascal import snake_to_pascal

from ._interfaces import (
    AliasCallback,
    ArgsClassCallback,
    DescCallback,
    PropNameCallback,
    ToolClassCallback,
    ToolNameCallback,
)


class DefaultArgsClass(ArgsClassCallback):
    """Default callback for generating argument class names."""

    def __call__(
        self,
        *,
        name: str,
        schema: dict[str, Any],  # noqa: ARG002
    ) -> str:
        return f"{snake_to_pascal(name)}Arguments"


class DefaultToolClass(ToolClassCallback):
    """Default callback for generating tool class names."""

    def __call__(
        self,
        *,
        name: str,
        schema: dict[str, Any],  # noqa: ARG002
    ) -> str:
        return f"{snake_to_pascal(name)}Tool"


class DefaultToolName(ToolNameCallback):
    """Default callback for tool name."""

    def __call__(
        self,
        *,
        name: str,
        schema: dict[str, Any],  # noqa: ARG002
    ) -> str:
        return name


class DefaultPropName(PropNameCallback):
    """Default callback for property name."""

    def __call__(
        self,
        *,
        name: str,
        prop_schema: dict[str, Any],  # noqa: ARG002
        class_schema: dict[str, Any],  # noqa: ARG002
        root_class_schema: dict[str, Any],  # noqa: ARG002
    ) -> str:
        return name


class DefaultDesc(DescCallback):
    """Default callback for description."""

    def __call__(
        self,
        *,
        description: str | None,
        root: bool,  # noqa: ARG002
        prop_schema: dict[str, Any],  # noqa: ARG002
        class_schema: dict[str, Any],  # noqa: ARG002
        root_class_schema: dict[str, Any],  # noqa: ARG002
    ) -> str | None:
        return description


class DefaultAlias(AliasCallback):
    """Default callback for alias (returns None by default)."""

    def __call__(
        self,
        *,
        name: str,  # noqa: ARG002
        root: bool,  # noqa: ARG002
        prop_schema: dict[str, Any],  # noqa: ARG002
        class_schema: dict[str, Any],  # noqa: ARG002
        root_class_schema: dict[str, Any],  # noqa: ARG002
    ) -> str | None:
        return None

