# Developer Tools (`devtools`)

This directory contains utility scripts designed to assist with the development, maintenance, and usage workflows related to the `baml-agents` project and projects that depend on it.

These tools are primarily intended for users looking to streamline tasks in their own projects that use `baml-agents` or BAML itself.

## Available Tools

### 1. `update-baml` (Update BAML Generator Versions)

**Description:**

Automates the process of updating the `version` specified within `generator` blocks across multiple `.baml` files. This is useful after upgrading the `baml-py` dependency to ensure your BAML files reference the correct generator version.

**Usage:**

The script is typically run using `uvx`:

```bash
# Basic usage
uvx --from baml-agents update-baml --target-version <new_baml_version> --search-root-path <path_to_search>

# Example: Update all .baml files in the current directory and subdirectories to version 0.85.0
uvx --from baml-agents update-baml --target-version 0.85.0 --search-root-path . --verbose false
```

**Arguments:**

- `--target-version`: (Optional) The new BAML version string (e.g., `0.85.0`) to set in the generator blocks.
- `--search-root-path`: (Optional) The root directory from which to start recursively searching for `baml_src` folders containing `.baml` files.
- `--verbose`: (Optional) Set to `true` for detailed output, `false` (default) for less output.

**Pro Tips:**

1.  **Update to Installed Version:** Automatically use the currently installed `baml-py` version:
    ```bash
    uvx --from baml-agents update-baml --target-version "$(uv pip list | grep baml-py | awk '{print $2}')" --search-root-path . --verbose false
    ```
2.  **Combine with Updates:** Add this command to a script after `uv sync --upgrade` for a one-step dependency update process.
3.  **Pinned Execution:** Consider running with a specific version of `baml-agents` if needed: `uvx --from baml-agents@0.22.1 update-baml ...` (evaluate pros/cons for your workflow).
4.  **Help:** Get detailed help and all options:
    ```bash
    uvx --from baml-agents update-baml --help
    ```

**Status:** Beta - Please report any issues or suggestions!

### 2. `inline-baml-tests` (Inline BAML Test File Arguments)

> [!TIP]
> TL;DR how it works
> 1. the script finds all tests with `my_arg { file "path/to/file.txt" }`.  Let's say your test is called `test my_test`.
> 2. it creates a **new** file with a **new** test called `test my_test_inlined` it contains `my_arg "this_is_file_contents"`
> 3. You need to run `test my_test_inlined`, the `test my_test` will not work (it contains the path)

**Description:**

Facilitates cleaner and more maintainable BAML test cases by allowing large string arguments or shared values to be stored in external files. The script processes `.baml` files, looking for test arguments defined with the `file` keyword (e.g., `my_arg { file "data/prompt.txt" }`). It reads the content from the referenced external file and "inlines" it directly as a BAML string literal into a new version of the test case. These modified test cases are typically renamed (e.g., by adding an `_inlined` suffix) and collected into a separate output BAML file (by default, `inlined_tests.baml` inside an `.inlined/` directory).

This primarily helps with:

- **Improved Readability & Maintainability:** Keeps your main `.baml` files concise and focused by offloading bulky string literals (like extensive prompts, sample documents, or large JSON/XML payloads) to separate, easily manageable text files.
- **Data Reusability:** Allows a single piece of test data (e.g., a standard input template, a common configuration snippet) stored in an external file to be easily referenced and reused across multiple BAML test cases, promoting DRY (Don't Repeat Yourself) principles.

The resulting inlined tests can be useful for creating self-contained test suites, for instance, for easier sharing or for execution in environments where relative file paths might be problematic.

**Usage:**

The script is typically run using `uvx`:

> [!TIP]
> Let's explain how uvx works (conceptually, rather than accurately)
> `uvx --from my_package --with another_package my_program`
> 1. It creates a virtual python environment where it can safely `pip install` new packages without messing with anything else
> 2. It does `pip install my_package` and `pip install another_package` into that environment
> 3. It runs `my_program.py` python program from `my_package`

```bash
# Basic usage - search current directory, output to .inlined/inlined_tests.baml
uvx --from baml-agents --with regex inline-baml-tests

# Example: Search in 'my_baml_project/baml_src', output to 'dist/tests_bundle', add 'CI_' prefix
uvx --from baml-agents --with regex inline-baml-tests \
    --search-root-path ./my_baml_project/baml_src \
    --output-folder ./dist/tests_bundle \
    --test-name-prefix "CI_" \
    --test-name-suffix "_bundle" \
    --verbose true
```

**Arguments:**

- `--search-root-path`: (Optional) The root directory from which to start recursively searching for `.baml` files. Defaults to the current working directory.
- `--output-folder`: (Optional) The folder where the BAML file containing the newly generated, inlined tests will be written. Defaults to `.inlined/`. A `.gitignore` file is automatically added to this folder if it's newly created. The output file within this folder is always named `inlined_tests.baml`.
- `--test-name-prefix`: (Optional) A prefix string to add to the names of test functions that have had their arguments inlined. Defaults to an empty string.
- `--test-name-suffix`: (Optional) A suffix string to add to the names of test functions that have had their arguments inlined. Defaults to `_inlined`.
- `--verbose`: (Optional) Set to `true` for detailed output to `stderr`, `false` (default) for summary output.

**Pro Tips:**

1.  **Simplify Complex Test Setups:** Externalize complex or lengthy string inputs (e.g., few-shot examples, email bodies, code snippets) to keep your BAML test definitions clean and focused on the test logic itself.
2.  **Manage Shared Test Assets:** Define common string assets once in external files and reference them in multiple tests. Updating the asset in one place updates it for all referencing tests after re-running the inliner.
3.  **Custom Naming for Clarity:** Use `--test-name-prefix` and `--test-name-suffix` to clearly distinguish inlined tests from their originals or to organize them.
4.  **Workflow Integration:** Consider adding this script to your development workflow (e.g., pre-commit hook, build step) to automatically update the inlined test file when source BAML or external data files change.
5.  **Help:** Get detailed help and all options:
    ```bash
    uvx --from baml-agents inline-baml-tests --help
    ```

**Status:** Beta - Please report any issues or suggestions!
