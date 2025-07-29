# Git fork recon

Analyse the network of forked git repositories, summarise changes and innovations in forked repositories.

## Features

- Intelligent analysis of fork networks using LLM-powered summaries
- Filters and prioritizes forks based on number of commits ahead of parent, starts, recent activity, PRs. Ignores forks with no changes.
- Local caching of git repositories and forks as remotes
- Detailed Markdown reports with:
  - Repository overview
  - Analysis of significant forks
  - Commit details and statistics
  - Links to GitHub commits and repositories
  - Overall summary of changes and innovations highlighting the most interesting forks

# Installation

```bash
pip install git-fork-recon
```

## Installation (development)

Using `uv` (recommended):
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate a new virtual environment (optional but recommended)
uv venv
source .venv/bin/activate

# Install the package in editable mode
uv pip install -e .
```

## Configuration

The following environment variables are required (can be provided via `.env` file):

- `GITHUB_TOKEN`: GitHub API token for (public read-only) repository metadata access
- `OPENROUTER_API_KEY` or `OPENAI_API_KEY`: API key for an OpenAI-compatible LLM provider
- `CACHE_DIR` (optional): Directory for caching repository data (defaults to `~/.cache/git-fork-recon`)

## Running

```bash
# Activate the virtual environment if you haven't already
# source .venv/bin/activate

git-fork-recon https://github.com/martinpacesa/BindCraft
```

Output is generated as `{username}-{repo}-forks.md` by default (use `-o` to specify a different file name, `-o -` to print to stdout).

## Options

```bash
$ git-fork-recon --help
                                                                                                          
 Usage: git-fork-recon [OPTIONS] REPO_URL                                                                               
                                                                                                                        
 Analyze a GitHub repository's fork network and generate a summary report.                                              
                                                                                                                        
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    repo_url      TEXT  URL of the GitHub repository to analyze [default: None] [required]                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --output              -o      PATH     Output file path (defaults to {repo_name}-forks.md) [default: None]           │
│ --active-within               TEXT     Only consider forks with activity within this time period (e.g. '1 hour', '2  │
│                                        days', '6 months', '1 year')                                                  │
│                                        [default: None]                                                               │
│ --env-file                    PATH     Path to .env file [default: None]                                             │
│ --model                       TEXT     OpenRouter model to use (overrides MODEL env var) [default: None]             │
│ --context-length              INTEGER  Override model context length (overrides CONTEXT_LENGTH env var)              │
│                                        [default: None]                                                               │
│ --api-base-url                TEXT     OpenAI-compatible API base URL [default: None]                                │
│ --api-key-env-var             TEXT     Environment variable containing the API key [default: None]                   │
│ --parallel            -p      INTEGER  Number of parallel requests [default: 5]                                      │
│ --verbose             -v               Enable verbose logging                                                        │
│ --clear-cache                          Clear cached repository data before analysis                                  │
│ --max-forks                   INTEGER  Maximum number of forks to analyze after ranking [default: None]              │
│ --install-completion                   Install completion for the current shell.                                     │
│ --show-completion                      Show completion for the current shell, to copy it or customize the            │
│                                        installation.                                                                 │
│ --help                                 Show this message and exit.                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Running with Docker

Build the image:
```bash
docker build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) -t git-fork-recon .
```

Run the analysis (replace the repository URL with your target):
```bash
# Create cache directory with correct permissions
mkdir -p "${HOME}/.cache/git-fork-recon"

docker run --rm \
  -v "$(pwd):/app" \
  -v "${HOME}/.cache/git-fork-recon:/app/.cache" \
  --env-file .env \
  --user "$(id -u):$(id -g)" \
  git-fork-recon \
  "https://github.com/martinpacesa/BindCraft"
```

## See also

- [Useful forks](https://useful-forks.github.io/)
- [frogmouth](https://github.com/Textualize/frogmouth) - a quick viewer for the generated Markdown
