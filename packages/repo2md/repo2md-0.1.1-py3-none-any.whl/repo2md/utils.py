import re

LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "csharp": [".cs"],
    "c++": [".cpp", ".h"],
    "c": [".c", ".h"],
    "ruby": [".rb"],
    "go": [".go"],
    "php": [".php"],
    "html": [".html", ".htm"],
    "css": [".css"],
    "bash": [".sh"],
    "kotlin": [".kt", ".kts"],
    "swift": [".swift"],
    "rust": [".rs"],
    "scala": [".scala"],
    "perl": [".pl"],
    "lua": [".lua"],
    "dart": [".dart"],
    "elixir": [".ex", ".exs"],
    "haskell": [".hs"],
    "shell": [".sh", ".bash"],
    "powershell": [".ps1"],
    "sql": [".sql"],
    "pascal": [".pas"],
    "objective-c": [".m", ".h"],
    "r": [".r"],
    "julia": [".jl"],
}

IGNORE_FILES = [
    ".gitignore",
    "readme.md",
    "license",
    "requirements.txt",
    "setup.py",
    "pyproject.toml",
    "pipfile",
    "pipfile.lock",
    "pnpm-lock.yaml",
    "pnpm-lock.yml",
    "package-lock.json",
    "yarn.lock",
    ".dockerignore",
    ".pre-commit-config.yaml",
    "makefile",
    "settings.gradle",
    "build.gradle",
    "pom.xml",
    "build.sbt",
    "cargo.toml",
    "cargo.lock",
    "gradlew",
    "gradlew.bat",
    ".gitattributes",
    "changelog.md",
    ".java-version",
    "openapi.yml",
    "openapi.yaml",
    "openapi.json",
    "swagger.yml",
    "swagger.yaml",
    "swagger.json",
]

IGNORE_DIRECTORIES = [
    "__pycache__",
    ".git",
    ".idea",
    "venv",
    ".github",
    "node_modules",
    ".ds_store",
    ".vscode",
    ".pytest_cache",
    "build",
    "dist",
    "docs",
    "tests",
    "gradle",
]

IGNORE_LIST = IGNORE_DIRECTORIES + IGNORE_FILES


def urljoin(*args) -> str:
    """Joins given arguments into an url. Trailing but not leading slashes are stripped for each argument.

    Returns:
        str:
        Joined url.
    """
    return "/".join(map(lambda x: str(x).rstrip("/").lstrip("/"), args))


def is_valid_url(url: str):
    """Regular expression for validating a URL.

    Args:
        url: Takes the URL as a string.

    Returns:
        bool:
        Returns a boolean flag to indicate validity.
    """
    # noinspection RegExpRedundantEscape,RegExpSimplifiable
    pattern = re.compile(
        r"^(https?|ftp):\/\/"  # Match http, https or ftp
        r"(\w+:\w+@)?"  # Optional username:password
        r"(\S+)"  # Domain name and optional path
        r"(\:\d+)?"  # Optional port
        r"(\/[^\s]*)?$"  # Optional path and query string
    )
    return re.match(pattern, url)
