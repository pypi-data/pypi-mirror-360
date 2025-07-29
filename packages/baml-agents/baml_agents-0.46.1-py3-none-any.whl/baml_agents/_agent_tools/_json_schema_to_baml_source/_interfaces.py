import json
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, runtime_checkable

from ._model import BamlClassModel, BamlEnumModel

if TYPE_CHECKING:
    from baml_py.type_builder import TypeBuilder

T = TypeVar("T", bound="TypeBuilder")


class BaseSchemaConverter:
    def __init__(self, schema: str | Mapping[str, Any]):
        if isinstance(schema, str):
            try:
                self._root_schema: dict[str, Any] = json.loads(schema)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON schema provided: {e}") from e
        elif isinstance(schema, Mapping):
            self._root_schema = dict(schema)
        else:
            raise TypeError(
                f"Schema must be a JSON string or a dictionary, got {type(schema)}",
            )


class AbstractMcpSchemaToBamlModelConverter(ABC, BaseSchemaConverter):
    @abstractmethod
    def convert_tools(self) -> list[BamlClassModel | BamlEnumModel]:
        pass


class AbstractJsonSchemaToBamlModelConverter(ABC, BaseSchemaConverter):
    def __init__(self, schema: str | Mapping[str, Any], class_name: str):
        super().__init__(schema)
        self._class_name = class_name

    @abstractmethod
    def convert(self) -> list[BamlClassModel | BamlEnumModel]:
        pass


class BamlModelConverter:
    def __init__(self, baml_models: list[BamlClassModel | BamlEnumModel]):
        # Check for duplicate model names
        names = [model.name for model in baml_models]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError(
                f"Duplicate model names found: {', '.join(sorted(duplicates))}"
            )

        self._baml_models = baml_models


class BamlSourceGenerator(ABC, Generic[T], BamlModelConverter):
    """Abstract base for generating BAML source code."""

    @abstractmethod
    def generate(self) -> str:
        """
        Generate BAML source code.

        :return: BAML source code as a string.
        """


class BamlTypeBuilderConfigurer(ABC, Generic[T], BamlModelConverter):
    """Abstract base for configuring BAML TypeBuilder objects by adding types/classes."""

    @abstractmethod
    def configure(self, tb: T):
        """
        Add types/classes into the provided TypeBuilder.

        :param tb: An instance of TypeBuilder to be configured.
        """


@runtime_checkable
class ArgsClassCallback(Protocol):
    def __call__(
        *,
        name: str,
        schema: dict[str, Any],
    ) -> str: ...


@runtime_checkable
class ToolClassCallback(Protocol):
    def __call__(
        *,
        name: str,
        schema: dict[str, Any],
    ) -> str: ...


@runtime_checkable
class ToolNameCallback(Protocol):
    def __call__(
        *,
        name: str,
        schema: dict[str, Any],
    ) -> str: ...


@runtime_checkable
class PropNameCallback(Protocol):
    def __call__(
        *,
        name: str,
        prop_schema: dict[str, Any],
        class_schema: dict[str, Any],
        root_class_schema: dict[str, Any],
    ) -> str: ...


@runtime_checkable
class DescCallback(Protocol):
    def __call__(
        *,
        description: str | None,
        root: bool,
        prop_schema: dict[str, Any],
        class_schema: dict[str, Any],
        root_class_schema: dict[str, Any],
    ) -> str | None: ...


@runtime_checkable
class AliasCallback(Protocol):
    def __call__(
        *,
        name: str,
        root: bool,
        prop_schema: dict[str, Any],
        class_schema: dict[str, Any],
        root_class_schema: dict[str, Any],
    ) -> str | None: ...

