import logging
import sys

import click

from repo2md.main import convert_repo_to_md, generate_markdown  # noqa: F401
from repo2md.utils import (  # noqa: F401
    IGNORE_DIRECTORIES,
    IGNORE_FILES,
    IGNORE_LIST,
    LANGUAGE_EXTENSIONS,
)

version = "0.1.0"

LOGGER = logging.getLogger("repo2md")
handler = logging.StreamHandler()
handler.setFormatter(
    fmt=logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s:%(funcName)s:%(lineno)d] - %(message)s",
        datefmt="%b-%d-%Y %H:%M:%S",
    )
)
LOGGER.setLevel(level=logging.INFO)
LOGGER.addHandler(hdlr=handler)


def print_help() -> None:
    """Prints the help section for the commandline interface."""
    options = {
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--repo | -R": "Name of the GitHub repository to convert.",
        "--branch | -B": "Branch of the repository to use (default is None, which uses the default branch).",
        "--delete | -D": "Boolean flag to delete the repository after conversion (default is True).",
        "--output | -O": "Output directory to store the Markdown file (default is 'tmp').",
        "--language | -L": "Boolean flag to filter files by language (default is False).",
        "--source | -S": "Source path to a repo if a directory has been downloaded already.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    click.echo(
        f"\nUsage: repo2md [arbitrary-command]\nCommands:"
        "\n\t* github: Initiates the conversion process."
        "\n\t* local: Uses a local directory as the source for conversion."
        f"\n\nOptions (and corresponding behavior):{choices}"
    )


def rename_io_map(**kwargs) -> dict:
    """Renames the keyword arguments to match the expected parameters for the conversion functions.

    Args:
        **kwargs: Keyword arguments to be renamed.

    Returns:
        dict:
        A dictionary with the renamed keyword arguments.
    """
    kwargs_map = {
        "repo": "repo_name",
        "language": "language_filter",
        "source": "source_repo_path",
        "output": "destination",
    }
    final_kwargs = {}
    for key, value in kwargs.items():
        if kwargs_map.get(key):
            final_kwargs[kwargs_map[key]] = value
        else:
            final_kwargs[key] = value
    return final_kwargs


@click.command()
@click.argument("github", required=False)
@click.argument("local", required=False)
@click.option("--version", "-V", is_flag=True, help="Prints the version.")
@click.option("--help", "-H", is_flag=True, help="Prints the help section.")
@click.option("--repo", "-R", help="Name of the GitHub repository to convert.")
@click.option("--branch", "-B", help="Branch of the repository to use (default is None, which uses the default branch).")
@click.option("--output", "-O", help="Output directory to store the Markdown file (default is 'tmp').", default="tmp")
@click.option("--delete", "-D", help="Boolean flag to delete the repository after conversion (default is True).", is_flag=True, default=False)
@click.option("--language", "-L", help="Boolean flag to filter files by language (default is False).", is_flag=True, default=False)
@click.option("--source", "-S", help="Source path to a repo if a directory has been downloaded already.")
def commandline(*args, **kwargs) -> None:
    # noinspection GrazieInspection
    """Starter function to construct a markdown file from a GitHub repository.

        **Flags**
            - ``--version | -V``: Prints the version.
            - ``--help | -H``: Prints the help section.
            - ``--repo | -R``: Name of the GitHub repository to convert.
            - ``--branch | -B``: Branch of the repository to use (default is None, which uses the default branch).
            - ``--delete | -D``: Boolean flag to delete the repository after conversion (default is True).
            - ``--output | -O``: Output directory to store the Markdown file (default is "tmp").
            - ``--language | -L``: Boolean flag to filter files by language (default is False).
            - ``--source | -S``: Source path to a repo if a directory has been downloaded already.

        **Commands**
            - ``github``: Initiates the conversion process.
            - ``local``: Uses a local directory as the source for conversion.
    """
    assert sys.argv[0].lower().endswith("repo2md"), "Invalid commandline trigger!!"

    if kwargs.get("version"):
        click.echo(f"repo2md {version}")
        sys.exit(0)
    if kwargs.get("help"):
        print_help()
        sys.exit(0)

    if kwargs.get("github"):
        convert_repo_to_md(**rename_io_map(**kwargs))
    elif kwargs.get("source"):
        generate_markdown(**rename_io_map(**kwargs))
    else:
        print_help()
        sys.exit(1)
