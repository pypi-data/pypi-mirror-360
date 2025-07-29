#!/usr/bin/env -S uv run
import argparse
import re
import subprocess
import sys
import traceback
from pathlib import Path

# Regex to find the simple version pattern
# (version\s*") : Group 1 (literal 'version "')
# ([^"]+)       : Group 2 (the current version string)
# (")           : Group 3 (the closing quote)
VERSION_PATTERN = re.compile(r'(version\s*")([^"]+)(")')

# Regex to check if a line starts a generator block
# \s*           : Optional leading whitespace
# generator     : Literal keyword
# \s+           : One or more whitespace chars
# [\w\d_-]+     : The generator name (alphanumeric, underscore, hyphen)
# \s*           : Optional whitespace before {
# \{            : The opening brace
# \s*$          : Optional trailing whitespace until end of line
GENERATOR_BLOCK_START_PATTERN = re.compile(r"^\s*generator\s+[\w\d_-]+\s*\{\s*$")


def update_version_in_file(*, file_path: Path, new_version: str, verbose: bool) -> bool:
    """
    Reads a file, finds 'version "YYY"' lines ONLY within generator blocks,
    replaces YYY with new_version, and writes the file back if changed.

    Args:
        file_path (Path): The path to the .baml file.
        new_version (str): The new version string to set.
        verbose (bool): Whether to print detailed output.

    Return:
        bool: True if the file was modified, False otherwise.

    """
    try:
        if verbose:
            print(f"Processing: {file_path}")
        original_content = file_path.read_text(encoding="utf-8")

        modified_content = original_content
        modification_made = False
        matches_found_count = 0
        matches_replaced_in_generator = 0

        def replace_if_in_generator_block(match):
            nonlocal modification_made, matches_found_count, matches_replaced_in_generator
            matches_found_count += 1

            old_version = match.group(2)
            if old_version == new_version:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match.start()}, already matches target. Skipping."
                    )
                return match.group(0)

            match_start_index = match.start()
            last_open_brace_index = original_content.rfind("{", 0, match_start_index)
            last_close_brace_index = original_content.rfind("}", 0, match_start_index)

            if last_open_brace_index == -1:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index}, but no preceding '{{'. Skipping."
                    )
                return match.group(0)

            if last_close_brace_index > last_open_brace_index:
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index}, but last relevant block closed @ pos {last_close_brace_index}. Skipping."
                    )
                return match.group(0)

            block_header_start_index = (
                original_content.rfind("\n", 0, last_open_brace_index) + 1
            )
            block_header_line_end = original_content.find(
                "\n", block_header_start_index
            )
            if block_header_line_end == -1:
                block_header_line_end = len(original_content)

            block_header_line_content = original_content[
                block_header_start_index : last_open_brace_index + 1
            ].strip()

            if GENERATOR_BLOCK_START_PATTERN.match(block_header_line_content):
                if verbose:
                    print(
                        f"  - Found version '{old_version}' @ pos {match_start_index} inside a generator block. Replacing with '{new_version}'."
                    )
                modification_made = True
                matches_replaced_in_generator += 1
                return f"{match.group(1)}{new_version}{match.group(3)}"

            if verbose:
                print(
                    f"  - Found version '{old_version}' @ pos {match_start_index}, but not in a 'generator' block (header line segment: '{block_header_line_content}'). Skipping."
                )
            return match.group(0)

        modified_content = VERSION_PATTERN.sub(
            replace_if_in_generator_block, original_content
        )

        if modification_made:
            if verbose:
                print(f"  Updating file '{file_path}'...")
            file_path.write_text(modified_content, encoding="utf-8")
            if verbose:
                print(f"  Successfully updated: {file_path}")
            return True

        if matches_found_count > 0:
            if verbose:
                if matches_replaced_in_generator == 0:
                    print(
                        f"  Found {matches_found_count} 'version \"...\"' pattern(s), but none required updates in generator blocks or they already matched."
                    )
            return False
        else:
            if verbose:
                print(f"  No 'version \"...\"' pattern found at all in {file_path}.")
            return False

    except FileNotFoundError:
        if verbose:
            print(f"  Error: File not found: {file_path}", file=sys.stderr)
        return False
    except PermissionError:
        if verbose:
            print(f"  Error: Permission denied for file: {file_path}", file=sys.stderr)
        return False
    except Exception as e:
        if verbose:
            print(
                f"  An unexpected error occurred processing {file_path}: {e}",
                file=sys.stderr,
            )
            traceback.print_exc()
        return False


