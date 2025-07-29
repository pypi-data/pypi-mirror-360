# RepoStats

A CLI tool to fetch GitHub repository statistics.

## Installation

```bash
pip install repostats
```

## Usage

```bash
# Basic usage
repostats python/cpython

# With GitHub token for higher rate limits
export GITHUB_TOKEN=your_token_here
repostats python/cpython

# Or pass token directly
repostats python/cpython --token your_token_here
```

## Features

- Fetch repository statistics including stars, forks, issues, and more
- Support for GitHub API token authentication
- Clean, formatted output
- Cross-platform compatibility

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/repostats.git
cd repostats

# Create virtual environment
uv venv
source .venv/bin/activate

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy src
```

## License

MIT

> Much of the code was written by Claude 4 LLM. The code is provided under the MIT License, allowing for free use, modification, and distribution.