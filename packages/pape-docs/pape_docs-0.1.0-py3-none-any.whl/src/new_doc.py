# # # # # # # # # # # # # # # # # # # #
# Pape Docs
# Copyright 2025 Carter Pape
#
# See file LICENSE for licensing terms.
# # # # # # # # # # # # # # # # # # # #

"""A CLI script for creating a new document from a template."""

import os
from datetime import datetime
from pathlib import Path

import click
import pape
import pape.utilities
import toml
import tzlocal


def _get_docs_directory() -> Path:
    """Determine the docs directory based on environment, pyproject.toml, or prompt."""
    docs_dir: Path | None = None

    # 1. Check PAPE_DOCS_DIR environment variable
    env_docs_dir = os.getenv("PAPE_DOCS_DIR")
    if env_docs_dir:
        docs_dir = Path(env_docs_dir)
        click.echo(
            "✓ Using docs directory from PAPE_DOCS_DIR environment variable: "
            f"{docs_dir}",
        )
    else:
        # 2. Check for pyproject.toml
        current_dir = Path.cwd()
        for directory in [current_dir, *list(current_dir.parents)]:
            pyproject_path = directory / "pyproject.toml"
            if pyproject_path.exists():
                with pyproject_path.open("r", encoding="utf-8") as f:
                    pyproject_content = toml.load(f)
                tool_config = pyproject_content.get("tool", {}).get("pape-docs", {})
                if "docs-dir" in tool_config:
                    docs_dir = directory / tool_config["docs-dir"]
                    click.echo(
                        f"✓ Using docs directory from pyproject.toml: {docs_dir}",
                    )
                    break
                docs_dir = (
                    directory / "docs"
                )  # Default to docs/ in pyproject.toml directory
                click.echo(
                    "✓ Using default docs directory in pyproject.toml location: "
                    f"{docs_dir}",
                )
                break
        if not docs_dir:  # If not found via pyproject.toml
            # 3. Look for a docs/ directory
            for directory in [current_dir, *list(current_dir.parents)]:
                potential_docs_dir = directory / "docs"
                if potential_docs_dir.is_dir():
                    docs_dir = potential_docs_dir
                    click.echo(f"✓ Using existing docs directory: {docs_dir}")
                    break

    # 4. Prompt the user if no docs directory is found
    if docs_dir is None:
        click.echo(
            "The script detected no PAPE_DOCS_DIR environment variable, "
            "no pyproject.toml in the current directory or any of its parents, "
            "and no docs/ directory in the current directory or any of its parents.",
        )
        user_input_docs_dir = click.prompt(
            "Please provide a docs directory to use",
            default="./docs",
        )
        docs_dir = Path(user_input_docs_dir)

    # At this point, docs_dir should always be a Path
    return docs_dir


def _ensure_docs_directory_exists(docs_dir: Path) -> None:
    """Ensure the docs directory exists, prompting to create it if necessary."""
    if not docs_dir.exists():
        if click.confirm(f"Docs directory '{docs_dir}' does not exist. Create it?"):
            try:
                docs_dir.mkdir(exist_ok=True)
                click.echo(f"✓ Created docs directory: {docs_dir}")
            except FileNotFoundError as file_not_found_error:
                error_message = (
                    f"'{docs_dir}' could not be created because the parent directory "
                    f'does not exist. Fix with `mkdir -p "{docs_dir.parent}"`'
                )
                raise click.ClickException(error_message) from file_not_found_error
            except Exception as e:
                error_message = f"Error creating docs directory '{docs_dir}': {e}"
                raise click.ClickException(error_message) from e
        else:
            click.echo("Operation cancelled. Docs directory not created.")
            raise click.Abort


