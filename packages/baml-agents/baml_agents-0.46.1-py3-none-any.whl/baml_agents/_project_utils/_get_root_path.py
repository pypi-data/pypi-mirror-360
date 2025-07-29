import pathlib


def get_root_path(*, start_path=None):
    if start_path is None:
        start_path = pathlib.Path.cwd().resolve()
    else:
        start_path = pathlib.Path(start_path).resolve()

    root_path = next(
        (
            str(p)
            for p in [start_path, *list(start_path.parents)]
            if (p / "pyproject.toml").is_file()
        ),
        None,
    )
    if root_path is None:
        raise FileNotFoundError(
            "Could not find pyproject.toml in the specified or parent directories"
        )
    return root_path
