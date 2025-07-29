import hashlib
from collections.abc import Callable
from typing import Any

from baml_agents._baml_client_proxy._hooks._implementations._test_generator_helpers import (
    get_args_block_str,
)
from baml_agents._baml_client_proxy._hooks._on_before_call_hook import (
    OnBeforeCallHookContext,
    OnBeforeCallHookSync,
)


def generate_baml_test(test_name, baml_function_name, params):
    return f"""\
test {test_name} {{
  functions [{baml_function_name}]
  args {{
{get_args_block_str(params)}
  }}
}}\n\n"""


def default_generate_test_name(baml_function_name, params):
    hash_input = f"{baml_function_name}{params}"
    return f"t_{hashlib.md5(hash_input.encode()).hexdigest()[:6]}"  # noqa: S324


class BamlTestGeneratorHook(OnBeforeCallHookSync):
    def __init__(
        self, *, test_name: str | Callable[[str, dict[str, Any]], str] | None = None
    ):
        if isinstance(test_name, str):
            self.generate_test_name = lambda _, __: test_name
        else:
            self.generate_test_name = test_name or default_generate_test_name
        self.baml_tests: list[str] = []

    def on_before_call(self, params: dict[str, Any], ctx: OnBeforeCallHookContext):
        test_name = self.generate_test_name(ctx.baml_function_name, params)
        baml_test = generate_baml_test(test_name, ctx.baml_function_name, params)
        self.baml_tests.append(baml_test)

    @property
    def baml_test_source_code(self):
        return "\n".join(self.baml_tests)
