from collections.abc import Mapping
from typing import Any

from baml_agents._agent_tools._json_schema_to_baml_source._model_to_baml_source import (
    BamlModelToBamlSourceConverter,
)

from ._json_to_model import (
    JsonSchemaToBamlModelConverter,
    JsonSchemaToBamlModelConverterConfig,
)


def json_schema_to_baml_source(
    class_name,
    json_schema: str | Mapping[str, Any],
    *,
    schema_to_model_config: JsonSchemaToBamlModelConverterConfig | None = None,
):
    schema_to_model = JsonSchemaToBamlModelConverter(
        json_schema, class_name, config=schema_to_model_config
    )
    baml_models = schema_to_model.convert()
    model_to_source = BamlModelToBamlSourceConverter(baml_models)
    baml_source = model_to_source.generate()
    return baml_source

