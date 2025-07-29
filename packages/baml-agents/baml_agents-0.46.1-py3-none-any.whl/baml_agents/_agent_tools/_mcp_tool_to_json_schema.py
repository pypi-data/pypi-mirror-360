from baml_py.type_builder import TypeBuilder

from baml_agents._agent_tools._utils._snake_to_pascal import snake_to_pascal
from baml_agents._utils._merge_dicts_no_overlap import merge_dicts_no_overlap

from ._tool_definition import McpToolDefinition


def mcp_tool_to_json_schema(
    tool: McpToolDefinition,
    tb: TypeBuilder,
    baml_tool_id_field: str,
):
    schema = tool.parameters_json_schema.copy()
    props = merge_dicts_no_overlap(
        {
            "action_id": {
                "title": snake_to_pascal(tool.name),
                "type": tb.literal_string(tool.name),
                "description": tool.description,
            },
        },
        schema.get("properties", {}),
    )
    schema["properties"] = props
    schema["required"] = (*schema.get("required", []), baml_tool_id_field)
    return schema
