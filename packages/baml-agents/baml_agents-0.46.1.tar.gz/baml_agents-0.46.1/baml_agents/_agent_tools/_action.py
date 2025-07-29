import inspect
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Self

from loguru import logger
from pydantic import BaseModel

from baml_agents._agent_tools._str_result import Result
from baml_agents._agent_tools._utils._snake_to_pascal import pascal_to_snake

from ._tool_definition import McpToolDefinition


class Action(BaseModel, ABC):
    """
    Abstract base class for creating local MCP-compatible tools using Pydantic.

    Subclasses define Pydantic fields for arguments and implement `__call__`.
    Class attributes `_mcp_tool_name` and `_mcp_annotations` provide overrides.
    `get_mcp_definition` returns an MCPToolDefinition instance.
    """

    _alias: ClassVar[str | None] = None
    _mcp_annotations: ClassVar[dict[str, Any] | None] = None

    @classmethod
    def get_action_id(cls) -> str:
        """
        Returns the canonical name of the action, using the alias if set, otherwise the class name,
        always in snake_case.
        """
        tool_name_override = cls._alias
        tool_name = (
            tool_name_override
            if isinstance(tool_name_override, str) and tool_name_override
            else cls.__name__
        )
        return pascal_to_snake(tool_name)

    @abstractmethod
    def run(self) -> Result: ...

    @classmethod
    def validate(cls, model: BaseModel) -> Self:
        """
        Creates an instance of the Action class from a Pydantic model.
        """
        return cls(**model.model_dump())

    @classmethod
    def get_mcp_definition(cls) -> McpToolDefinition:
        """
        Generates the strict MCPToolDefinition dataclass instance for this tool.
        """
        # 1. Determine Tool Name using the property for canonicalization
        tool_name = cls.get_action_id()

        # 2. Determine Tool Description
        tool_desc = inspect.getdoc(cls) or f"Executes the {tool_name} tool."
        if not tool_desc.strip():
            logger.warning(
                f"Tool class '{tool_name}' has an empty or missing docstring."
            )
            tool_desc = f"Executes the {tool_name} tool."

        # 3. Generate and Extract JSON Schema parts
        try:
            model_schema = cls.model_json_schema()
            input_schema_properties = model_schema.get("properties", {})
            input_schema_required = model_schema.get("required", [])
        except Exception as e:  # noqa: BLE001
            logger.error(
                f"Failed to generate JSON schema for {tool_name}: {e}", exc_info=True
            )
            input_schema_properties = {}
            input_schema_required = []
            tool_desc += " (Schema generation failed)"  # Append warning to description

        # 4. Construct the parameters_json_schema dictionary adhering to MCP standard
        input_schema_dict: dict = {
            "type": "object",
            "properties": input_schema_properties,
            # Only add 'required' key if the list is not empty
            **({"required": input_schema_required} if input_schema_required else {}),
        }

        # 5. Determine Annotations
        tool_annotations_override = getattr(cls, "_mcp_annotations", None)
        tool_annotations = (
            tool_annotations_override
            if isinstance(tool_annotations_override, dict)
            else None
        )

        # 6. Instantiate and return the strict MCPToolDefinition dataclass
        return McpToolDefinition(
            name=tool_name,
            description=tool_desc.strip(),
            parameters_json_schema=input_schema_dict,
            annotations=tool_annotations,
        )

