import logging
import os
import pathlib
import shutil
from collections.abc import Generator
from typing import Dict, List, Tuple

from repo2md import config, github, tree, utils

LOGGER = logging.getLogger("repo2md")


def get_content(filepath: str) -> Dict[str, str]:
    """Reads the content of a file and returns it as a dictionary with the filepath as the key.

    Args:
        filepath: File path to read.

    Returns:
        Dict[str, str]:
        A dictionary with the file path as the key and the file content as the value.
    """
    LOGGER.info("Reading file %s", filepath)
    try:
        with open(filepath) as fstream:
            return {
                filepath: "\n".join([f.replace("\n", "") for f in fstream.readlines()])
            }
    except UnicodeDecodeError as error:
        LOGGER.warning("Error reading file %s: %s", filepath, error)
        return {filepath: "No unicode data available"}


def get_current(
    dir_path: str, ignore_files: List[str], language: str = None
) -> Generator[Dict[str, str]]:
    """Loops through the current directory and yields file contents as dictionaries.

    Args:
        dir_path: Directory path to loop through.
        ignore_files: Files to ignore in the directory.
        language: Language to filter files.

    Yields:
        Dict[str, str]:
        A dictionary with the file path as the key and the file content as the value.
    """
    LOGGER.info("Reading directory %s", dir_path)
    extensions = utils.LANGUAGE_EXTENSIONS[language.lower()] if language else []
    for file in os.listdir(dir_path):
        if file.lower() in ignore_files:
            LOGGER.debug("Ignoring file %s in directory %s", file, dir_path)
            continue
        if extensions and pathlib.Path(file).suffix not in extensions:
            continue
        filepath = os.path.join(dir_path, file)
        if os.path.isfile(filepath):
            yield get_content(filepath)


def get_files(
    src: str,
    ignore_directories: List[str] = utils.IGNORE_DIRECTORIES,
    ignore_files: List[str] = utils.IGNORE_FILES,
    language: str = None,
) -> Generator[Tuple[str, List[Dict[str, str]]]]:
    """Walks through the source directory and yields directories with their file contents.

    Args:
        src: Source directory to walk through.
        ignore_directories: Directories to ignore in the walk.
        ignore_files: Files to ignore in the directories.
        language: Language to filter files.

    Yields:
        Tuple[str, List[Dict[str, str]]]:
        A generator yielding tuples of directory paths and lists of dictionaries containing file contents.
    """
    LOGGER.info("Walking directory %s", src)
    for __path, directories, files in os.walk(src):
        if any(
            (
                ignore in __path.lower().split(os.path.sep)
                for ignore in ignore_directories
            )
        ):
            LOGGER.debug("Ignoring directory %s", __path)
            continue
        # Loops through root directory
        if __path == src:
            yield src, list(get_current(src, ignore_files, language))
        # Loops through subdirectories
        for directory in directories:
            if directory.lower() in ignore_directories:
                LOGGER.debug("Ignoring directory %s", directory)
                continue
            dir_path = os.path.join(__path, directory)
            yield dir_path, list(get_current(dir_path, ignore_files, language))


def get_code(iterator: Generator[Tuple[str, List[Dict[str, str]]]]) -> str:
    """Generates a formatted string of code contents from the iterator.

    Args:
        iterator: Iterator yielding directory paths and lists of file contents.

    Returns:
        str:
        A formatted string containing the code contents, either in Markdown format or plain text.
    """
    text = ""
    sep = os.path.sep
    for __dir, content_list in iterator:
        for file_content_map in content_list:
            for filepath, content in file_content_map.items():
                text += f"###### {sep.join(filepath.split(sep)[1:])}\n\n"
                text += f"```\n{content.strip()}\n```"
                text += "\n\n"
    return text


def generate_markdown(
    path: str | pathlib.Path | os.PathLike, filename: str = None, language: str = None
) -> None:
    """Generates a Markdown file with the directory tree and code contents.

    Args:
        path: Path to the directory to process.
        filename: Filename for the output Markdown file.
        language: Programming language of the code files.
    """
    if not isinstance(path, pathlib.Path):
        path = pathlib.Path(path)
    assert path.exists(), f"Path {path.name} at {path.parent} does not exist"
    if not filename:
        filename = f"{path.name}.md"
    iterator = get_files(str(path), language=language)
    text = get_code(iterator)
    LOGGER.info("Generating tree for %s", path)
    structure = tree.Tree(path).get()
    LOGGER.info("Storing output in %s", filename)
    with open(filename, "w") as file:
        file.write(f"## Contents:\n\n```\n{structure}\n```\n\n")
        file.write(text.rstrip())
        file.write("\n")
        file.flush()


def convert_repo_to_md(
    repo_name: str = None,
    branch: str = None,
    delete: bool = True,
    destination: str = "tmp",
    language_filter: bool = False,
    source_repo_path: str = None,
    source_repo_language: str = None,
    **kwargs,
) -> None:
    """Converts a repository to a Markdown file with its directory tree and code contents.

    Args:
        repo_name: Name of the GitHub repository to convert.
        branch: Branch of the repository to use (default is None, which uses the default branch).
        delete: Boolean flag to delete the repository after conversion (default is False).
        destination: Destination directory to store the Markdown file (default is "tmp").
        language_filter: Boolean flag to filter files by language (default is True).
        source_repo_path: Source path to a repo if a directory has been downloaded already.
        source_repo_language: Programming language of the code files in source path.

    Keyword Args:
        git_token: Git token to authenticate with GitHub.
        git_owner: Owner of the repository. Defaults to the environment variable GIT_OWNER.
        git_api_url: GitHub API URL. Defaults to the environment variable GIT_API_URL.
    """
    config.env = config.EnvConfig(**kwargs)
    os.makedirs(destination, exist_ok=True)
    if source_repo_path:
        assert os.path.isdir(
            source_repo_path
        ), f"'source_repo_path' {source_repo_path!r} does not exist"
        if source_repo_language:
            assert utils.LANGUAGE_EXTENSIONS.get(
                source_repo_language.lower()
            ), f"'source_repo_language' {source_repo_language!r} is not supported for conversion"
        else:
            assert (
                language_filter is False
            ), "'source_repo_language' is required for custom source when 'language_filter' is enabled"
        downloaded = {"path": source_repo_path, "language": source_repo_language}
        delete = False  # Do not delete custom source path
        repo_name = os.path.basename(os.path.normpath(source_repo_path))
    else:
        assert repo_name, "'repo_name' is mandatory for conversion"
        assert (
            config.env.git_owner
        ), f"'git_owner' is required to fetch the repository: {repo_name!r}"
        downloaded = github.download_and_extract(
            repo=repo_name,
            dest_dir=destination,
            branch=branch,
        )
    download_path = downloaded["path"]
    output = os.path.join(destination, f"{repo_name}.md")
    args = dict(path=download_path, filename=output)
    if language_filter:
        args["language"] = downloaded["language"]
    generate_markdown(**args)
    if delete:
        LOGGER.info("Deleting repository after conversion")
        shutil.rmtree(path=download_path, ignore_errors=True)
