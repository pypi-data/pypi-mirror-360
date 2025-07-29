from unittest.mock import MagicMock, patch

import pytest

from githubstats.github import GitHubClient


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.json.return_value = {
        "full_name": "test/repo",
        "stargazers_count": 100,
        "forks_count": 50,
        "open_issues_count": 10,
        "subscribers_count": 25,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2022-02-01T00:00:00Z",
        "language": "Python",
    }
    return mock


def test_get_repo_stats(mock_response):
    with patch("requests.get", return_value=mock_response) as mock_get:
        client = GitHubClient()
        stats = client.get_repo_stats("test", "repo")

        mock_get.assert_called_once()
        assert stats["name"] == "test/repo"
        assert stats["stars"] == 100
        assert stats["forks"] == 50


def test_github_client_with_token():
    client = GitHubClient("test_token")
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "token test_token"


def test_github_client_without_token():
    client = GitHubClient()
    assert "Authorization" not in client.headers
