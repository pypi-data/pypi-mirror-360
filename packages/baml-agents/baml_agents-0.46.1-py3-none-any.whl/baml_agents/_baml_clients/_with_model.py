import os
from typing import TypeVar

from pydantic import BaseModel

from ._with_baml_client import with_baml_client

T = TypeVar("T")


class BamlModelConfig(BaseModel):
    provider: str = "openai"
    api_key: str | None = None
    api_key_env_var: str = "OPENAI_API_KEY"
    base_url: str | None = None
    base_url_env_var: str = "OPENAI_API_BASE"


def with_model(
    b: T,
    model: str,
    *,
    config: BamlModelConfig | None = None,
) -> T:
    config = config or BamlModelConfig()
    api_key = config.api_key or os.environ.get(config.api_key_env_var)
    base_url = config.base_url or os.environ.get(config.base_url_env_var)

    options = {
        "model": model,
        "api_key": api_key,
    }
    if base_url:
        options["base_url"] = base_url

    return with_baml_client(b, provider=config.provider, options=options)  # type: ignore
