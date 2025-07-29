from ._baml_tool_prompt_config import BamlToolPromptConfig
from ._json_schema_to_baml_converter import JsonSchemaToBamlConverter
from ._tool_to_baml_type import ToolToBamlType
from ._type_builder_orchestrator import TypeBuilderOrchestrator


def add_available_actions(output_class: str, tools, tb, cfg=None):
    prompt_cfg = cfg or BamlToolPromptConfig()
    schema_converter = JsonSchemaToBamlConverter()
    tool_converter = ToolToBamlType(schema_converter=schema_converter)
    tbo = TypeBuilderOrchestrator(
        tool_converter=tool_converter,
        prompt_cfg=prompt_cfg,
    )
    field = getattr(tb, output_class, None)
    if field is None:
        raise ValueError(f"Output class {output_class} not found in TypeBuilder.")
    tb = tbo.build_types(
        tb,
        field,
        tools=tools,
    )
    return tb

