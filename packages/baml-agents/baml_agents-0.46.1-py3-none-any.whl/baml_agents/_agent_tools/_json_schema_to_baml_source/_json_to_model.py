import re
import warnings
from collections.abc import Mapping
from contextlib import suppress
from typing import Any, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from ._default_callbacks import (
    DefaultAlias,
    DefaultDesc,
    DefaultPropName,
)
from ._interfaces import (
    AbstractJsonSchemaToBamlModelConverter,
    AliasCallback,
    DescCallback,
    PropNameCallback,
)
from ._model import (
    BamlBaseType,
    BamlClassModel,
    BamlEnumModel,
    BamlEnumValueModel,
    BamlFieldModel,
    BamlTypeInfo,
)


class SchemaTypeAndUnions(NamedTuple):
    effective_type: str | None
    union_options: list[BamlTypeInfo] | None


class JsonSchemaToBamlModelConverterConfig(BaseModel):
    prop_name: PropNameCallback = Field(default_factory=DefaultPropName)
    desc: DescCallback = Field(default_factory=DefaultDesc)
    alias: AliasCallback = Field(default_factory=DefaultAlias)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class JsonSchemaToBamlModelConverter(AbstractJsonSchemaToBamlModelConverter):
    def __init__(
        self,
        schema: str | Mapping[str, Any],
        class_name: str,
        *,
        config: JsonSchemaToBamlModelConverterConfig | None = None,
    ):
        super().__init__(schema, class_name)

        # Internal state for tracking definitions and naming
        self._definitions: dict[
            str,
            BamlClassModel | BamlEnumModel | _RefPlaceholder,
        ] = {}
        self._anonymous_type_counter = 0
        self._cfg = config or JsonSchemaToBamlModelConverterConfig()

    def convert(self) -> list[BamlClassModel | BamlEnumModel]:
        """
        Performs the conversion from the JSON schema to BAML models.

        Args:
            class_name: The desired name for the root BAML class generated from the schema.

        Returns:
            A list of BamlClassModel and BamlEnumModel instances representing
            all the types defined or referenced within the schema.

        """
        self._definitions = {}  # Reset definitions for potentially multiple calls
        self._anonymous_type_counter = 0

        # Start parsing from the root schema, using the provided class_name
        self._parse_schema_to_type_info(
            schema=self._root_schema,
            json_pointer="#",
            forced_class_name=self._class_name,
        )

        # Extract all successfully created models from the definitions map
        models = [
            model
            for model in self._definitions.values()
            if isinstance(model, (BamlClassModel, BamlEnumModel))
        ]
        return models

    # --- Core Parsing Orchestrator ---

    def _parse_schema_to_type_info(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        *,
        is_property_optional: bool = False,
        forced_class_name: str | None = None,
    ) -> BamlTypeInfo:
        """
        Orchestrates the parsing of a JSON schema node into a BamlTypeInfo.
        Delegates to specialized handlers based on the schema structure.

        Args:
            schema: The schema dictionary to parse.
            json_pointer: The JSON pointer path to this schema node.
            is_property_optional: True if this schema represents a property not in the parent's 'required' list.
            forced_class_name: If provided, use this as the class name for an object type at this level.

        Returns:
            A BamlTypeInfo object representing the type defined by the schema.

        """
        # Step 1: Handle $ref if present (returns immediately if ref found)
        ref_type_info = self._handle_ref(
            schema,
            json_pointer,
            is_property_optional=is_property_optional,
        )
        if ref_type_info:
            return ref_type_info

        # Step 2: Determine the primary type(s) defined (explicit type, anyOf, oneOf)
        type_str, union_options = self._determine_schema_type_and_unions(
            schema,
            json_pointer,
        )

        # Step 3: Handle Unions (anyOf, oneOf, type array)
        if union_options is not None:
            # This recursively calls _parse_schema_to_type_info for each option
            return self._create_union_or_optional_type(
                union_options,
                is_context_optional=is_property_optional,
            )

        # Step 4: Infer type if not explicitly provided but implied
        effective_type = type_str or self._infer_effective_type(schema, json_pointer)

        # Step 5: Process based on the determined single effective type
        final_type_info = self._process_single_type_schema(
            schema=schema,
            json_pointer=json_pointer,
            effective_type=effective_type,
            forced_class_name=forced_class_name,
        )

        # Step 6: Apply contextual optionality (from parent 'required' list)
        # This overrides or combines with optionality derived from type itself (e.g., String|Null)
        final_type_info.is_optional = (
            is_property_optional or final_type_info.is_optional
        )

        return final_type_info

    # --- Specialized Parsing Helpers ---

    def _handle_ref(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        *,
        is_property_optional: bool,
    ) -> BamlTypeInfo | None:
        """
        Handles schema nodes containing a '$ref'. Resolves the reference,
        parses the target schema (handling recursion and caching), and returns
        the corresponding BamlTypeInfo if a '$ref' exists.

        Returns:
            BamlTypeInfo if a valid $ref is processed, None otherwise.

        """
        ref = schema.get("$ref")
        if not ref:
            return None  # Not a reference schema

        if not isinstance(ref, str):
            raise InvalidRefError(
                f"Invalid $ref value at '{json_pointer}': must be a string, got {type(ref)}",
            )

        # Check cache first to handle recursion and avoid re-parsing
        if ref in self._definitions:
            existing = self._definitions[ref]
            if isinstance(existing, _RefPlaceholder):
                # Circular reference detected during resolution
                raise CircularRefError(
                    f"Circular $ref detected involving '{ref}' (encountered at '{json_pointer}')",
                )
            if isinstance(existing, BamlClassModel):
                # Return type info for existing cached class
                return BamlTypeInfo(
                    base_type=BamlBaseType.CLASS,
                    custom_type_name=existing.name,
                    is_optional=is_property_optional,  # Optionality depends on context
                )
            if isinstance(existing, BamlEnumModel):
                # Return type info for existing cached enum
                return BamlTypeInfo(
                    base_type=BamlBaseType.ENUM,
                    custom_type_name=existing.name,
                    is_optional=is_property_optional,  # Optionality depends on context
                )
            # Should not happen
            raise UnexpectedTypeError(
                f"Unexpected cached type for $ref '{ref}': {type(existing)}",
            )

        # Ref not cached, resolve and parse recursively
        try:
            resolved_schema = self._resolve_ref(ref, json_pointer)
            # Add placeholder *before* recursive call to detect circularity
            self._definitions[ref] = _RefPlaceholder(ref)

            # Recursively parse the resolved schema. Crucially, pass the *contextual* optionality.
            type_info = self._parse_schema_to_type_info(
                schema=resolved_schema,
                json_pointer=ref,  # Use the ref itself as the new pointer context
                is_property_optional=is_property_optional,  # Pass down optionality
            )

            # Update cache with the actual model if one was created during resolution
            self._cache_resolved_ref_model(ref, type_info)

            # Return the derived type info, ensuring contextual optionality is set
            type_info.is_optional = is_property_optional
            return type_info

        except (
            InvalidRefError,
            CircularRefError,
            UnexpectedTypeError,
            RefResolutionError,
            TypeError,
            ValueError,
        ) as e:
            # Clean up placeholder if resolution/parsing failed
            if ref in self._definitions and isinstance(
                self._definitions[ref],
                _RefPlaceholder,
            ):
                del self._definitions[ref]
            raise RefResolutionError(
                f"Error processing $ref '{ref}' at '{json_pointer}': {e}",
            ) from e
        finally:
            # Ensure placeholder is removed if it wasn't replaced by a model,
            # unless an error was already raised. This handles refs to primitives.
            if ref in self._definitions and isinstance(
                self._definitions[ref],
                _RefPlaceholder,
            ):
                # Check if a model corresponding to the type info was actually created and cached
                # If type_info points to a class/enum, check if that name exists as a model
                should_delete = True
                if (
                    hasattr(type_info, "custom_type_name")
                    and type_info.custom_type_name
                    and type_info.custom_type_name in self._definitions
                ):
                    # A model likely exists, cache_resolved_ref_model should handle it
                    pass  # Keep placeholder for now, let cache_resolved_ref_model decide
                if (
                    should_delete
                    and ref in self._definitions
                    and isinstance(self._definitions[ref], _RefPlaceholder)
                ):
                    # Might have been deleted by _cache_resolved_ref_model already
                    with suppress(KeyError):
                        del self._definitions[ref]

    def _cache_resolved_ref_model(self, ref: str, type_info: BamlTypeInfo) -> None:
        """Helper to update the definitions cache after resolving a $ref."""
        if type_info.base_type == BamlBaseType.CLASS and type_info.custom_type_name:
            model = self._definitions.get(type_info.custom_type_name)
            if isinstance(model, BamlClassModel):
                self._definitions[ref] = model  # Replace placeholder with actual model
            else:
                warnings.warn(
                    f"Could not find BamlClassModel '{type_info.custom_type_name}' to cache for $ref '{ref}'."
                    " This might happen with complex nested anonymous types referenced later.",
                )
                # Decide whether to keep or delete placeholder if model not found
                if ref in self._definitions and isinstance(
                    self._definitions[ref],
                    _RefPlaceholder,
                ):
                    del self._definitions[
                        ref
                    ]  # Remove placeholder if model link is broken

        elif type_info.base_type == BamlBaseType.ENUM and type_info.custom_type_name:
            model = self._definitions.get(type_info.custom_type_name)
            if isinstance(model, BamlEnumModel):
                self._definitions[ref] = model  # Replace placeholder with actual model
            else:
                warnings.warn(
                    f"Could not find BamlEnumModel '{type_info.custom_type_name}' to cache for $ref '{ref}'.",
                )
                if ref in self._definitions and isinstance(
                    self._definitions[ref],
                    _RefPlaceholder,
                ):
                    del self._definitions[ref]  # Remove placeholder

        # If the ref resolved to a primitive or basic type, the placeholder
        # should generally be removed (handled in the finally block of _handle_ref or here).
        elif ref in self._definitions and isinstance(
            self._definitions[ref],
            _RefPlaceholder,
        ):

            with suppress(KeyError):
                del self._definitions[ref]

    def _determine_schema_type_and_unions(
        self,
        schema: dict[str, Any],
        json_pointer: str,
    ) -> SchemaTypeAndUnions:
        """
        Determines the effective JSON schema type(s). Handles explicit 'type' keyword
        (string or list), 'anyOf', and 'oneOf'.

        Returns:
            A tuple: (effective_type_string, list_of_union_options | None).
            - If a single type string is found, returns (type_string, None).
            - If multiple types (type list, anyOf, oneOf) are found, returns (None, list_of_parsed_BamlTypeInfo).
            - If no type information is found, returns (None, None).

        """
        schema_type = schema.get("type")
        types: list[str] = []
        if isinstance(schema_type, str):
            types = [schema_type]
        elif isinstance(schema_type, list):
            types = [t for t in schema_type if isinstance(t, str)]  # Filter non-strings

        # Handle union keywords first (anyOf/oneOf take precedence over 'type' if both exist)
        union_schemas = schema.get("anyOf") or schema.get(
            "oneOf",
        )  # Treat oneOf like anyOf for type analysis
        if union_schemas and isinstance(union_schemas, list):
            union_options: list[BamlTypeInfo] = []
            key = "anyOf" if "anyOf" in schema else "oneOf"
            for i, sub_schema in enumerate(union_schemas):
                if isinstance(sub_schema, dict):
                    # Recursively parse each option *without* passing contextual optionality yet
                    # Optionality will be handled by _create_union_or_optional_type
                    option_type = self._parse_schema_to_type_info(
                        sub_schema,
                        f"{json_pointer}/{key}/{i}",
                    )
                    union_options.append(option_type)
                else:
                    warnings.warn(
                        f"Ignoring non-dictionary item in {key} at '{json_pointer}/{key}/{i}'",
                    )
            return SchemaTypeAndUnions(
                None,
                union_options,
            )  # Return parsed options for union processing

        # Handle explicit type arrays (e.g., ["string", "null"])
        if len(types) > 1:
            # Simulate anyOf structure for consistent handling by _create_union_or_optional_type
            simulated_anyof = [{"type": t} for t in types]
            union_options = []
            for i, sub_schema in enumerate(simulated_anyof):
                # Recursively parse each simulated option
                option_type = self._parse_schema_to_type_info(
                    sub_schema,
                    f"{json_pointer}/type/{i}",  # Pointer reflects source
                )
                union_options.append(option_type)
            return SchemaTypeAndUnions(
                None,
                union_options,
            )  # Return parsed options for union processing

        # Handle single explicit type
        if len(types) == 1:
            return SchemaTypeAndUnions(types[0], None)

        # No explicit type, anyOf, or oneOf found
        return SchemaTypeAndUnions(None, None)

    def _infer_effective_type(
        self,
        schema: dict[str, Any],
        json_pointer: str,
    ) -> str | None:
        """
        Infers the JSON schema type if not explicitly provided, based on other
        keywords like 'properties' or 'enum'.

        Returns:
            The inferred type ('object', 'string') or None if no inference is made.

        """
        if "properties" in schema:
            warnings.warn(
                f"Schema at '{json_pointer}' lacks 'type' but has 'properties'; assuming 'object'.",
            )
            return "object"
        if "enum" in schema:
            # Check if values are strings, default to string enum if type is missing
            if all(isinstance(v, str) for v in schema.get("enum", [])):
                warnings.warn(
                    f"Schema at '{json_pointer}' lacks 'type' but has 'enum' with string values; assuming 'string'.",
                )
                return "string"
            # Add checks for other enum types if needed (e.g., integer enums)
            warnings.warn(
                f"Schema at '{json_pointer}' lacks 'type' but has 'enum' with non-string values; cannot reliably infer base type. Defaulting later.",
            )
            return None  # Let the main processor handle it as 'any' or error

        return None  # No basis for inference

    def _process_single_type_schema(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        effective_type: str | None,
        forced_class_name: str | None = None,
    ) -> BamlTypeInfo:
        """
        Processes a schema node based on a single, determined effective type
        (e.g., 'object', 'array', 'string', 'integer', etc.). Delegates to
        type-specific parsing methods.

        Returns:
            The BamlTypeInfo corresponding to the effective_type. Defaults to 'any'
            if the type is unknown, unsupported, or None.

        """
        if effective_type == "object":
            # Check for map-like objects - BAML modeling might differ, warn for now.
            if isinstance(schema.get("additionalProperties"), dict):
                warnings.warn(
                    f"Schema at '{json_pointer}' uses 'additionalProperties' dictionary. "
                    "BAML conversion currently models this as a standard class. "
                    "Consider defining a clear structure or using 'any'.",
                )
            elif schema.get("additionalProperties") is True:
                warnings.warn(
                    f"Schema at '{json_pointer}' uses 'additionalProperties: true'. "
                    "BAML conversion currently models this as a standard class (no extra fields). "
                    "Consider using 'any' if a truly dynamic map is needed.",
                )
            # Delegate to object parsing (handles class creation/caching)
            return self._parse_object_schema(schema, json_pointer, forced_class_name)

        if effective_type == "array":
            # Delegate to array parsing
            return self._parse_array_schema(schema, json_pointer)

        if effective_type == "string":
            # Delegate to string parsing (handles enums within)
            return self._parse_string_schema(schema, json_pointer)

        if effective_type == "integer":
            return BamlTypeInfo(base_type=BamlBaseType.INT)
        if effective_type == "number":
            return BamlTypeInfo(
                base_type=BamlBaseType.FLOAT,
            )  # Map JSON number to BAML float
        if effective_type == "boolean":
            return BamlTypeInfo(base_type=BamlBaseType.BOOL)
        if effective_type == "null":
            # Represents the literal 'null' type. Optionality is handled later.
            return BamlTypeInfo(base_type=BamlBaseType.NULL)

        if effective_type == "baml_literal_string":
            # Special case for BAML literal strings
            return BamlTypeInfo(
                base_type=BamlBaseType.LITERAL_STRING,
                literal_string=schema["baml_literal_string"],
            )

        # Handle missing type or unknown/unsupported types
        if not effective_type:
            warnings.warn(
                f"Schema at '{json_pointer}' has no discernible type. Defaulting to 'any'. Schema: {schema}",
            )
        else:
            warnings.warn(
                f"Unsupported JSON schema type '{effective_type}' at '{json_pointer}'. Defaulting to 'any'.",
            )
        return BamlTypeInfo(base_type=BamlBaseType.ANY)

    def _parse_array_schema(
        self,
        schema: dict[str, Any],
        json_pointer: str,
    ) -> BamlTypeInfo:
        """Parses an 'array' type schema."""
        items_schema = schema.get("items")
        item_type_info: BamlTypeInfo

        if isinstance(items_schema, dict):
            item_pointer = f"{json_pointer}/items"
            # Recursively parse the item schema. Optionality of items is determined within this call.
            item_type_info = self._parse_schema_to_type_info(items_schema, item_pointer)
        elif items_schema is None:
            # Array with no 'items' defined - default to any[]
            warnings.warn(
                f"Array schema at '{json_pointer}' missing 'items'. Defaulting to list of 'any'.",
            )
            item_type_info = BamlTypeInfo(BamlBaseType.ANY)
        elif isinstance(items_schema, list):
            # JSON Schema tuple validation (fixed-length, typed array) - not directly supported in BAML types easily
            warnings.warn(
                f"Array schema at '{json_pointer}' uses tuple validation (list 'items'). BAML conversion does not support this directly. Defaulting to list of 'any'.",
            )
            item_type_info = BamlTypeInfo(BamlBaseType.ANY)
        elif items_schema is False:
            # "items": false means the array must be empty. Not easily representable as a BAML *type*.
            warnings.warn(
                f"Array schema at '{json_pointer}' uses 'items: false' (must be empty array). Representing as list of 'any' with potential validation needed.",
            )
            item_type_info = BamlTypeInfo(
                BamlBaseType.ANY,
            )  # Or perhaps a special marker? 'any' is safest for type system.
        else:
            # Unknown items format
            warnings.warn(
                f"Unsupported 'items' format in array schema at '{json_pointer}'. Defaulting to list of 'any'. Type was: {type(items_schema)}",
            )
            item_type_info = BamlTypeInfo(BamlBaseType.ANY)

        # The BamlTypeInfo for the list itself. Optionality applied later by the caller.
        return BamlTypeInfo(base_type=BamlBaseType.LIST, item_type=item_type_info)

    def _parse_string_schema(
        self,
        schema: dict[str, Any],
        json_pointer: str,
    ) -> BamlTypeInfo:
        """Parses a 'string' type schema, handling enums."""
        enum_values = schema.get("enum")

        # Check if 'enum' exists and contains only strings
        if (
            isinstance(enum_values, list)
            and enum_values
            and all(isinstance(v, (str, type(None))) for v in enum_values)
        ):
            # Filter out None for enum values, handle optionality via union logic later
            string_enum_values = [v for v in enum_values if isinstance(v, str)]
            if string_enum_values:
                # Delegate to enum parsing if string values exist
                # We pass the original list including None if present, let enum parser handle name/alias
                return self._parse_enum_schema(
                    schema,
                    json_pointer,
                    enum_values,
                )  # Pass original list
            # Enum list exists but only contains null after filtering strings
            warnings.warn(
                f"Enum list at '{json_pointer}' contains only null after filtering non-strings. Treating as 'null' type.",
            )
            return BamlTypeInfo(base_type=BamlBaseType.NULL)
        if isinstance(enum_values, list) and not enum_values:
            warnings.warn(
                f"Empty enum list found at '{json_pointer}'. Treating as regular string.",
            )
            # Fall through to return basic string type

        # Handle other string constraints (pattern, format, etc.) if needed in the future here.
        # For now, just return the base string type.
        return BamlTypeInfo(base_type=BamlBaseType.STR)

    # --- Model Creation Helpers (Object, Enum, Union) ---

    def _parse_object_schema(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        forced_class_name: str | None = None,
    ) -> BamlTypeInfo:
        """
        Parses an 'object' type schema into a BamlClassModel, handling caching
        and recursive property parsing.
        """
        class_name = self._get_or_create_model_name(
            schema,
            json_pointer,
            "Class",
            forced_name=forced_class_name,
        )

        # Check cache/placeholder first (handles recursion)
        if class_name in self._definitions:
            existing = self._definitions[class_name]
            if isinstance(existing, BamlClassModel):
                # Already defined, return type info referencing it
                return BamlTypeInfo(
                    base_type=BamlBaseType.CLASS,
                    custom_type_name=class_name,
                )
            if isinstance(existing, _RefPlaceholder):
                # Currently processing this object due to a reference, return type info
                # The caller (_handle_ref) will eventually cache the real model.
                return BamlTypeInfo(
                    base_type=BamlBaseType.CLASS,
                    custom_type_name=class_name,
                )
            if isinstance(existing, BamlEnumModel):
                # Name collision
                raise NameCollisionError(
                    f"Name collision: Schema at '{json_pointer}' tries to define class '{class_name}' but an enum with this name already exists.",
                )
            # Should not happen
            raise UnexpectedTypeError(
                f"Unexpected type in definitions map for key '{class_name}': {type(existing)}",
            )

        # Add placeholder before parsing properties to handle self-references within properties
        self._definitions[class_name] = _RefPlaceholder(
            json_pointer,
        )  # Use pointer for placeholder context

        properties: list[BamlFieldModel] = []
        required_props: set[str] = set(schema.get("required", []))
        prop_schemas: dict[str, Any] = schema.get("properties", {})

        # Parse properties
        for prop_name, prop_schema in prop_schemas.items():
            if not isinstance(prop_schema, dict):
                warnings.warn(
                    f"Ignoring non-dictionary property schema for '{prop_name}' in class '{class_name}' at '{json_pointer}'.",
                )
                continue

            prop_pointer = f"{json_pointer}/properties/{prop_name}"
            is_optional = prop_name not in required_props
            try:
                # Recursively parse property schema
                prop_type_info = self._parse_schema_to_type_info(
                    prop_schema,
                    prop_pointer,
                    is_property_optional=is_optional,  # Pass optionality context
                )

                # Sanitize property name for BAML (camelCase)
                baml_prop_name = self._sanitize_name(prop_name, capitalize=False)
                alias = prop_name if baml_prop_name != prop_name else None

                field = BamlFieldModel(
                    name=baml_prop_name,
                    type_info=prop_type_info,
                    description=prop_schema.get("description"),
                    alias=alias,
                )
                properties.append(field)
            except (
                InvalidRefError,
                CircularRefError,
                UnexpectedTypeError,
                RefResolutionError,
                TypeError,
                ValueError,
            ) as e:
                # Catch circular refs or other parsing errors for a property
                warnings.warn(
                    f"Skipping property '{prop_name}' in class '{class_name}' at '{prop_pointer}' due to error: {e}",
                    stacklevel=2,
                )
                # Decide if you want to add a placeholder field (e.g., type 'any') or just skip
                # Skipping for now.

        # Create and store the final model, replacing the placeholder
        original_title = schema.get("title")
        class_model = BamlClassModel(
            name=class_name,
            properties=properties,
            description=schema.get("description"),
            # Add alias only if sanitization changed the original title
            alias=(
                original_title
                if isinstance(original_title, str)
                and self._sanitize_name(original_title, capitalize=True) != class_name
                else None
            ),
            # is_dynamic = ? # Could check for additionalProperties: true maybe
        )
        self._definitions[class_name] = class_model

        # Return type info referencing the newly created class
        return BamlTypeInfo(base_type=BamlBaseType.CLASS, custom_type_name=class_name)

    def _parse_enum_schema(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        values: list[str | None],
    ) -> BamlTypeInfo:
        """
        Parses a schema with string 'enum' values into a BamlEnumModel.
        Handles caching and value sanitization. Allows None in the input list
        which contributes to optionality but isn't a BAML enum value itself.
        """
        enum_name = self._get_or_create_model_name(schema, json_pointer, "Enum")

        # Check cache/placeholder first
        if enum_name in self._definitions:
            existing = self._definitions[enum_name]
            if isinstance(existing, (BamlEnumModel, _RefPlaceholder)):
                return BamlTypeInfo(
                    base_type=BamlBaseType.ENUM,
                    custom_type_name=enum_name,
                )
            if isinstance(existing, BamlClassModel):
                raise NameCollisionError(
                    f"Name collision: Schema at '{json_pointer}' tries to define enum '{enum_name}' but a class with this name already exists.",
                )
            # Should not happen
            raise UnexpectedTypeError(
                f"Unexpected type in definitions map for key '{enum_name}': {type(existing)}",
            )

        # Add placeholder
        self._definitions[enum_name] = _RefPlaceholder(json_pointer)

        enum_values_models: list[BamlEnumValueModel] = []
        has_null = False
        valid_string_values = (
            set()
        )  # Track unique string values after potential None filtering

        for val in values:
            if val is None:
                has_null = True
                continue  # Null contributes to optionality, not an enum value

            if not isinstance(val, str):
                warnings.warn(
                    f"Ignoring non-string value '{val}' in enum '{enum_name}' at '{json_pointer}'.",
                )
                continue

            if val in valid_string_values:
                warnings.warn(
                    f"Duplicate enum value '{val}' found in schema for '{enum_name}' at '{json_pointer}'. Using first occurrence.",
                )
                continue
            valid_string_values.add(val)

            # Sanitize enum value name for BAML (PascalCase or UPPER_SNAKE_CASE?)
            # Let's stick to PascalCase for consistency with type names.
            baml_val_name = self._sanitize_name(val, capitalize=True)

            # Handle potential collisions after sanitization (e.g., "my-value" and "MyValue" -> MyValue)
            # This simple check doesn't fully resolve, just warns. A robust solution might append numbers.
            if any(evm.name == baml_val_name for evm in enum_values_models):
                warnings.warn(
                    f"Enum value sanitization collision for '{val}' resulting in duplicate name '{baml_val_name}' in enum '{enum_name}'. Check BAML output.",
                )
                # Consider appending a number or using a different strategy if this is common

            alias = val if baml_val_name != val else None
            # Consider for future improvement: Look for richer enum descriptions if available in schema extensions?
            enum_values_models.append(
                BamlEnumValueModel(name=baml_val_name, alias=alias),
            )

        # Create and store the final model
        original_title = schema.get("title")
        enum_model = BamlEnumModel(
            name=enum_name,
            values=enum_values_models,
            description=schema.get("description"),
            alias=(
                original_title
                if isinstance(original_title, str)
                and self._sanitize_name(original_title, capitalize=True) != enum_name
                else None
            ),
        )
        self._definitions[enum_name] = enum_model

        # Return type info. If null was present, mark this type info as optional.
        return BamlTypeInfo(
            base_type=BamlBaseType.ENUM,
            custom_type_name=enum_name,
            is_optional=has_null,  # Optionality derived *directly* from presence of null in enum list
        )

    def _create_union_or_optional_type(
        self,
        options: list[BamlTypeInfo],
        *,
        is_context_optional: bool,
    ) -> BamlTypeInfo:
        """
        Simplifies a list of BamlTypeInfo options (from anyOf, oneOf, type array)
        into a single BamlTypeInfo, handling null extraction for optionality and
        simplifying single-type unions.

        Args:
            options: List of BamlTypeInfo objects representing the union members.
            is_context_optional: Whether the union itself is optional due to parent schema context.

        Returns:
            A simplified BamlTypeInfo representing the union or optional type.

        """
        # Filter out any explicit 'null' types and track if null was present
        has_null_type = any(opt.base_type == BamlBaseType.NULL for opt in options)
        # Also consider if any option *itself* became optional (e.g., an enum with null)
        # Using `is_inherently_optional = any(opt.is_optional for opt in options)`` might be too broad? Let's stick to explicit null type for now.

        non_null_options = [
            opt for opt in options if opt.base_type != BamlBaseType.NULL
        ]

        # Determine final optionality: true if context requires it OR if 'null' was one of the types.
        is_final_optional = is_context_optional or has_null_type

        if not non_null_options:
            # Only null was present, or empty union. Result is effectively 'null'.
            # If context made it optional, it's 'null?' which is still just 'null'.
            return BamlTypeInfo(
                base_type=BamlBaseType.NULL,
                is_optional=True,
            )  # Represent as optional null

        if len(non_null_options) == 1:
            # Single type remains after removing null. Apply the final optionality flag.
            final_type = non_null_options[0]
            # Preserve existing optionality on the type if it was already optional for other reasons,
            # OR make it optional if the union context dictates.
            final_type.is_optional = final_type.is_optional or is_final_optional
            return final_type
        # Multiple non-null types remain -> create a Union type.
        # The Union *itself* carries the optionality flag.
        # We might need to simplify nested unions or make member types non-optional within the union string?
        # For now, keep it simple: list the non-null types.
        # Ensure constituent types within the union list don't redundantly carry the optional flag
        # if the optionality comes *only* from the null type being present.

        # If the overall union is optional *because* of null,
        # individual members shouldn't also be marked optional unless they inherently are.
        # This is complex. Let BamlTypeInfo.get_effective_type_str handle display logic.
        # We just store the resolved types.
        simplified_union_types = non_null_options.copy()

        return BamlTypeInfo(
            base_type=BamlBaseType.UNION,
            union_types=simplified_union_types,
            is_optional=is_final_optional,  # Union wrapper is optional if needed
        )

    # --- Utility Helpers ---

    def _navigate_pointer(self, root: Any, path_parts: list[str]) -> dict[str, Any]:
        current = root
        for raw_part in path_parts:
            # Unescape per JSON Pointer spec (do NOT overwrite the original part variable)
            unescaped_part = raw_part.replace("~1", "/").replace("~0", "~")
            if isinstance(current, dict):
                if unescaped_part not in current:
                    raise PathNavigationError(
                        f"Key {unescaped_part!r} not found in object",
                    )
                current = current[unescaped_part]
            elif isinstance(current, list):
                try:
                    idx = int(unescaped_part)
                except ValueError as e:
                    raise PathNavigationError(
                        f"Invalid list index format: {unescaped_part!r}",
                    ) from e
                if not 0 <= idx < len(current):
                    raise PathNavigationError(f"List index out of range: {idx}")
                current = current[idx]
            else:
                raise PathNavigationError(
                    f"Cannot navigate into {type(current).__name__!r} at segment {unescaped_part!r}",
                )
        if not isinstance(current, dict):
            raise UnexpectedTypeError(
                f"Resolved $ref does not point to a dict, got {type(current).__name__}",
            )
        return current

    def _resolve_ref(self, ref: str, current_pointer: str) -> dict[str, Any]:
        """
        Resolves a local JSON Pointer reference (`#/path/to/definition`).

        Args:
            ref: The JSON Pointer string (e.g., "#/$defs/Address").
            current_pointer: The JSON pointer of the schema currently being processed (for error context).

        Returns:
            The resolved schema part (as a dictionary).

        Raises:
            RefResolutionError: If the ref format is invalid, points outside the schema, or cannot be resolved.

        """
        if not ref.startswith("#/"):
            # Allow internal refs like '#' (self-reference)
            if ref == "#":
                return self._root_schema

            raise InvalidRefError(
                f"Unsupported $ref format at '{current_pointer}': '{ref}'. "
                "Only local root references (starting with '#/') are supported.",
            )

        path_parts = ref[2:].split("/")
        try:
            return self._navigate_pointer(self._root_schema, path_parts)
        except (PathNavigationError, UnexpectedTypeError) as e:
            raise RefResolutionError(
                f"Failed to resolve $ref '{ref}' encountered at '{current_pointer}': {e}",
            ) from e

    def _get_or_create_model_name(
        self,
        schema: dict[str, Any],
        json_pointer: str,
        type_kind: str,  # "Class" or "Enum"
        forced_name: str | None = None,
    ) -> str:
        """
        Determines the BAML name for a class or enum based on schema title,
        forced name, or context. Ensures the name is sanitized and unique.

        Args:
            schema: The schema dictionary for the class/enum.
            json_pointer: JSON pointer path to this schema, used for context/fallback naming.
            type_kind: Either "Class" or "Enum" for naming anonymous types.
            forced_name: If provided, use this sanitized name directly.

        Returns:
            A unique, sanitized BAML name (PascalCase).

        """
        name: str
        if forced_name:
            # Use the forced name (typically for the root object)
            name = self._sanitize_name(forced_name, capitalize=True)
        else:
            # Try schema title first
            title = schema.get("title")
            if title and isinstance(title, str):
                name = self._sanitize_name(title, capitalize=True)
            else:
                # Attempt to derive name from JSON pointer structure
                parts = json_pointer.strip("#/").split("/")
                # Filter out generic structural parts to find meaningful name components
                meaningful_parts = [
                    p
                    for p in parts
                    if p
                    not in (
                        "properties",
                        "items",
                        "$defs",
                        "definitions",
                        "anyOf",
                        "oneOf",
                        "type",
                    )
                    and not p.isdigit()
                ]
                if meaningful_parts:
                    # Use last meaningful part, e.g., #/$defs/User -> User, #/properties/address -> Address
                    derived_name = meaningful_parts[-1]
                    # Check if it looks like a property name (likely camelCase) and PascalCase it
                    if derived_name and derived_name[0].islower():
                        name = self._sanitize_name(derived_name, capitalize=True)
                    elif derived_name:
                        name = self._sanitize_name(
                            derived_name,
                            capitalize=True,
                        )  # Already likely Pascal or needs sanitizing
                    else:  # Meaningful part was empty after filtering? Fallback.
                        name = ""  # Handled by fallback below
                else:
                    name = ""  # No meaningful parts found

                # Fallback to anonymous naming if no title or derived name
                if not name:
                    self._anonymous_type_counter += 1
                    name = f"Anonymous{type_kind}{self._anonymous_type_counter}"
                    warnings.warn(
                        f"Assigning anonymous name '{name}' to schema at '{json_pointer}' lacking a title or clear pointer context.",
                    )

        # Ensure name uniqueness across all definitions
        original_name = name
        count = 1
        while name in self._definitions:
            existing = self._definitions[name]
            # If we encounter a placeholder for the *same* name we are trying to define,
            # it means we are resolving a reference *to* this schema being defined. Return the name.
            if isinstance(existing, _RefPlaceholder):
                # Ensure the placeholder corresponds to *this* schema definition attempt, not an unrelated one
                # This check is tricky. Assume if name matches placeholder, it's the recursive case.
                return name
            if isinstance(existing, (BamlClassModel, BamlEnumModel)):
                # Simple name collision (e.g. two schemas with same title/derived name), append counter
                count += 1
                name = f"{original_name}{count}"
                warnings.warn(
                    f"Name collision detected for '{original_name}'. Renaming to '{name}' for schema at '{json_pointer}'.",
                )
            else:  # Should not happen
                raise UnexpectedTypeError(
                    f"Unexpected type in definitions map for key '{name}': {type(existing)}",
                )

        return name

    @staticmethod
    def _sanitize_name(name: str, *, capitalize: bool = False) -> str:
        """
        Converts a string to a valid BAML identifier (PascalCase for types, camelCase for fields).
        Handles common separators and invalid characters.
        """
        if not name:
            return "Unnamed"  # Or raise error?

        # Replace common separators and invalid characters with underscores
        name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

        # Split by underscore or camelCase transitions
        words = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z]|$)", name)

        if not words:
            # Handle cases like "__" or numeric inputs becoming empty
            return (
                f"InvalidName{name}"
                if not capitalize
                else f"InvalidName{name.capitalize()}"
            )

        if capitalize:  # PascalCase for types (classes, enums)
            return "".join(word.capitalize() for word in words)
        # camelCase for fields/properties
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])


class _RefPlaceholder:
    """Sentinel object used to detect circular references during parsing."""

    def __init__(self, ref: str):
        self.ref = ref


class JsonSchemaToBamlModelError(Exception):
    """Base exception for errors in JsonSchemaToBamlModelConverter."""


class PathNavigationError(JsonSchemaToBamlModelError):
    """Raised when navigation through a JSON pointer path fails due to an unexpected node type."""


class InvalidRefError(JsonSchemaToBamlModelError):
    """Raised when a $ref is invalid."""


class CircularRefError(JsonSchemaToBamlModelError):
    """Raised when a circular $ref is detected."""


class NameCollisionError(JsonSchemaToBamlModelError):
    """Raised when a name collision occurs in model definitions."""


class UnexpectedTypeError(JsonSchemaToBamlModelError):
    """Raised when an unexpected type is encountered in definitions."""


class RefResolutionError(JsonSchemaToBamlModelError):
    """Raised when a $ref cannot be resolved."""

