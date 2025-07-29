import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BamlBaseType(Enum):
    """Core BAML primitive or structural types."""

    BOOL = "bool"
    STR = "string"
    INT = "int"
    FLOAT = "float"
    LIST = "list"  # Represents the concept of a list, actual type info combined
    DICT = "dict"  # Should likely map to CLASS for structured dicts
    NULL = "null"  # Explicitly represent null type
    ANY = "any"  # Fallback or for complex unions
    # Structural types - details captured elsewhere
    CLASS = "class"
    ENUM = "enum"
    # Meta types - used during processing
    UNION = "union"  # Represents a union of other types
    # BAML-specific types
    LITERAL_STRING = "literal_string"
    LITERAL_INT = "literal_int"
    LITERAL_BOOL = "literal_bool"


@dataclass
class BamlTypeInfo:
    """Represents detailed type information for a BAML field or array item."""

    base_type: BamlBaseType
    # For lists/arrays: information about the items
    item_type: Optional["BamlTypeInfo"] = None
    # For unions: the possible types
    union_types: list["BamlTypeInfo"] = field(default_factory=list)
    # For classes/enums: the name defined in the BAML model registry
    custom_type_name: str | None = None
    # Optionality - derived from schema context (required list or explicit null type)
    is_optional: bool = False
    # For literal types, the value itself
    literal_string: str | None = None
    literal_bool: bool | None = None
    literal_int: int | None = None

    def __post_init__(self):
        # Basic validation / canonical representation
        if self.base_type == BamlBaseType.UNION and not self.union_types:
            raise ValueError("Union type must have union_types specified")
        if self.base_type != BamlBaseType.UNION and self.union_types:
            warnings.warn(
                f"Non-union type {self.base_type} has union_types specified; ignoring.",
            )
            self.union_types = []
        if (
            self.base_type not in (BamlBaseType.CLASS, BamlBaseType.ENUM)
            and self.custom_type_name
        ):
            warnings.warn(
                f"Non-class/enum type {self.base_type} has custom_type_name specified; ignoring.",
            )
            self.custom_type_name = None
        if (
            self.base_type != BamlBaseType.UNION
            and not self.item_type
            and len(self.get_effective_type_str().split("[]")) > 1
        ):
            # Inferring item_type from type string like int[] - potentially needed if constructed manually
            pass  # Or implement parsing logic if needed

    def get_effective_type_str(self) -> str:
        """Helper to get a BAML-like type string representation."""
        if self.base_type in (BamlBaseType.CLASS, BamlBaseType.ENUM):
            base = self.custom_type_name or "UnnamedCustomType"
        elif self.base_type == BamlBaseType.UNION:
            # Simple union representation (might need refinement for BAML syntax)
            base = "|".join(t.get_effective_type_str() for t in self.union_types)
        elif self.base_type == BamlBaseType.ANY:
            base = "any"  # Map BamlBaseType.ANY to 'any' string
        elif self.base_type == BamlBaseType.LITERAL_INT:
            base = str(self.literal_int)
        elif self.base_type == BamlBaseType.LITERAL_BOOL:
            base = "true" if self.literal_bool else "false"
        elif self.base_type == BamlBaseType.LITERAL_STRING:
            base = f'"{self.literal_string}"'
        else:
            base = self.base_type.value

        if self.item_type:  # Implies this BamlTypeInfo itself represents a list
            item_str = self.item_type.get_effective_type_str()
            # Avoid double optional marker like string?[]?
            if self.item_type.is_optional and self.is_optional:
                return f"{item_str}[]"
            if self.item_type.is_optional and not self.is_optional:
                return f"{item_str}[]"  # Optionality applies to item, not list itself typically
            base = f"{item_str}[]"

        # Add optional marker '?' if needed, but not if it's already part of a union component string
        # And avoid adding '?' to list types like 'string[]?' - optionality usually on items
        if (
            self.is_optional
            and not self.item_type
            and "?" not in base
            and "|" not in base
            and base != BamlBaseType.NULL.value
        ):
            return f"{base}?"
        return base

    @classmethod
    def from_string(cls, type_str: str) -> "BamlTypeInfo":
        """Crude parser to create BamlTypeInfo from a string like 'string[]?'."""
        is_optional = type_str.endswith("?")
        if is_optional:
            type_str = type_str[:-1]

        is_list = type_str.endswith("[]")
        if is_list:
            item_type_str = type_str[:-2]
            item_type = cls.from_string(item_type_str)  # Recursive call for item type
            return cls(
                base_type=BamlBaseType.LIST,
                item_type=item_type,
                is_optional=is_optional,
            )

        if "|" in type_str:
            parts = type_str.split("|")
            union_types = [cls.from_string(part) for part in parts]
            # If 'null' is one of the union types, mark the overall union as optional
            # and remove the null type from the list if other types exist.
            has_null = any(ut.base_type == BamlBaseType.NULL for ut in union_types)
            if has_null and len(union_types) > 1:
                is_optional = True
                union_types = [
                    ut for ut in union_types if ut.base_type != BamlBaseType.NULL
                ]
                if len(union_types) == 1:  # Simplified back to single optional type
                    single_type = union_types[0]
                    single_type.is_optional = True
                    return single_type

            return cls(
                base_type=BamlBaseType.UNION,
                union_types=union_types,
                is_optional=is_optional,
            )

        try:
            # Try matching basic types
            base_type = BamlBaseType(type_str)
            return cls(base_type=base_type, is_optional=is_optional)
        except ValueError:
            # Assume it's a custom class/enum name
            return cls(
                base_type=BamlBaseType.CLASS,
                custom_type_name=type_str,
                is_optional=is_optional,
            )


@dataclass
class BamlFieldModel:
    """Represents a field/property of a BAML class."""

    name: str  # The BAML field name (potentially sanitized)
    type_info: BamlTypeInfo
    description: str | None = None
    alias: str | None = None  # The original JSON schema property name if different
    skip: bool = False


@dataclass
class BamlEnumValueModel:
    """Represents a value/member of a BAML enum."""

    name: str  # The BAML enum value name (potentially sanitized)
    description: str | None = None
    alias: str | None = None  # The original JSON schema enum value if different
    skip: bool = False


@dataclass
class BamlClassModel:
    """Represents a BAML class with fields."""

    name: str  # The BAML class name (potentially sanitized)
    properties: list[BamlFieldModel]
    description: str | None = None
    alias: str | None = None  # The original JSON schema title if different
    is_dynamic: bool = False  # Default to False unless schema indicates otherwise


@dataclass
class BamlEnumModel:
    """Represents a BAML enum with values."""

    name: str  # The BAML enum name (potentially sanitized)
    values: list[BamlEnumValueModel]
    description: str | None = None
    alias: str | None = None  # The original JSON schema title if different
    is_dynamic: bool = False  # Enums are typically not dynamic

