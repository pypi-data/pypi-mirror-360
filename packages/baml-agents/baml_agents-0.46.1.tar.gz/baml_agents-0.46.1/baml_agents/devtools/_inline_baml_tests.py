#!/usr/bin/env -S uv run

import argparse
import sys
import traceback
from pathlib import Path

import regex as re

# Regex to find a test block. Captures:
# Group 1: test header (e.g., "test MyTestName {")
# Group 2: test name (e.g., "MyTestName")
# Group 3: content inside the test block's main braces (recursive)
# Group 4: test footer (closing brace, e.g., "}")
TEST_BLOCK_PATTERN = re.compile(
    r"^(^\s*test\s+([\w\d_-]+)\s*\{)"  # Group 1 (header), Group 2 (name)
    r"((?:[^{}]|\{(?3)\})*)"  # Group 3 (content, handles balanced braces)
    r"(^\s*\})",  # Group 4 (closing brace)
    re.VERBOSE | re.MULTILINE | re.DOTALL,
)

# Regex to find an args block within a test block's content. Captures:
# Group 1: args header (e.g., "args {")
# Group 2: content inside the args block's braces (recursive)
# Group 3: args footer (closing brace, e.g., "}")
ARGS_BLOCK_PATTERN = re.compile(
    r"(\bargs\s*\{)"  # Group 1 (header)
    r"((?:[^{}]|\{(?2)\})*)"  # Group 2 (content, handles balanced braces)
    r"(\})",  # Group 3 (closing brace)
    re.VERBOSE | re.DOTALL,
)

# Regex for the specific file input pattern: arg_name { file "path/to/file.ext" }
# It captures:
# Group 1: arg_name (e.g., "input_csv")
# Group 2: Double-quoted path (e.g., "./data.csv")
# Group 3: Single-quoted path
# Group 4: Unquoted path
FILE_INPUT_PATTERN = re.compile(
    r"""
    (\b[\w\d_-]+\b)  # Group 1: arg_name
    \s*
    (?:               # Non-capturing group for the whole { file ... } structure
        \{
        \s*
        file
        \s+
        (?:           # Non-capturing group for path alternatives
            "([^"]*)"    # Group 2: Double-quoted path
            |
            '([^']*)'    # Group 3: Single-quoted path
            |
            ([^#\"'\s][^\s,}]*) # Group 4: Unquoted path (cannot start with #, ", ' or whitespace; cannot contain whitespace, ,, })
        )
        \s*
        \}
    )
    """,
    re.VERBOSE,
)


def make_baml_string_literal(content: str) -> str:
    """Creates a BAML string literal, using #"..."# syntax, handling internal #", "# etc."""
    if not content:
        return '#""#'  # BAML representation of an empty string

    num_hashes = 1
    # Increment hashes if the chosen delimiter would conflict with the content
    while f'{"#" * num_hashes}"' in content or f'"{"#" * num_hashes}' in content:
        num_hashes += 1

    hashes = "#" * num_hashes
    return f'{hashes}"{content}"{hashes}'


def _process_one_args_block_inner_content(
    args_inner_content: str, baml_file_path: Path, test_name: str, *, verbose: bool
) -> tuple[str, bool]:  # Returns (modified_content, was_modified)
    """Helper to process the inner content of a single args block."""
    current_args_block_modified = False

    def file_replacer_func(file_input_match_obj):
        nonlocal current_args_block_modified
        arg_name = file_input_match_obj.group(1)

        relative_file_path_str = (
            file_input_match_obj.group(2)  # Double-quoted
            or file_input_match_obj.group(3)  # Single-quoted
            or file_input_match_obj.group(4)  # Unquoted
        )

        if not relative_file_path_str:
            if verbose:
                print(
                    f"      Warning: Could not extract file path for arg '{arg_name}' in test '{test_name}' of {baml_file_path}. Match: {file_input_match_obj.group(0)}",
                    file=sys.stderr,
                )
            return file_input_match_obj.group(0)

        data_file_path = baml_file_path.parent / relative_file_path_str.strip()
        if verbose:
            print(
                f"      Found file reference for '{arg_name}' in test '{test_name}': '{data_file_path}' (original relative: '{relative_file_path_str.strip()}')",
                file=sys.stderr,
            )

        try:
            file_content = data_file_path.read_text(encoding="utf-8")
            baml_string = make_baml_string_literal(file_content)
            replacement = f"{arg_name} {baml_string}"
            current_args_block_modified = True
            if verbose:
                print(
                    f"        Inlined content for '{arg_name}'. Original: '{file_input_match_obj.group(0)}', New: '{replacement[:50]}...'",
                    file=sys.stderr,
                )
            return replacement
        except FileNotFoundError:
            if verbose:
                print(
                    f"      Error: Data file not found for arg '{arg_name}' in test '{test_name}': {data_file_path}",
                    file=sys.stderr,
                )
        except Exception as e:
            if verbose:
                print(
                    f"      Error reading or processing data file for arg '{arg_name}' in test '{test_name}' ({data_file_path}): {e}",
                    file=sys.stderr,
                )
                traceback.print_exc(file=sys.stderr)
        return file_input_match_obj.group(0)  # Return original on error

    modified_args_inner_content = FILE_INPUT_PATTERN.sub(
        file_replacer_func, args_inner_content
    )
    return modified_args_inner_content, current_args_block_modified


