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

version = "0.1.1"

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
        "--owner | -O": "Name of the GitHub repository's owner/organization.",
        "--branch | -B": "Branch of the repository to use (default is None, which uses the default branch).",
        "--destination | -D": "Destination directory to store the Markdown file (default is 'tmp').",
        "--clean | -C": "Boolean flag to delete the repository after conversion (default is 'True').",
        "--language | -L": "Boolean flag to filter files by language (default is False).",
        "--source | -S": "Source path to a repo if a directory has been downloaded already.",
    }
    # unique way to increase spacing to keep all values monotonic
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
        "clean": "delete",
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
@click.option("--owner", "-O", help="Name of the GitHub repository to convert.")
@click.option(
    "--branch",
    "-B",
    help="Branch of the repository to use (default is None, which uses the default branch).",
)
@click.option(
    "--destination",
    "-D",
    help="Output directory to store the Markdown file (default is 'tmp').",
    default="tmp",
)
@click.option(
    "--clean",
    "-C",
    help="Boolean flag to delete the repository after conversion (default is True).",
    is_flag=False,
    default=True,
)
@click.option(
    "--language",
    "-L",
    help="Boolean flag to filter files by language (default is False).",
    is_flag=True,
    default=False,
)
@click.option(
    "--source",
    "-S",
    help="Source path to a repo if a directory has been downloaded already.",
)
def commandline(*args, **kwargs) -> None:
    # noinspection GrazieInspection
    """Starter function to construct a markdown file from a GitHub repository.

    **Commands**
        - ``github``: Initiates the conversion process.
        - ``local``: Uses a local directory as the source for conversion.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--help | -H``: Prints the help section.
        - ``--repo | -R``: Name of the GitHub repository to convert.
        - ``--owner | -O``: Name of the GitHub repository's owner/organization.
        - ``--branch | -B``: Branch of the repository to use (default is None, which uses the default branch).
        - ``--destination | -D``: Destination directory to store the Markdown file (default is "tmp").
        - ``--clean | -C``: Boolean flag to delete the repository after conversion (default is True).
        - ``--language | -L``: Boolean flag to filter files by language (default is False).
        - ``--source | -S``: Source path to a repo if a directory has been downloaded already.
    """
    assert sys.argv[0].lower().endswith("repo2md"), "Invalid commandline trigger!!"

    if kwargs.get("version"):
        click.echo(f"repo2md {version}")
        sys.exit(0)
    if kwargs.get("help"):
        print_help()
        sys.exit(0)

    github = kwargs.get("github") and kwargs.get("github") == "github"
    local = (kwargs.get("github") and kwargs.get("github") == "local") or (
        kwargs.get("local") and kwargs.get("local") == "local"
    )
    if github:
        assert kwargs.get("repo"), "\n\t--repo flag is mandatory for GitHub repository!"
        convert_repo_to_md(**rename_io_map(**kwargs))
    elif local:
        assert kwargs.get(
            "source"
        ), "\n\t--source flag is mandatory for local repository!"
        convert_repo_to_md(**rename_io_map(**kwargs))
    else:
        print_help()
        sys.exit(1)
