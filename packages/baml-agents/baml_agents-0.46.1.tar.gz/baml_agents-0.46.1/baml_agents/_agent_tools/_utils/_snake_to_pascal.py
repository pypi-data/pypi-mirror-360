def snake_to_pascal(name: str) -> str:
    name = pascal_to_snake(name)
    """Convert snake_case or kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in name.replace("-", "_").split("_"))


def pascal_to_snake(name: str) -> str:
    """
    Convert PascalCase or camelCase to snake_case.
    """
    name = name.replace(" ", "_")
    if not name:
        return ""
    chars = []
    for i, c in enumerate(name):
        if (
            c.isupper()
            and i != 0
            and (
                not name[i - 1].isupper()
                or (i + 1 < len(name) and not name[i + 1].isupper())
            )
        ):
            chars.append("_")
        chars.append(c.lower())
    return "".join(chars)