def process_baml_file_content(
    content: str,
    baml_file_path: Path,
    *,
    verbose: bool,
    test_name_prefix: str,
    test_name_suffix: str,
) -> list[str]:
    """
    Processes BAML content to inline file references in test args.
    Returns a list of strings, where each string is a fully reconstructed
    test block that had its content modified (inlined) and name changed.
    """
    collected_modified_test_blocks = []

    for test_match_obj in TEST_BLOCK_PATTERN.finditer(content):
        original_test_header = test_match_obj.group(1)
        original_test_name = test_match_obj.group(2)
        test_inner_content = test_match_obj.group(3)
        test_footer = test_match_obj.group(4)

        if verbose:
            print(f"  Processing test block: {original_test_name}", file=sys.stderr)

        current_test_block_was_modified = False  # Flag for this specific test block

        def replace_args_block_match(
            args_match_obj, original_test_name=original_test_name
        ):
            nonlocal current_test_block_was_modified
            args_header = args_match_obj.group(1)
            original_args_inner_content = args_match_obj.group(2)
            args_footer = args_match_obj.group(3)

            if verbose:
                print(
                    f"    Found args block in '{original_test_name}'.", file=sys.stderr
                )

            processed_args_inner_content, args_block_had_inlining = (
                _process_one_args_block_inner_content(
                    original_args_inner_content,
                    baml_file_path,
                    original_test_name,
                    verbose=verbose,
                )
            )

            if args_block_had_inlining:
                current_test_block_was_modified = True
                return f"{args_header}{processed_args_inner_content}{args_footer}"
            return args_match_obj.group(0)  # Return original args block if not modified

        modified_test_inner_content = ARGS_BLOCK_PATTERN.sub(
            replace_args_block_match, test_inner_content
        )

        if current_test_block_was_modified:
            new_test_name = f"{test_name_prefix}{original_test_name}{test_name_suffix}"
            # Replace the old test name in the header with the new one
            new_test_header = re.sub(
                r"\b" + re.escape(original_test_name) + r"\b",
                new_test_name,
                original_test_header,
                count=1,
            )

            reconstructed_block = (
                f"{new_test_header}{modified_test_inner_content}{test_footer}"
            )
            collected_modified_test_blocks.append(reconstructed_block)
            if verbose:
                print(
                    f"    Test block '{original_test_name}' was modified, renamed to '{new_test_name}', and collected.",
                    file=sys.stderr,
                )
        elif verbose:
            print(
                f"    Test block '{original_test_name}' had no inlinable file references.",
                file=sys.stderr,
            )

    return collected_modified_test_blocks


