import warnings
from typing import Any

from baml_py.baml_py import FieldType
from baml_py.type_builder import TypeBuilder

from baml_agents._agent_tools._utils._snake_to_pascal import snake_to_pascal

from ._abstract_json_schema_to_baml_converter import AbstractJsonSchemaToBamlConverter


class _RefPlaceholder:
    """Private sentinel for circular $ref resolution."""


class JsonSchemaToBamlConverter(AbstractJsonSchemaToBamlConverter):
    """Parse JSON Schema into BAML field types."""

    def __init__(self, *, fail_on_unknown: bool = True):
        """:param fail_on_unknown: If True, raise on unknown or ambiguous schema shapes."""
        self._fail_on_unknown = fail_on_unknown

    def convert(
        self,
        schema: dict[str, Any],
        tb: TypeBuilder,
    ) -> FieldType:
        """Public entry: parses the entire root schema into a FieldType."""
        cache: dict[str, FieldType | _RefPlaceholder] = {}
        return self._parse(schema, tb, cache, schema)

    def _parse(
        self,
        schema: dict[str, Any],
        tb: TypeBuilder,
        cache: dict[str, FieldType | _RefPlaceholder],
        root_schema: dict[str, Any],
    ) -> FieldType:
        if "$ref" not in schema and "anyOf" not in schema and "type" not in schema:
            msg = (
                f"Schema missing both 'type' and 'anyOf': {schema!r}. "
                "This is likely an invalid or unsupported schema shape."
            )
            if self._fail_on_unknown:
                raise ValueError(msg)
            warnings.warn(msg, stacklevel=2)
            # Fallback: treat as string for robustness
            return tb.string()

        if ref := schema.get("$ref"):
            return self._resolve_ref(ref, tb, cache, root_schema)

        if any_of := schema.get("anyOf"):
            return tb.union(
                [self._parse(sub, tb, cache, root_schema) for sub in any_of],
            )

        t = schema.get("type")
        if isinstance(t, FieldType):
            return t
        match t:
            case "object":
                return self._object(schema, tb, cache, root_schema)
            case "array":
                item_type = self._parse(schema["items"], tb, cache, root_schema)
                return item_type.list()
            case "string":
                return self._string(schema, tb)
            case "integer":
                return tb.int()
            case "number":
                return tb.float()
            case "boolean":
                return tb.bool()
            case "null":
                return tb.null()
            case None:
                msg = (
                    f"No 'type' found in schema: {schema!r}. "
                    "Defaulting to string. Set fail_on_unknown=True to raise instead."
                )
                if self._fail_on_unknown:
                    raise ValueError(msg)
                warnings.warn(msg, stacklevel=2)
                return tb.string()
            case other:
                # Improved error message: include the schema snippet for debugging
                raise ValueError(f"Unsupported type: {other!r} in schema: {schema!r}")

    def _object(
        self,
        schema: dict[str, Any],
        tb: TypeBuilder,
        cache: dict[str, FieldType | _RefPlaceholder],
        root_schema: dict[str, Any],
    ) -> FieldType:
        # Warn if additionalProperties is present, since we ignore it
        if "additionalProperties" in schema:
            warnings.warn(
                f"JSON Schema 'additionalProperties' is present in object schema but will be ignored: {schema['additionalProperties']!r} (schema title: {schema.get('title')!r})",
                stacklevel=2,
            )
        cls = tb.add_class(snake_to_pascal(schema["properties"]["action_id"]["title"]))
        required = set(schema.get("required", []))
        for name, prop in schema.get("properties", {}).items():
            field = self._parse(prop, tb, cache, root_schema)
            if name not in required:
                field = field.optional()
            p = cls.add_property(name, field)
            if desc := prop.get("description"):
                p.description(desc.strip())
            if alias := prop.get("baml_alias"):
                p.alias(alias)
        return cls.type()

    def _string(
        self,
        schema: dict[str, Any],
        tb: TypeBuilder,
    ) -> FieldType:
        if enum := schema.get("enum"):
            if title := schema.get("title"):
                enum_def = tb.add_enum(title)
                for v in enum:
                    enum_def.add_value(v)
                return enum_def.type()
            return tb.union([tb.literal_string(v) for v in enum])
        return tb.string()

    def _resolve_ref(
        self,
        ref: str,
        tb: TypeBuilder,
        cache: dict[str, FieldType | _RefPlaceholder],
        root_schema: dict[str, Any],
    ) -> FieldType:
        if not ref.startswith("#/"):
            raise ValueError(
                f"External refs are not supported: {ref!r}. "
                "Only local JSON Pointer refs (starting with '#/') are supported. "
                "Did you mean to inline this definition or ensure all refs are local?",
            )
        if ref in cache:
            val = cache[ref]
            if isinstance(val, _RefPlaceholder):
                raise ValueError(f"Circular $ref detected for {ref!r}")
            return val

        # split "#/definitions/Foo" → ["definitions", "Foo"]
        section, *path = ref.lstrip("#/").split("/")
        node = root_schema.get(section, {})
        for key in path:
            node = node[key]

        # Insert a private sentinel into the cache before recursing to prevent infinite recursion on circular refs.
        cache[ref] = _RefPlaceholder()

        ft = self._parse(node, tb, cache, root_schema)
        cache[ref] = ft
        return ft

