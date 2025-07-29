#!/usr/bin/env -S uv run


import subprocess
from pathlib import Path

from baml_agents._agent_tools._utils._baml_utils import display_prompt
from baml_agents._baml_clients._with_model import with_model


def _input_multiline_message(
    msg: str,
):
    print(msg)
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _get_git_diff():
    result = subprocess.run(
        ["git", "diff", "--staged", "--ignore-all-space"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    )
    filtered_diff = "\n".join(
        line
        for line in result.stdout.splitlines()
        if not line.startswith("index") and not line.startswith("@@")
    )
    formatted_diff = filtered_diff.replace("{{", "{").replace("}}", "}")
    return formatted_diff


def _generate_baml_client(working_dir: Path):
    subprocess.run(
        ["uvx", "--from", "baml-py", "baml-cli", "generate"],  # noqa: S607
        cwd=working_dir,
        check=True,
    )


def generate_commit_message():
    import argparse

    def parse_arguments():
        parser = argparse.ArgumentParser(description="Generate a commit message.")
        parser.add_argument(
            "--model",
            type=str,
            required=False,
            default=None,
            help="Specify the model to use for generating the commit message.",
        )
        return parser.parse_args()

    args = parse_arguments()
    model = args.model

    git_diff = _get_git_diff()

    high_level_context = _input_multiline_message(
        "Enter high level context for this commit (end with an empty line):"
    )
    if not high_level_context:
        print("\n# No high level context provided.")

    working_dir = Path(__file__).parent
    _generate_baml_client(working_dir)
    from .baml_client.sync_client import b

    if model:
        b = with_model(b, model=model)
    request = b.request.GenerateCommitMessage(
        git_diff=git_diff,
        high_level_context=high_level_context,
    )
    display_prompt(request)
    result = b.GenerateCommitMessage(
        git_diff=git_diff,
        high_level_context=high_level_context,
    )
    import pyperclip

    pyperclip.copy(f'git commit -m "{result.conventional_commit_message}"')
    print()
    for key, value in result.model_dump().items():
        if key == "conventional_commit_message":
            continue
        print(f"# {key}:\n\n{value}\n")
    print("\n# Commit Message:\n", result.conventional_commit_message)


if __name__ == "__main__":
    generate_commit_message()
