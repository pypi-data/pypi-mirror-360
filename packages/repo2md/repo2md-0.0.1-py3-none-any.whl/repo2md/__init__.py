import logging

from repo2md.main import convert_repo_to_md, generate_markdown  # noqa: F401
from repo2md.utils import (  # noqa: F401
    IGNORE_DIRECTORIES,
    IGNORE_FILES,
    IGNORE_LIST,
    LANGUAGE_EXTENSIONS,
)

version = "0.0.1"

LOGGER = logging.getLogger("repo2md")
handler = logging.StreamHandler()
handler.setFormatter(
    fmt=logging.Formatter(
        fmt="%(asctime)s - [%(levelname)s] - %(name)s - %(funcName)s - Line: %(lineno)d - %(message)s",
        datefmt="%b-%d-%Y %H:%M:%S",
    )
)
LOGGER.setLevel(level=logging.INFO)
LOGGER.addHandler(hdlr=handler)
