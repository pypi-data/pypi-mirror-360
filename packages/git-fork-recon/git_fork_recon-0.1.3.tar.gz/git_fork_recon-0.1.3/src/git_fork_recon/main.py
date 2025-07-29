#!/usr/bin/env python

from typing import Optional
import logging
from pathlib import Path
from datetime import datetime, timezone
import os
import sys
from dotenv import load_dotenv

from .config import load_config
from .github.api import GithubClient
from .git.repo import GitRepo
from .llm.client import LLMClient
from .report.generator import ReportGenerator

# Load environment variables from .env file at startup
load_dotenv()

logger = logging.getLogger(__name__)


def analyze(
    repo_url: str,
    output: Optional[Path] = None,
    output_formats: Optional[str] = None,
    active_within: Optional[str] = None,
    env_file: Optional[Path] = None,
    model: Optional[str] = None,
    context_length: Optional[int] = None,
    api_base_url: Optional[str] = None,
    api_key_env_var: Optional[str] = None,
    parallel: int = 5,
    verbose: bool = False,
    clear_cache: bool = False,
    activity_threshold: Optional[datetime] = None,
    max_forks: Optional[int] = None,
) -> None:
    """Analyze forks of a GitHub repository."""
    # Load config and apply overrides
    config = load_config(env_file, api_key_env_var=api_key_env_var)

    # Override config with command line options if provided
    if model is not None:
        config.model = model
    if context_length is not None:
        config.context_length = context_length
    if api_base_url is not None:
        config.openai_api_base_url = api_base_url

    # Log final configuration
    logger.info(f"Found GITHUB_TOKEN: {'yes' if config.github_token else 'no'}")
    logger.info(f"Using API key from: {config.api_key_source}")
    logger.info(f"Found API key: {'yes' if config.openai_api_key else 'no'}")
    logger.info(f"Using API base URL: {config.openai_api_base_url}")
    logger.info(f"Using CACHE_DIR: {config.cache_dir}")
    logger.info(f"Using MODEL: {config.model}")
    if config.context_length is not None:
        logger.info(f"Using CONTEXT_LENGTH override: {config.context_length}")
    logger.info(f"Maximum forks to analyze: {max_forks}")

    # Initialize clients with parallel option
    github_client = GithubClient(config.github_token, max_parallel=parallel)
    llm_client = LLMClient(
        config.openai_api_key,
        model=config.model,
        context_length=config.context_length,
        api_base_url=config.openai_api_base_url,
        max_parallel=parallel,
    )

    # Get repository and fork information
    repo_info = github_client.get_repository(repo_url)

    # Clear cache only if requested
    if clear_cache and config.cache_dir:
        repo_cache = config.cache_dir / repo_info.name
        if repo_cache.exists():
            logger.info(f"Clearing cache for {repo_cache}")
            repo_cache.unlink(missing_ok=True)

    # Clone main repository
    git_repo = GitRepo(repo_info, config)

    # Get and filter forks
    forks = github_client.get_forks(repo_info, max_forks=max_forks)

    # Apply activity threshold if specified
    if activity_threshold:
        active_forks = [
            fork
            for fork in forks
            if datetime.fromisoformat(fork.last_updated) >= activity_threshold
        ]
        logger.info(
            f"Found {len(active_forks)} forks active since {activity_threshold} out of {len(forks)} processed forks"
        )
        forks = active_forks

    # Generate report
    report_gen = ReportGenerator(llm_client)
    report = report_gen.generate(repo_info, forks, git_repo)

    # Write report to file or stdout
    if output is None or str(output) == "-":
        sys.stdout.write(report)
    else:
        output.write_text(report)
        logger.info(f"Report written to {output}")

        # Handle additional output formats if specified
        if output_formats:
            report_gen.convert_report(output, output_formats.split(","))
