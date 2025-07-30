import io
import logging
import os
import shutil
import zipfile
from typing import Dict

import requests

from repo2md import config, utils

LOGGER = logging.getLogger("repo2md")


def get_repo_info(
    repo: str,
) -> Dict[str, str]:
    """Fetches the default branch and language of a GitHub repository.

    Args:
        repo: The name of the repository.

    Returns:
        Dict[str, str]:
        A dictionary containing the default branch and language of the repository.
    """
    LOGGER.info("Fetching default branch for %s/%s...", config.env.git_owner, repo)
    url = utils.urljoin(config.env.repos_url, config.env.git_owner, repo)
    response = requests.get(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {config.env.git_token}",
        },
    )
    assert response.ok, response.text
    data = response.json()
    return {"branch": data.get("default_branch"), "language": data.get("language")}


def make_request(url: str) -> requests.Response:
    """Makes a GET request to the specified URL with the configured headers.

    Args:
        url: The URL to make the request to.

    Returns:
        requests.Response: The response object from the GET request.
    """
    for attempt in range(5):
        LOGGER.debug("Attempt %d to fetch %s", attempt + 1, url)
        try:
            response = requests.get(
                url,
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {config.env.git_token}",
                },
            )
            assert response.ok, response.text
        except requests.exceptions.RequestException as error:
            LOGGER.error(error)
            LOGGER.warning("Request failed on attempt %d, retrying...", attempt + 1)
            continue
        return response
    raise RuntimeError(f"Request failed on {url}")


def download_and_extract(
    repo: str,
    dest_dir: str,
    branch: str = None,
) -> Dict[str, str]:
    """Downloads a GitHub repository as a zip file and extracts it to the specified directory.

    Args:
        repo: Repository name.
        dest_dir: Destination directory where the repository will be extracted.
        branch: Branch name to download. If not specified, the default branch will be used.

    Returns:
        str:
        True path to the extracted repository directory.
    """
    repo_info = get_repo_info(repo=repo)
    url = utils.urljoin(
        config.env.repos_url,
        config.env.git_owner,
        repo,
        "zipball",
        branch or repo_info["branch"],
    )
    LOGGER.info("Downloading '%s/%s' to '%s'", config.env.git_owner, repo, dest_dir)
    response = make_request(url=url)
    LOGGER.debug("Download successful, unzipping...")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        zip_ref.extractall(dest_dir)
        subdir = zip_ref.namelist()[0].split("/")[0]
    LOGGER.debug(f"Repository unzipped to: {dest_dir}")
    true_path = os.path.join(dest_dir, repo)
    if os.path.exists(true_path):
        LOGGER.warning(
            "Directory '%s' already exists, removing it before renaming", true_path
        )
        shutil.rmtree(true_path)
    LOGGER.debug("Renaming '%s' to '%s'", subdir, repo)
    os.rename(os.path.join(dest_dir, subdir), true_path)
    return {"path": true_path, "language": repo_info["language"]}
