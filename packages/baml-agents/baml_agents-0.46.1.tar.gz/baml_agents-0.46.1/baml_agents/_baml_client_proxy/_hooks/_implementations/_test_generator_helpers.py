from typing import Any

from pydantic import BaseModel


# The core recursive formatting function
def _format_baml_value(value: Any, indent_level: int) -> str:
    """
    Recursively formats a Python value into BAML syntax string.
    The returned string includes necessary indentation starting at indent_level.
    Handles primitives, lists, dicts, and Pydantic models.
    """
    indent_space = "  " * indent_level
    content_indent_space = "  " * (indent_level + 1)

    if isinstance(value, BaseModel):
        # Format model as dict at the same indent level
        return _format_baml_value(value.model_dump(mode="json"), indent_level)

    if isinstance(value, dict):
        if not value:
            return "{}"  # Empty dict inline
        items = []
        for k, v in value.items():
            formatted_key = str(k)
            # Format value recursively, starting at the content level
            formatted_value = _format_baml_value(v, indent_level + 1)
            # Combine key and value. Primitive values returned by _format_baml_value
            # have no leading space. Complex values ({...} or [...]) might,
            # but combining them directly after the key space is usually correct.
            items.append(f"{content_indent_space}{formatted_key} {formatted_value}")

        # Construct dict string with braces at the current indent level
        return f"{indent_space}{{\n" + "\n".join(items) + f"\n{indent_space}}}"

    if isinstance(value, list):
        if not value:
            return "[]"  # Empty list inline
        items = []
        is_complex_list = any(
            isinstance(item, (dict, BaseModel, list)) for item in value
        )

        for i, item in enumerate(value):
            # Format item recursively, starting at the content level (+1)
            # formatted_item will be a string representing the item,
            # correctly indented to start at level indent_level + 1.
            formatted_item = _format_baml_value(item, indent_level + 1)
            comma = "," if is_complex_list and i < len(value) - 1 else ""
            # Append the already-indented item string and the comma
            items.append(f"{formatted_item}{comma}")

        # Construct list string with brackets at the current indent level
        # Items are joined by newlines; their existing indentation handles alignment.
        return "[\n" + "\n".join(items) + f"\n{indent_space}]"

    # Primitives: Return representation without adding indentation here.
    if isinstance(value, str):
        return f'#"{value}"#' if value else '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    # Fallback for unsupported types
    repr_str = repr(value)
    return f'#"{repr_str}"#' if repr_str else '""'


def get_args_block_str(params):
    args_to_format = {k: v for k, v in params.items() if k != "baml_options"}
    formatted_args = []
    # Arguments inside 'args {}' block start at indent level 1
    args_block_indent_level = 2
    args_block_indent_space = "  " * args_block_indent_level

    for k, v in args_to_format.items():
        # Format the value. The value itself should be formatted
        # as if starting at the same level as the key for BAML style.
        # Let _format_baml_value handle the internal indentation relative to this level.
        formatted_value = _format_baml_value(v, args_block_indent_level)

        # Combine the argument key (at level 1 indent) with the formatted value.
        formatted_args.append(f"{args_block_indent_space}{k} {formatted_value}")

    # Join the formatted argument lines for the args block content
    return "\n".join(formatted_args)
