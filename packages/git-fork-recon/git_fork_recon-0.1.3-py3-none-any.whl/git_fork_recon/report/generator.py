from typing import List, Dict, Any, Optional, Set
import subprocess
import logging
from pathlib import Path
import re
import asyncio

from jinja2 import Environment, PackageLoader, select_autoescape

from ..github.api import RepoInfo, ForkInfo
from ..git.repo import GitRepo, CommitInfo
from ..llm.client import LLMClient
from .pandoc import PandocConverter

logger = logging.getLogger(__name__)


def _linkify_commit_hashes(text: str, repo_url: str) -> str:
    """Convert commit hashes in text to markdown links."""
    # Match 7-40 character hex strings that look like commit hashes
    pattern = r"\b([a-f0-9]{7,40})\b"

    def replace_hash(match):
        commit_hash = match.group(1)
        return f"[{commit_hash}]({repo_url}/commit/{commit_hash})"

    return re.sub(pattern, replace_hash, text)


class ReportGenerator:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.pandoc = PandocConverter()
        self.env = Environment(
            loader=PackageLoader("git_fork_recon", "report/templates"),
            autoescape=select_autoescape(),
        )
        # Add custom filter
        self.env.filters["linkify_commits"] = lambda text: _linkify_commit_hashes(
            text, self.repo_url
        )

    async def _analyze_fork(
        self, fork: ForkInfo, git_repo: GitRepo
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single fork asynchronously."""
        try:
            commits = git_repo.get_fork_commits(fork)

            diff = None
            if commits and len(commits[0].files_changed) > 0:
                diff = git_repo.get_file_diff(fork, commits[0].files_changed[0])

            summary = await self.llm_client.async_summarize_changes(commits, diff)

            return {"fork": fork, "commits": commits, "summary": summary}

        except Exception as e:
            logger.error(f"Error analyzing fork {fork.repo_info.name}: {e}")
            return None

    async def _analyze_fork_batch(
        self, forks: List[ForkInfo], git_repo: GitRepo
    ) -> List[Dict[str, Any]]:
        """Analyze a batch of forks in parallel."""
        tasks = []
        for fork in forks:
            tasks.append(self._analyze_fork(fork, git_repo))

        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _generate_interesting_forks_summary(
        self, analyses: List[Dict[str, Any]]
    ) -> str:
        """Generate a high-level summary of the most interesting forks using the LLM."""
        # Prepare the input for the LLM
        fork_summaries = []
        for analysis in analyses:
            fork = analysis["fork"]
            fork_summaries.append(
                f"Fork: {fork.repo_info.owner}/{fork.repo_info.name}\n"
                f"Stars: {fork.repo_info.stars}\n"
                f"Changes: {analysis['summary']}\n"
            )

        prompt = (
            "Below are summaries of changes made in different forks of a repository. "
            "Please provide a concise overview of the most interesting forks, focusing on "
            "those with significant feature additions or major changes. Give less emphasis "
            "to forks that are primarily about installation or minor fixes.\n\n"
            + "\n---\n".join(fork_summaries)
        )

        return await self.llm_client.async_generate_summary(prompt)

    async def async_generate(
        self, repo_info: RepoInfo, forks: List[ForkInfo], git_repo: GitRepo
    ) -> str:
        """Generate a Markdown report summarizing the forks asynchronously."""
        template = self.env.get_template("master.md.jinja")

        # Construct GitHub repository URL and store it for the filter
        self.repo_url = f"https://github.com/{repo_info.owner}/{repo_info.name}"

        # Process forks in batches
        fork_analyses = []
        for i in range(0, len(forks), self.llm_client.max_parallel):
            batch = forks[i : i + self.llm_client.max_parallel]
            batch_results = await self._analyze_fork_batch(batch, git_repo)
            fork_analyses.extend(batch_results)

        # Generate high-level summary
        interesting_forks_summary = await self._generate_interesting_forks_summary(
            fork_analyses
        )

        # Render template
        return template.render(
            repo=repo_info,
            analyses=fork_analyses,
            summary=interesting_forks_summary,
        )

    def convert_report(self, markdown_path: Path, formats: List[str]) -> None:
        """Convert markdown report to additional formats using pandoc."""
        self.pandoc.convert(markdown_path, formats)

    def generate(
        self, repo_info: RepoInfo, forks: List[ForkInfo], git_repo: GitRepo
    ) -> str:
        """Synchronous wrapper for async_generate."""
        return asyncio.run(self.async_generate(repo_info, forks, git_repo))
