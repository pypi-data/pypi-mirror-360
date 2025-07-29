import hashlib
import json
import os
import shelve
import shlex
import subprocess
import threading
from collections.abc import Callable, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any, Generic, TypeVar, cast

from baml_py.type_builder import TypeBuilder
from loguru import logger
from pydantic import BaseModel

from baml_agents._agent_tools._action import Action
from baml_agents._agent_tools._baml_client_passthrough_wrapper import PassthroughWrapper
from baml_agents._agent_tools._mcp_schema_to_type_builder._facade import (
    add_available_actions,
)
from baml_agents._agent_tools._str_result import Result
from baml_agents._agent_tools._tool_definition import McpToolDefinition
from baml_agents._agent_tools._utils._snake_to_pascal import pascal_to_snake

# Use a lock to avoid concurrent shelve access issues
_shelve_lock = threading.Lock()

T = TypeVar("T", bound=TypeBuilder)
B = TypeVar("B")


def get_cache_path() -> str:
    cache_path = Path(".cache") / "mcp_cli_cache"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    return str(cache_path)


def _make_cache_key(*args) -> str:
    # Deterministically hash the arguments for a cache key
    key_str = json.dumps(args, sort_keys=True, default=str)
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()


def normalize_action_id(action_id):
    return pascal_to_snake(action_id)


NO_SILENT_TYPEBUILDER_OVERWRITE = True


class ActionRunner(Generic[T, B]):
    def __init__(
        self,
        tbc: type[T],
        *,
        b: B | None = None,
        cache: bool | None = None,
    ):
        self._original_baml_client = b
        self._baml_client = (
            PassthroughWrapper(
                self._original_baml_client,
                mutate_args_kwargs=self._mutate_baml_function_args_kwargs,
            )
            if self._original_baml_client is not None
            else None
        )
        self._actions = []
        self._tool_to_function = {}
        self._cache = False if cache is None else cache
        self._tb_cls = tbc

        self._teleport_baml_class = None
        self._teleport_tb = None
        self._teleport_include = None

    def _mutate_baml_function_args_kwargs(
        self, args, kwargs, baml_function_return_type_name
    ):
        tb = None
        baml_options = None
        baml_options_args_i = None
        for v, i in enumerate(args):
            if isinstance(v, dict) and "tb" in v and isinstance(v["tb"], TypeBuilder):
                baml_options = v
                baml_options_args_i = i
                tb = v["tb"]
        for v in kwargs:
            if isinstance(v, dict) and "tb" in v and isinstance(v["tb"], TypeBuilder):
                baml_options = v
                tb = v["tb"]
        if tb and self._teleport_tb:
            raise ValueError(
                """Both baml_options={"tb": tb) and .b_(tb=tb) are set. Please use only one."""
            )
        tb = tb or self._teleport_tb or self._tb_cls()  # type: ignore

        baml_function_return_type_name = (
            self._teleport_baml_class or baml_function_return_type_name
        )

        tb = self.tb(baml_function_return_type_name, tb=tb, include=self._teleport_include)  # type: ignore

        self._teleport_baml_class = None
        self._teleport_tb = None
        self._teleport_include = None

        baml_options = {**(baml_options or {}), "tb": tb}
        if baml_options_args_i:
            if NO_SILENT_TYPEBUILDER_OVERWRITE:
                raise ValueError(
                    """Please provide TypeBuilder like this: b_(tb=tb).MyBamlFunction() instead of: MyBamlFunction(baml_options={'tb': tb})."""
                )
            new_args = tuple(
                baml_options if idx == baml_options_args_i else arg
                for idx, arg in enumerate(args)
            )
            return new_args, kwargs
        if NO_SILENT_TYPEBUILDER_OVERWRITE and "baml_options" in kwargs:
            raise ValueError(
                """Please provide TypeBuilder like this: b_(tb=tb).MyBamlFunction() instead of: MyBamlFunction(baml_options={'tb': tb})."""
            )
        new_kwargs = {
            **kwargs,
            "baml_options": baml_options,
        }
        return args, new_kwargs

    @property
    def b(self) -> B:
        return self.b_()

    def b_(
        self,
        *,
        return_class: str | type["BaseModel"] | None = None,
        tb: T | None = None,
        include: Callable[[McpToolDefinition], bool] | None = None,
    ) -> B:
        if self._baml_client is None:
            raise ValueError(
                "Field not set. Please pass argument `b=b` (BAML Client) to the constructor, for example: ActionRunner(..., b=b)."
            )

        self._teleport_baml_class = return_class
        self._teleport_tb = tb
        self._teleport_include = include
        return self._baml_client  # type: ignore

    def add_from_mcp_server(
        self,
        server: str,
        *,
        include: Callable[[McpToolDefinition], bool] | None = None,
        env: dict | None = None,
    ):
        tools = list_tools(server, cache=self._cache, env=env)
        for t in tools:
            if include and not include(t):
                continue
            if t.name in self._tool_to_function:
                raise ValueError(
                    f"Tool {t.name} already exists in the tool to function map."
                )
            # Use self._cache to control call_tool caching
            self._tool_to_function[normalize_action_id(t.name)] = (
                lambda params, t=t, env=env: call_tool(
                    t.name,
                    params,
                    server,
                    cache=self._cache,
                    env=env,
                )
            )
            self._actions.append(t)

    def add_action(self, action: type[Action], handler=None):
        definition = action.get_mcp_definition()
        definition.name = normalize_action_id(definition.name)
        name = definition.name
        self._actions.append(definition)
        if name in self._tool_to_function:
            raise ValueError(f"Tool {name} already exists in the tool to function map.")
        self._tool_to_function[name] = handler or (
            lambda params: action(**params).run()
        )

    def state(self) -> dict[str, Any]: ...

    def run(self, result: Any) -> Any:
        result = cast("BaseModel", result)
        action = result.model_dump()["chosen_action"]
        action_id = action["action_id"]
        action_params = {k: v for k, v in action.items() if k != "action_id"}
        if action_id not in self._tool_to_function:
            raise ValueError(
                f"Action {action_id} not found in the tool to function map."
            )

        result = self._tool_to_function[action_id](action_params)
        if isinstance(result, Result):
            return result
        return Result.from_mcp_schema(result)

    @property
    def actions(self):
        return deepcopy(self._actions)

    def tb(
        self,
        field: str | type["BaseModel"],
        /,
        *,
        tb: T | None = None,
        include: Callable[[McpToolDefinition], bool] | None = None,
    ) -> T:
        tb = tb or self._tb_cls()  # type: ignore
        field_name = (
            field.__name__
            if isinstance(field, type) and issubclass(field, BaseModel)
            else field
        )
        actions = self._actions
        if include is not None:
            actions = [a for a in actions if include(a)]
        return add_available_actions(field_name, actions, tb)


