from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import re
import asyncio
from datetime import datetime

from github import Github, Repository, GithubException
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.GithubException import UnknownObjectException

logger = logging.getLogger(__name__)


@dataclass
class RepoInfo:
    """Information about a GitHub repository."""

    owner: str
    name: str
    clone_url: str
    default_branch: str
    stars: int
    description: Optional[str] = None


@dataclass
class ForkInfo:
    """Information about a forked repository."""

    repo_info: RepoInfo
    parent_repo: RepoInfo
    ahead_commits: int
    behind_commits: int
    has_pull_requests: bool
    pull_request_urls: List[str]
    last_updated: str


class GithubClient:
    def __init__(self, token: str, max_parallel: int = 5):
        self.client = Github(token)
        self.max_parallel = max_parallel

    def _check_rate_limit(self):
        """Check rate limit status and log warning if getting low."""
        rate_limit = self.client.get_rate_limit()
        remaining = rate_limit.core.remaining
        total = rate_limit.core.limit
        reset_time = rate_limit.core.reset.strftime("%Y-%m-%d %H:%M:%S UTC")

        if remaining < 100:
            logger.warning(
                f"GitHub API rate limit low: {remaining}/{total} requests remaining. "
                f"Resets at {reset_time}"
            )
        else:
            logger.debug(
                f"GitHub API rate limit status: {remaining}/{total} requests remaining. "
                f"Resets at {reset_time}"
            )

        return remaining

    async def _process_fork(
        self, repo: Repository, fork: Repository
    ) -> Optional[ForkInfo]:
        """Process a single fork asynchronously."""
        try:
            logger.debug(f"Processing fork: {fork.full_name}")
            logger.debug(f"Fork default branch: {fork.default_branch}")
            logger.debug(f"Parent default branch: {repo.default_branch}")

            try:
                fork_branch = fork.get_branch(fork.default_branch)
                logger.debug(f"Fork branch SHA: {fork_branch.commit.sha}")

                parent_branch = repo.get_branch(repo.default_branch)
                logger.debug(f"Parent branch SHA: {parent_branch.commit.sha}")

                comparison = repo.compare(
                    parent_branch.commit.sha, fork_branch.commit.sha
                )
                logger.debug(
                    f"Comparison successful: ahead={comparison.ahead_by}, behind={comparison.behind_by}"
                )

            except UnknownObjectException as e:
                logger.warning(
                    f"Fork {fork.full_name} branch comparison failed - repository or branch may be deleted/private: {e}"
                )
                return None
            except Exception as e:
                logger.warning(f"Failed to compare branches for {fork.full_name}: {e}")
                return None

            pr_spec = f"{fork.owner.login}:{fork.default_branch}"
            logger.debug(f"Checking PRs with head: {pr_spec}")
            prs = repo.get_pulls(state="all", head=pr_spec)
            pr_urls = [pr.html_url for pr in prs]

            fork_info = ForkInfo(
                repo_info=RepoInfo(
                    owner=fork.owner.login,
                    name=fork.name,
                    clone_url=fork.clone_url,
                    default_branch=fork.default_branch,
                    stars=fork.stargazers_count,
                    description=fork.description,
                ),
                parent_repo=RepoInfo(
                    owner=repo.owner.login,
                    name=repo.name,
                    clone_url=repo.clone_url,
                    default_branch=repo.default_branch,
                    stars=repo.stargazers_count,
                    description=repo.description,
                ),
                ahead_commits=comparison.ahead_by,
                behind_commits=comparison.behind_by,
                has_pull_requests=prs.totalCount > 0,
                pull_request_urls=pr_urls,
                last_updated=fork.pushed_at.isoformat(),
            )

            if fork_info.ahead_commits > 0:
                logger.info(
                    f"Adding fork {fork.full_name} with {fork_info.ahead_commits} commits ahead"
                )
                return fork_info
            else:
                logger.debug(f"Skipping fork {fork.full_name} with no changes")
                return None

        except Exception as e:
            logger.warning(
                f"Error processing fork {fork.full_name}: {e}", exc_info=True
            )
            return None

    async def _process_fork_batch(
        self, repo: Repository, forks: List[Repository]
    ) -> List[ForkInfo]:
        """Process a batch of forks in parallel."""
        # Check rate limit before processing batch
        remaining = self._check_rate_limit()

        # Estimate requests needed (4 API calls per fork)
        requests_needed = len(forks) * 4
        if remaining < requests_needed:
            logger.warning(
                f"Rate limit may be exceeded: need ~{requests_needed} requests but only {remaining} remaining. "
                "Processing may be incomplete."
            )

        tasks = []
        for fork in forks:
            tasks.append(self._process_fork(repo, fork))

        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def async_get_forks(
        self, repo_info: RepoInfo, max_forks: Optional[int] = None
    ) -> List[ForkInfo]:
        """Get information about all forks of a repository asynchronously.

        Args:
            repo_info: Repository information
            max_forks: Maximum number of forks to process after sorting by update time
        """
        repo = self.client.get_repo(f"{repo_info.owner}/{repo_info.name}")
        forks = list(repo.get_forks())
        logger.info(
            f"Found {len(forks)} total forks for {repo_info.owner}/{repo_info.name}"
        )

        # Sort forks by updated_at before processing
        forks.sort(key=lambda x: x.updated_at, reverse=True)
        logger.debug("Sorted forks by last update time")

        # Limit number of forks to process if specified
        if max_forks and len(forks) > max_forks:
            logger.info(
                f"Limiting processing to {max_forks} most recently updated forks (out of {len(forks)} total)"
            )
            forks = forks[:max_forks]
        else:
            logger.debug(f"Processing all {len(forks)} forks (no limit specified)")

        # Check if we have enough rate limit for all forks
        remaining = self._check_rate_limit()
        total_requests_needed = len(forks) * 4  # Approximate requests per fork
        if remaining < total_requests_needed:
            logger.warning(
                f"Not enough rate limit for all forks. Need ~{total_requests_needed} requests but only have {remaining}. "
                "Will process as many as possible."
            )

        # Process forks in batches
        processed_forks = []
        for i in range(0, len(forks), self.max_parallel):
            if self._check_rate_limit() < self.max_parallel * 4:
                logger.error(
                    "Rate limit too low to process next batch. Stopping early."
                )
                break

            batch = forks[i : i + self.max_parallel]
            batch_results = await self._process_fork_batch(repo, batch)
            processed_forks.extend(batch_results)

        logger.info(
            f"Found {len(processed_forks)} active forks with changes out of {len(forks)} processed forks"
        )
        # Final sort by significance (ahead commits and stars)
        processed_forks.sort(
            key=lambda x: (x.ahead_commits, x.repo_info.stars), reverse=True
        )
        return processed_forks

    def get_forks(
        self, repo_info: RepoInfo, max_forks: Optional[int] = None
    ) -> List[ForkInfo]:
        """Synchronous wrapper for async_get_forks."""
        return asyncio.run(self.async_get_forks(repo_info, max_forks))

    def get_repository(self, repo_identifier: str) -> RepoInfo:
        """Get information about a GitHub repository.

        Args:
            repo_identifier: Either a GitHub URL or a repository name in the format 'owner/repo'
        """
        if "/" in repo_identifier and "github.com" not in repo_identifier:
            # Already in owner/repo format
            owner, name = repo_identifier.split("/")
        else:
            # URL format
            owner, name = self._parse_repo_url(repo_identifier)

        repo = self.client.get_repo(f"{owner}/{name}")

        return RepoInfo(
            owner=repo.owner.login,
            name=repo.name,
            clone_url=repo.clone_url,
            default_branch=repo.default_branch,
            stars=repo.stargazers_count,
            description=repo.description,
        )

    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        # Remove trailing slash if present
        url = url.rstrip("/")
        pattern = r"github\.com[:/]([^/]+)/([^/\s]+?)(?:\.git)?$"
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return match.group(1), match.group(2)
