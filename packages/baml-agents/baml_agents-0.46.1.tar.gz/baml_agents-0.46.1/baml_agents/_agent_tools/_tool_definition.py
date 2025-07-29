import json
from typing import Any, Self

from pydantic import BaseModel, Field


class McpToolDefinition(BaseModel):
    name: str = Field(..., exclude=True)
    description: str
    parameters_json_schema: dict[str, Any]
    annotations: dict[str, Any] | None = None

    @classmethod
    def from_mcp_schema(cls, mcp_schema: str | dict[str, Any]) -> list[Self]:
        parsed = json.loads(mcp_schema) if isinstance(mcp_schema, str) else mcp_schema
        tools = parsed.get("tools", [])
        return [
            cls(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters_json_schema=tool.get("inputSchema", {}),
            )
            for tool in tools
        ]

