from typing import Union

import click

from .github import GitHubClient


@click.command()
@click.argument("repo")
@click.option("--token", help="GitHub API token", envvar="GITHUB_TOKEN")
def main(repo: str, token: Union[str, None] = None):
    """Fetch statistics for a GitHub repository.

    REPO should be in the format 'owner/repo', e.g., 'python/cpython'
    """
    try:
        owner, repo_name = repo.split("/")
    except ValueError:
        click.echo("Error: Repository should be in the format 'owner/repo'")
        return

    client = GitHubClient(token)
    try:
        stats = client.get_repo_stats(owner, repo_name)
        click.echo(f"\n{stats['name']} Statistics:")
        click.echo(f"⭐ Stars:       {stats['stars']:,}")
        click.echo(f"🍴 Forks:       {stats['forks']:,}")
        click.echo(f"⚠️ Open Issues: {stats['open_issues']:,}")
        click.echo(f"👀 Watchers:    {stats['watchers']:,}")
        click.echo(f"🔤 Language:    {stats['language']}")
        click.echo(f"📅 Created:     {stats['created_at']}")
        click.echo(f"📝 Updated:     {stats['updated_at']}\n")
    except Exception as e:
        click.echo(f"Error: Failed to fetch repository stats: {e}")


if __name__ == "__main__":
    main()