def inline_baml_tests():
    parser = argparse.ArgumentParser(
        description="Recursively find .baml files, inline 'file' references in test args, "
        "rename these tests, and write them to a consolidated output file."
    )
    parser.add_argument(
        "--search-root-path",
        default=str(Path.cwd()),
        help="The root folder path to search for .baml files. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--output-folder",
        default=".inlined/",
        help="Folder to write the consolidated inlined tests file. Default: '.inlined/'",
    )
    parser.add_argument(
        "--test-name-prefix",
        default="",
        help="Prefix to add to the names of inlined test functions. Default: empty string.",
    )
    parser.add_argument(
        "--test-name-suffix",
        default="_inlined",
        help="Suffix to add to the names of inlined test functions. Default: '_inlined'.",
    )
    parser.add_argument(
        "--verbose",
        choices=["true", "false"],
        default="false",
        help="Set to 'true' for detailed output to stderr, 'false' for summary only. Default: 'false'.",
    )

    args = parser.parse_args()

    root_folder = Path(args.search_root_path)
    verbose = args.verbose.lower() == "true"
    test_name_prefix = args.test_name_prefix
    test_name_suffix = args.test_name_suffix
    output_folder_path = Path(args.output_folder)

    output_filename = "inlined_tests.baml"  # Fixed name for the output file
    output_file_path = output_folder_path / output_filename

    if not root_folder.is_dir():
        print(
            f"Error: Root search folder not found or is not a directory: {root_folder}",
            file=sys.stderr,
        )
        sys.exit(1)

    if verbose:
        print(f"Starting search in: {root_folder}", file=sys.stderr)
        print(f"Output target: {output_file_path}", file=sys.stderr)
        print(f"Test name prefix: '{test_name_prefix}'", file=sys.stderr)
        print(f"Test name suffix: '{test_name_suffix}'", file=sys.stderr)
        print("-" * 30, file=sys.stderr)

    processed_files_count = 0
    total_inlined_tests_collected = 0
    files_with_inlined_tests = 0

    all_collected_inlined_test_blocks = (
        []
    )  # To store all modified test blocks as strings

    for baml_file_path in root_folder.rglob("*.baml"):
        if not baml_file_path.is_file():
            continue

        processed_files_count += 1
        if verbose:
            print(f"Processing: {baml_file_path}", file=sys.stderr)

        try:
            original_content = baml_file_path.read_text(encoding="utf-8")
            modified_test_blocks_from_current_file = process_baml_file_content(
                original_content,
                baml_file_path,
                verbose=verbose,
                test_name_prefix=test_name_prefix,
                test_name_suffix=test_name_suffix,
            )

            if modified_test_blocks_from_current_file:
                files_with_inlined_tests += 1
                all_collected_inlined_test_blocks.extend(
                    modified_test_blocks_from_current_file
                )
                num_collected_this_file = len(modified_test_blocks_from_current_file)
                total_inlined_tests_collected += num_collected_this_file
                if verbose:
                    print(
                        f"  Collected {num_collected_this_file} inlined test(s) from {baml_file_path}.",
                        file=sys.stderr,
                    )
            elif verbose:
                print(
                    f"  No inlinable test arguments found in {baml_file_path}.",
                    file=sys.stderr,
                )

        except Exception as e:
            print(
                f"  An unexpected error occurred processing {baml_file_path}: {e}",
                file=sys.stderr,
            )
            if verbose:
                traceback.print_exc(file=sys.stderr)

        if verbose and modified_test_blocks_from_current_file:
            print(file=sys.stderr)  # Visual separator in verbose log for multiple files

    output_file_written_successfully = False
    if all_collected_inlined_test_blocks:
        folder_was_brand_new = not output_folder_path.exists()
        try:
            # Ensure the output directory exists
            # mkdir(exist_ok=True) will not error if it's already a directory.
            # It WILL error with FileExistsError if output_folder_path is a file.
            output_folder_path.mkdir(parents=True, exist_ok=True)
            if folder_was_brand_new and verbose:
                print(f"Created output folder: {output_folder_path}", file=sys.stderr)

            # If the folder was newly created, add .gitignore
            if folder_was_brand_new:
                gitignore_path = output_folder_path / ".gitignore"
                try:
                    gitignore_path.write_text(
                        "*\n# Content of this folder is auto-generated.\n",
                        encoding="utf-8",
                    )
                    if verbose:
                        print(
                            f"Created .gitignore in {output_folder_path}",
                            file=sys.stderr,
                        )
                except Exception as e_git:
                    print(
                        f"Warning: Could not create .gitignore in {output_folder_path}: {e_git}",
                        file=sys.stderr,
                    )

            # Write the consolidated BAML content
            try:
                with output_file_path.open("w", encoding="utf-8") as f_out:
                    f_out.write("\n\n".join(all_collected_inlined_test_blocks))
                    f_out.write("\n")  # Ensure final newline
                if verbose:
                    print(
                        f"Successfully wrote {total_inlined_tests_collected} inlined test(s) to: {output_file_path}",
                        file=sys.stderr,
                    )
                output_file_written_successfully = True
            except Exception as e_write:
                print(
                    f"Error: Could not write to output file {output_file_path}: {e_write}",
                    file=sys.stderr,
                )
                if verbose:
                    traceback.print_exc(file=sys.stderr)

        except FileExistsError:  # Raised by mkdir if output_folder_path is a file
            print(
                f"Error: Output path '{output_folder_path}' exists but is a file, not a directory. Cannot write output.",
                file=sys.stderr,
            )
        except OSError as e_dir:  # Other OS errors during directory creation
            print(
                f"Error: Could not create or access output folder '{output_folder_path}': {e_dir}",
                file=sys.stderr,
            )

    # Final summary messages
    if verbose:
        print("-" * 30, file=sys.stderr)
    print(
        f"Finished. Processed {processed_files_count} .baml file(s).", file=sys.stderr
    )
    print(
        f"Collected {total_inlined_tests_collected} inlined test function(s) from {files_with_inlined_tests} file(s).",
        file=sys.stderr,
    )

    if total_inlined_tests_collected > 0:
        if output_file_written_successfully:
            print(
                f"Consolidated output written to: {output_file_path}", file=sys.stderr
            )
        else:
            print(
                f"Consolidated output was NOT written due to errors (see messages above). Target path: {output_file_path}",
                file=sys.stderr,
            )
    else:
        print(
            f"No inlined tests to write. Output file '{output_file_path}' was not created.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    inline_baml_tests()
