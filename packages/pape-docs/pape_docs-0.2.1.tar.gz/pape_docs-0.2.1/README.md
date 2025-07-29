# Pape Docs

Pape Docs is a command-line interface (CLI) tool designed to simplify the creation and management of templated documentation. It provides a straightforward, opinionated system for generating various types of documents (e.g., ADRs, tasks, notes) from predefined templates, ensuring consistency and reducing overhead.

## Features

### Streamlined Document Creation

The core functionality is provided by the `new-doc` script, which allows users to quickly create new Markdown documents based on pre-defined templates.

**Usage:**

```bash
uvx pape-docs new
```

**Options:**

- `--simple`: Use the simple template.
- `--complex`: Use the complex template.
- `--priority <PRIORITY>`: Optional priority number for the document (e.g., "0100", "????" for unknown).
- `--doc-type <DOC_TYPE>`: Optional document type (e.g., "ADR", "Task", "Notes", "Bug").

### Robust Interactivity (Planned)

The `new-doc` script is designed to support both interactive and non-interactive modes.

- **Interactive Mode (Default):**
    - Prompts for required arguments (like the document title) if not provided via command-line options.
    - Re-prompts for invalid non-empty responses, providing reasonable defaults for empty responses.
- **Non-Interactive Mode (Planned Option):**
    - Will execute without any interactive prompts.
    - Will throw an error if any required arguments (e.g., title) are missing.

### Flexible Docs Directory Location

The script intelligently locates the `docs/` directory where new documents should be placed. The search order is:

1. An environment variable (`PAPE_DOCS_DIR`).
2. A `pyproject.toml` file in the current or parent directories, looking for `[tool.pape-docs]."docs-dir"`.
3. An existing `docs/` directory in the current or parent directories.
4. If no `docs/` directory is found, the user is prompted to create one (defaulting to `./docs/`).

### Packaged Templates

Pape Docs comes with pre-defined `simple.md` and `complex.md` templates. These templates are bundled with the application and are not user-configurable. This design choice reinforces the opinionated nature of the tool, aiming to prescribe a simple and consistent documentation system.

## Installation

(Installation instructions will go here once the project is ready for distribution.)

## Development

### Setup

1. Clone the repository.
2. Install dependencies using `uv` (or `pip`):

    ```bash
    uv pip install -e .
    uv pip install -e ".[dev]"
    ```

### Linting and Formatting

This project uses `ruff` for linting and formatting.

```bash
ruff check .
ruff format .
```

### Testing

Tests will be written using `pytest`.

```bash
pytest
```
