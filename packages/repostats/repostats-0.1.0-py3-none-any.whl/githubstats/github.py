from typing import Dict, Union

import requests


class GitHubClient:
    """A simple GitHub API client."""

    def __init__(self, token: Union[str, None] = None):
        """Initialize the GitHub client.

        Args:
            token: Optional GitHub API token for authenticated requests
        """
        self.base_url: str = "https://api.github.com"
        self.headers: Dict[str, str] = {}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_repo_stats(self, owner: str, repo: str) -> Dict[str, Union[str, int]]:
        """Get basic statistics for a repository.

        Args:
            owner: Repository owner (user or organization)
            repo: Repository name

        Returns:
            Dictionary with repository statistics
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()

        return {
            "name": data["full_name"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "open_issues": data["open_issues_count"],
            "watchers": data["subscribers_count"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
            "language": data["language"],
        }
