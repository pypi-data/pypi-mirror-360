from typing import TypeVar

from baml_py import ClientRegistry

T = TypeVar("T")


def with_baml_client(
    b: T,
    *,
    provider: str,
    options: dict,
) -> T:
    cr = ClientRegistry()
    if "model" not in options:
        raise ValueError("Options must contain a 'model' key.")
    model = options["model"]
    name = f"{provider}/{model}"
    cr.add_llm_client(
        name=name,
        provider=provider,
        options=options,
    )
    cr.set_primary(name)
    return b.with_options(client_registry=cr)  # type: ignore
