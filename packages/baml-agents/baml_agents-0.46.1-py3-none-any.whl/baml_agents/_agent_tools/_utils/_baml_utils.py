from collections.abc import Callable
from typing import TypeVar

from baml_agents._utils._sole import sole

T = TypeVar("T")


def default_format_role(role: str) -> str:
    return f"[{role}]\n"


def disable_format_role(role: str) -> str:  # noqa: ARG001
    return ""


def get_prompt(request, *, format_role: Callable[[str], str] | None = None):
    if format_role is None:
        format_role = default_format_role

    try:
        return sole(sole(request.body.json()["contents"])["parts"])["text"]
    except KeyError as e:
        messages = request.body.json()["messages"]
        prompt_parts = []
        for message in messages:
            content = sole(message["content"])
            if content["type"] != "text":
                raise ValueError(
                    f"Expected content type 'text', but got '{content['type']}'",
                ) from e
            prompt_parts.append(f"{format_role(message['role'])}{content['text']}")
        return "\n\n".join(prompt_parts)


def display_prompt(request):
    escaped_prompt = (
        get_prompt(request).replace("<", "‹").replace(">", "›")  # noqa: RUF001
    )
    print(escaped_prompt)  # noqa: T201
