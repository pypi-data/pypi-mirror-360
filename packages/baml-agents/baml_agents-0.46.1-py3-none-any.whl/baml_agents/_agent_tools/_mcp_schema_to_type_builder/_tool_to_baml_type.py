from abc import ABC, abstractmethod

from baml_py.baml_py import FieldType
from baml_py.type_builder import TypeBuilder

from baml_agents._agent_tools._mcp_tool_to_json_schema import mcp_tool_to_json_schema
from baml_agents._agent_tools._tool_definition import McpToolDefinition

from ._abstract_json_schema_to_baml_converter import AbstractJsonSchemaToBamlConverter


class AbstractToolToBamlType(ABC):

    @abstractmethod
    def convert(
        self,
        *,
        tool: McpToolDefinition,
        tb: TypeBuilder,
        baml_tool_id_field: str,
        **_,
    ) -> FieldType:
        pass


class ToolToBamlType(AbstractToolToBamlType):
    def __init__(
        self,
        *,
        schema_converter: AbstractJsonSchemaToBamlConverter,
    ):
        self._converter = schema_converter

    def convert(
        self,
        *,
        tool: McpToolDefinition,
        tb: TypeBuilder,
        baml_tool_id_field: str,
    ) -> FieldType:
        schema = mcp_tool_to_json_schema(tool, tb, baml_tool_id_field)
        return self._converter.convert(schema, tb)