def update_baml_generator_versions():
    parser = argparse.ArgumentParser(
        description="Recursively find 'baml_src' folders and update the version string "
        "in 'version \"...\"' lines ONLY within 'generator ... {}' blocks inside .baml files."
    )
    parser.add_argument(
        "--search-root-path",
        required=False,
        default=str(Path.cwd()),
        help="The root folder path to search within. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--target-version",
        required=False,
        help="The new version string (e.g., '0.123.0'). Defaults to the installed baml-py version.",
    )
    parser.add_argument(
        "--verbose",
        required=False,
        choices=["true", "false"],
        default="false",
        help="Set to 'true' for detailed output, 'false' for summary only.",
    )

    args = parser.parse_args()

    if args.target_version is None:
        try:
            # Use a more descriptive variable name for the subprocess result
            installed_version_process = subprocess.run(
                ["uv", "pip", "list"],  # noqa: S607
                capture_output=True,
                text=True,
                check=True,
            )
            baml_py_version = next(
                (
                    line.split()[1]
                    for line in installed_version_process.stdout.splitlines()
                    if "baml-py" in line
                ),
                None,
            )
            if baml_py_version is None:
                print(
                    "Error: baml-py version not found in 'uv pip list' output.",
                    file=sys.stderr,
                )
                sys.exit(1)
            new_version = baml_py_version
        except FileNotFoundError:
            print(
                "Error: 'uv' command not found. Is it installed and in your PATH?",
                file=sys.stderr,
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error running 'uv pip list': {e}", file=sys.stderr)
            if e.stderr:
                print(f"Stderr: {e.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
    else:
        new_version = str(args.target_version)

    new_version = new_version.replace('"', "").replace("'", "").strip()

    root_folder = Path(args.search_root_path)
    verbose = args.verbose.lower() == "true"

    if not root_folder.is_dir():
        print(
            f"Error: Folder not found or is not a directory: {root_folder}",
            file=sys.stderr,
        )
        sys.exit(1)

    if verbose:
        print(f"Starting search in: {root_folder}")
        print(f"Target version: {new_version}")
        print("-" * 30)

    # --- MODIFIED FILE DISCOVERY LOGIC ---
    found_any_baml_src_dir = False
    updated_files_count = 0
    processed_at_least_one_baml_file = (
        False  # Tracks if any .baml file was encountered and processed
    )

    # Iterate over all directories named 'baml_src' recursively under root_folder
    for baml_src_dir_path in root_folder.rglob("baml_src"):
        if not baml_src_dir_path.is_dir():
            # rglob("baml_src") can match files as well as directories. Skip non-directories.
            if verbose:
                print(
                    f"  Skipping non-directory path named 'baml_src': {baml_src_dir_path}"
                )
            continue

        # At this point, baml_src_dir_path is a directory named 'baml_src'
        if not found_any_baml_src_dir:
            found_any_baml_src_dir = True

        if verbose:
            # This message will print for each 'baml_src' directory found
            print(f"\n--- Scanning baml_src directory: {baml_src_dir_path} ---")

        baml_files_found_in_this_baml_src = 0
        # Now, find all .baml files recursively within this baml_src_dir_path
        for baml_file_path in baml_src_dir_path.rglob("*.baml"):
            # rglob for *.baml should yield files, but an explicit check is safe practice.
            if baml_file_path.is_file():
                baml_files_found_in_this_baml_src += 1
                if not processed_at_least_one_baml_file:
                    processed_at_least_one_baml_file = True

                # update_version_in_file handles its own "Processing: {file_path}" if verbose
                if update_version_in_file(
                    file_path=baml_file_path, new_version=new_version, verbose=verbose
                ):
                    updated_files_count += 1

        if verbose and baml_files_found_in_this_baml_src == 0:
            print(f"  No .baml files found within {baml_src_dir_path}")

    # Separator before final summary, only if verbose and we actually did baml_src dir processing
    if (
        verbose and found_any_baml_src_dir
    ):  # Check if any baml_src dir processing occurred
        print("-" * 30)

    # Refined final summary messages
    if not found_any_baml_src_dir:
        print("Warning: No directories named 'baml_src' were found.")
    elif (
        not processed_at_least_one_baml_file
    ):  # baml_src dir(s) found, but no .baml files in any of them
        print(
            "Info: Found 'baml_src' director(y/ies), but they contained no .baml files."
        )
    elif (
        updated_files_count == 0
    ):  # .baml files were processed, but none were actually changed
        print(
            "Finished: Processed .baml files in 'baml_src' director(y/ies), but no files required updates (e.g., versions already matched)."
        )
    else:  # At least one file was updated
        print(f"Finished: Successfully updated {updated_files_count} file(s).")
    # --- END OF MODIFIED FILE DISCOVERY LOGIC ---


if __name__ == "__main__":
    update_baml_generator_versions()
