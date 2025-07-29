from typing import Any, Self

from pydantic import BaseModel, ConfigDict

from baml_agents._utils._sole import sole


class Result(BaseModel):
    content: str
    error: bool = False

    model_config = ConfigDict(frozen=True)

    @classmethod
    def from_mcp_schema(cls, mcp_result_schema: dict[str, Any]) -> Self:
        item = sole(mcp_result_schema["content"])
        if item["type"] != "text":
            raise ValueError(f"Expected text type, got {item['type']}")
        return cls(content=item["text"], error=mcp_result_schema["isError"])
