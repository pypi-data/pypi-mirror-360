import os
from typing import Any, Dict, List

import dotenv

from repo2md import utils

dotenv.load_dotenv(dotenv_path=dotenv.find_dotenv(), override=True)


def get_env(
    keys: List[str],
    default: str = None,
) -> str:
    """Fetches the value of the environment variable that matches any of the provided keys.

    Args:
        keys: List of environment variable keys to check.
        default: Default value to return if no matching key is found.

    Returns:
        str:
        The value of the first matching environment variable, or the default value if none match.
    """
    for key in keys:
        if value := os.environ.get(key.lower()):
            return value
        if value := os.environ.get(key.upper()):
            return value
    return default


class EnvConfig:
    """Configuration class to hold environment variables for the application.

    >>> EnvConfig

    """

    def __init__(self, **kwargs: Dict[str, Any]):
        """Initializes the configuration with environment variables or provided keyword arguments.

        Keyword Args:
            git_api_url: GitHub API URL. Defaults to https://api.github.com or the environment variable GIT_API_URL.
            git_owner: Owner of the repository. Defaults to the environment variable OWNER, GIT_OWNER, or GITHUB_OWNER.
            git_token: GitHub token for authentication. Defaults to the environment variable GIT_TOKEN or GITHUB_TOKEN.
        """
        self.git_api_url: str = kwargs.get("git_api_url") or get_env(
            ["GIT_API_URL", "GITHUB_API_URL"], "https://api.github.com"
        )
        self.git_owner: str = kwargs.get("git_owner") or get_env(
            ["OWNER", "GIT_OWNER", "GITHUB_OWNER"]
        )
        self.git_token: str = kwargs.get("git_token") or get_env(
            ["GIT_TOKEN", "GITHUB_TOKEN"]
        )
        if not utils.is_valid_url(self.git_api_url):
            raise ValueError(
                f"'git_api_url' must be a valid URL, got: {self.git_api_url!r}"
            )
        self.repos_url = utils.urljoin(self.git_api_url, "repos")


env = EnvConfig()