def _prompt_for_missing_arguments(
    title: str | None,
    template_type: str | None,
    priority: str | None,
    doc_type: str | None,
) -> tuple[str, str, str, str]:
    """Prompt the user for any missing arguments."""
    if title:
        click.echo(f"✓ New document will be titled: {title}")
    else:
        title = click.prompt("Enter the short title to use in the file name")

    if title is None:
        error_message = "The short title of the doc cannot be None"
        raise TypeError(error_message)

    if template_type is None:
        template_type = click.prompt(
            "Choose template type",
            type=click.Choice(["simple", "complex"], case_sensitive=False),
            default="simple",
            show_default=True,
        )

    if doc_type is None:
        doc_type = click.prompt(
            "Enter the document type (e.g., 'RFC', 'ADR', 'Note')",
            default="",
            show_default=False,
        )

    if priority is None:
        priority = click.prompt(
            (
                "Enter the priority number to put at the start of the file name "
                "(e.g., '0210')"
            ),
            default="????",
            show_default=False,
        )
    if template_type is None:
        error_message = "Template type cannot be None after prompting."
        raise ValueError(error_message)
    if priority is None:
        error_message = "Priority cannot be None after prompting."
        raise ValueError(error_message)
    if doc_type is None:
        error_message = "Document type cannot be None after prompting."
        raise ValueError(error_message)
    return title, template_type, priority, doc_type


def _sanitize_inputs(title: str, priority: str) -> tuple[str, str]:
    """Sanitize priority and title strings."""
    sanitized_priority = (
        "".join(c if c.isalnum() or c.isspace() else "" for c in priority)
        .strip()
        .replace(" ", "-")
    )
    if not sanitized_priority:
        sanitized_priority = "????"  # Default priority

    sanitized_title = (
        "".join(c if c.isalnum() or c.isspace() else "" for c in title)
        .strip()
        .replace(" ", "-")
    )
    return sanitized_priority, sanitized_title


def _generate_document_content(
    templates_dir: Path,
    template_type: str,
    doc_type: str,
) -> str:
    """Read template content and insert dynamic values."""
    template_file = templates_dir / f"{template_type}.md"
    if not template_file.exists():
        click.echo(f"Error: Template file '{template_file}' not found.")
        raise click.Abort

    with template_file.open("r", encoding="utf-8") as f:
        template_content = f.read()

    today_date_str = pape.utilities.ap_style_date_string(
        datetime.now(tzlocal.get_localzone()),
        relative_to=False,
    )
    new_doc_content = template_content.replace("<!-- date -->", today_date_str)

    if doc_type:
        new_doc_content = new_doc_content.replace("<!-- file type -->", doc_type)
        if doc_type.lower().startswith(("a", "e", "i", "o", "u")):
            new_doc_content = new_doc_content.replace("A(n)", "An")
        else:
            new_doc_content = new_doc_content.replace("A(n)", "A")
    return new_doc_content


@click.command()
@click.argument("title", required=False, type=str)
@click.option(
    "--simple",
    "template_type",
    flag_value="simple",
    help="Use the simple template.",
)
@click.option(
    "--complex",
    "template_type",
    flag_value="complex",
    help="Use the complex template.",
)
@click.option(
    "--priority",
    "priority",
    required=False,
    type=str,
    help="Optional priority number for the document.",
)
@click.option(
    "--doc-type",
    "doc_type",
    required=False,
    type=str,
    help="Optional document type for the document.",
)
def main(
    title: str | None,
    template_type: str | None,
    priority: str | None,
    doc_type: str | None,
) -> None:
    """
    Interactively create a new file the docs folder based on the specified template.

    The script asks for the following, in order, skipping values already provided in the
    invocation or determined automatically:

    - the location of the docs directory
    - the short title of the doc (required, no default value)
    - the doc type to use (defaults to `None`)
    - which template to use (simple or complex, defaults to simple)
    - the priority number (actually a string) for the document (defaults to `"????"`)

    The script then creates a file with a name of the form 'priority-short-title.md' in
    the docs folder.
    """
    templates_dir = Path(__file__).parent.parent / "templates"

    docs_dir = _get_docs_directory()
    _ensure_docs_directory_exists(docs_dir)

    title, template_type, priority, doc_type = _prompt_for_missing_arguments(
        title,
        template_type,
        priority,
        doc_type,
    )

    sanitized_priority, sanitized_title = _sanitize_inputs(title, priority)

    filename = f"{sanitized_priority}-{sanitized_title}.md"
    new_doc_path = docs_dir / filename

    if new_doc_path.exists() and not click.confirm(
        f"File '{new_doc_path}' already exists. Overwrite?",
    ):
        click.echo("Operation cancelled.")
        return

    new_doc_content = _generate_document_content(
        templates_dir,
        template_type,
        doc_type,
    )

    with new_doc_path.open("w", encoding="utf-8") as f:
        f.write(new_doc_content)

    click.echo(f"✓ Document created successfully at {new_doc_path}")


if __name__ == "__main__":
    main()
