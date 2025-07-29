from pathlib import Path
from typing import Optional, Tuple
import logging
import sys
import re
import shutil
from datetime import datetime, timedelta, timezone

import typer
from rich.console import Console
from rich.logging import RichHandler

from .main import analyze

app = typer.Typer()
console = Console()
logger = logging.getLogger(__name__)


def parse_time_duration(duration: str) -> timedelta:
    """Parse a human-readable time duration into a timedelta.

    Supports formats like:
    - '1 hour', '2 hours'
    - '1 day', '3 days'
    - '1 week', '2 weeks'
    - '1 month', '6 months'
    - '1 year', '3 years'
    - '1 year 6 months'
    """
    duration = duration.lower()
    total_days = 0
    total_seconds = 0

    pairs = re.findall(r"(\d+)\s*([a-z]+?)s?\b(?:\s+|$)", duration)
    if not pairs:
        raise ValueError(f"Could not parse time duration: {duration}")

    for value_str, unit in pairs:
        value = int(value_str)
        if unit in ("hour", "hr", "h"):
            total_seconds += value * 3600
        elif unit in ("day", "d"):
            total_days += value
        elif unit in ("week", "wk", "w"):
            total_days += value * 7
        elif unit in ("month", "mo", "m"):
            total_days += value * 30  # Approximate
        elif unit in ("year", "yr", "y"):
            total_days += value * 365  # Approximate
        else:
            raise ValueError(f"Unknown time unit: {unit}")

    return timedelta(days=total_days, seconds=total_seconds)


def parse_github_url(url: str) -> Tuple[str, str]:
    """Extract owner and repository name from a GitHub URL."""
    url = url.rstrip("/")
    pattern = r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub repository URL")
    return match.group(1), match.group(2)


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


def clear_repo_cache(repo_dir: Path) -> None:
    """Clear the cached repository data."""
    if repo_dir.exists():
        logger.info(f"Clearing cache for {repo_dir}")
        shutil.rmtree(repo_dir)


@app.command()
def main(
    ctx: typer.Context,
    repo_url: Optional[str] = typer.Argument(None, help="URL of the GitHub repository to analyze"),
    output: Optional[Path] = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file path (defaults to {repo_name}-forks.md)",
    ),
    active_within: Optional[str] = typer.Option(
        None,
        "--active-within",
        help="Only consider forks with activity within this time period (e.g. '1 hour', '2 days', '6 months', '1 year')",
    ),
    env_file: Optional[Path] = typer.Option(
        None,
        "--env-file",
        help="Path to .env file",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        help="OpenRouter model to use (overrides MODEL env var)",
    ),
    context_length: Optional[int] = typer.Option(
        None,
        "--context-length",
        help="Override model context length (overrides CONTEXT_LENGTH env var)",
    ),
    api_base_url: Optional[str] = typer.Option(
        None, "--api-base-url", help="OpenAI-compatible API base URL"
    ),
    api_key_env_var: Optional[str] = typer.Option(
        None,
        "--api-key-env-var",
        help="Environment variable containing the API key",
    ),
    parallel: int = typer.Option(
        5, "--parallel", "-p", help="Number of parallel requests"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
    clear_cache: bool = typer.Option(
        False, "--clear-cache", help="Clear cached repository data before analysis"
    ),
    max_forks: Optional[int] = typer.Option(
        None,
        "--max-forks",
        help="Maximum number of forks to analyze (default: no limit)",
    ),
    output_formats: Optional[str] = typer.Option(
        None,
        "--output-formats",
        help="Comma-separated list of additional formats to generate (html,pdf)",
    ),
) -> None:
    """Analyze a GitHub repository's fork network and generate a summary report."""
    # If no repo_url is provided, print help and exit.
    if repo_url is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    # Set up logging
    setup_logging(verbose)

    try:
        # Parse repository URL
        owner, repo = parse_github_url(repo_url)
        repo_full_name = f"{owner}/{repo}"
        logger.debug(f"Analyzing repository: {repo_full_name}")

        # Set default output filename if none specified
        if output is None:
            output = Path(f"{owner}-{repo}-forks.md")
            logger.info(f"No output file specified, using default: {output}")

        # Parse active_within if provided
        activity_threshold = None
        if active_within:
            try:
                delta = parse_time_duration(active_within)
                activity_threshold = datetime.now(timezone.utc) - delta
                logger.info(f"Only considering forks active since {activity_threshold}")
            except ValueError as e:
                logger.error(f"Invalid active-within format: {e}")
                sys.exit(1)

        analyze(
            repo_url=repo_url,
            output=output,
            active_within=active_within,
            env_file=env_file,
            model=model,
            context_length=context_length,
            api_base_url=api_base_url,
            api_key_env_var=api_key_env_var,
            parallel=parallel,
            verbose=verbose,
            clear_cache=clear_cache,
            max_forks=max_forks,
            output_formats=output_formats,
        )

    except Exception as e:
        logger.error(f"Error analyzing repository: {e}", exc_info=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