def list_tools(
    server: str, *, cache: bool = False, env: dict | None = None
) -> list[McpToolDefinition]:
    cache_key = _make_cache_key("list_tools", server)
    if cache:
        with _shelve_lock, shelve.open(get_cache_path()) as cache_db:  # noqa: S301
            if cache_key in cache_db:
                mcp_schema = cache_db[cache_key]
            else:
                command = f"mcpt tools {server} --format json"
                mcp_schema = _run_cli_command(command, env=env)
                cache_db[cache_key] = mcp_schema
    else:
        command = f"mcpt tools {server} --format json"
        mcp_schema = _run_cli_command(command, env=env)
    return McpToolDefinition.from_mcp_schema(mcp_schema)


def call_tool(
    tool: str,
    params: dict[str, object],
    server: str,
    *,
    cache: bool = False,
    env: dict | None = None,
) -> object:
    params_json = json.dumps(params, sort_keys=True)
    cache_key = _make_cache_key("call_tool", tool, params_json, server)
    if cache:
        with _shelve_lock, shelve.open(get_cache_path()) as cache_db:  # noqa: S301
            if cache_key in cache_db:
                output = cache_db[cache_key]
            else:
                params_suffix = f" -p '{params_json}'" if params_json else ""
                command = f"mcpt call {tool}{params_suffix} {server} --format json"
                output = _run_cli_command(command, env=env)
                cache_db[cache_key] = output
    else:
        params_suffix = f" -p '{params_json}'" if params_json else ""
        command = f"mcpt call {tool}{params_suffix} {server} --format json"
        output = _run_cli_command(command, env=env)
    return json.loads(output)


def _run_cli_command(command: str | Sequence[str], *, env: dict | None = None) -> str:
    if isinstance(command, str):
        command = shlex.split(command)
    logger.debug("Running CLI command", command=command)
    result = subprocess.run(  # noqa: S603
        command,
        capture_output=True,
        text=True,
        check=False,
        env={**(env or {}), **os.environ},
    )
    if result.stderr:
        msg = f"[stderr] (exit code {result.returncode})\n{result.stderr.strip()}"
        raise RuntimeError(msg)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}")
    return result.stdout.strip()

