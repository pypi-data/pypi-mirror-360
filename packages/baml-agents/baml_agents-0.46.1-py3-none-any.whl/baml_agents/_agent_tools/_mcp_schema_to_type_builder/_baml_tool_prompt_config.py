from dataclasses import dataclass, field


@dataclass(frozen=True)
class BamlToolPromptConfig:
    id_field: str = field(
        default="action_id",
        metadata={"description": "Field name for tool ID"},
    )
    tools_field: str = field(
        default="chosen_action",
        metadata={"description": "Field name for tools collection"},
    )

