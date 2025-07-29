from abc import ABC, abstractmethod
from typing import Any

from baml_py.baml_py import FieldType
from baml_py.type_builder import TypeBuilder


class AbstractJsonSchemaToBamlConverter(ABC):
    """Abstract base for JSON Schema to BAML field type converters."""

    @abstractmethod
    def convert(
        self,
        schema: dict[str, Any],
        tb: TypeBuilder,
        **_,
    ) -> FieldType:
        """Parse the entire root schema into a FieldType."""

