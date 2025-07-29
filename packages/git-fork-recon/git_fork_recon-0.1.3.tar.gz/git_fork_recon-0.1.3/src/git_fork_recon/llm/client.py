from typing import List, Optional, Dict, Any
import logging
import json
import tiktoken
import sys
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ..git.repo import CommitInfo

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

# Configure retry decorator
retry_decorator = retry(
    stop=stop_after_attempt(3),  # Try 3 times
    wait=wait_exponential(
        multiplier=1, min=4, max=10
    ),  # Wait 2^x * multiplier seconds between retries
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError)),
    before_sleep=lambda retry_state: logger.warning(
        f"Attempt {retry_state.attempt_number} failed. Retrying in {retry_state.next_action.sleep} seconds..."
    ),
)


class LLMClient:
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek/deepseek-chat-v3-0324:free",
        context_length: Optional[int] = None,
        api_base_url: str = DEFAULT_BASE_URL,
        max_parallel: int = 5,
    ):
        self.api_key = api_key
        self.model_name = model
        # Ensure api_base_url ends with a slash for proper URL joining
        self.api_base_url = (
            api_base_url if api_base_url.endswith("/") else api_base_url + "/"
        )
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/git-fork-recon",
            "Content-Type": "application/json",
        }
        self.model_info: Optional[Dict[str, Any]] = None
        self._context_length_override = context_length
        self.tokenizer = tiktoken.encoding_for_model(
            "gpt-4"
        )  # Reasonable default for most models
        self.max_parallel = max_parallel
        self._executor = ThreadPoolExecutor(max_workers=max_parallel)
        self._async_client = httpx.AsyncClient(timeout=600.0)
        # Initialize model info after all configuration is set
        self._init_model_info()

    @property
    def chat_completions_url(self) -> str:
        """Get the chat completions endpoint URL."""
        return urljoin(self.api_base_url, "chat/completions")

    @property
    def models_url(self) -> str:
        """Get the models endpoint URL."""
        return urljoin(self.api_base_url, "models")

    @retry_decorator
    def _init_model_info(self) -> None:
        """Fetch model information from OpenAI-compatible API."""
        try:
            response = httpx.get(self.models_url, headers=self.headers, timeout=30.0)
            response.raise_for_status()
            models = response.json()
            for model in models["data"]:
                if model["id"] == self.model_name:
                    self.model_info = model
                    if self.model_info is not None:
                        logger.info(
                            f"Model context length: {self.model_info.get('context_length', 'unknown')}"
                        )
                    return
            logger.warning(f"Model {self.model_name} not found in API models list")
        except Exception as e:
            logger.error(f"Error fetching model info: {e}")
            self.model_info = None
            raise

    def _get_token_count(self, text: str) -> int:
        """Get approximate token count for text."""
        return len(self.tokenizer.encode(text))

    def _chunk_text(self, text: str, max_tokens: int) -> List[str]:
        """Split text into chunks that fit within token limit."""
        tokens = self.tokenizer.encode(text)
        chunks: List[str] = []
        current_chunk: List[int] = []

        # Reserve tokens for system message and response
        chunk_limit = (
            max_tokens - 1000
        )  # Reserve 1000 tokens for system message and response

        for token in tokens:
            current_chunk.append(token)
            if len(current_chunk) >= chunk_limit:
                chunks.append(self.tokenizer.decode(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(self.tokenizer.decode(current_chunk))

        return chunks

    @retry_decorator
    def _make_direct_request(self, messages: List[dict]) -> str:
        """Make a direct request to the API without chunking."""
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        try:
            response = httpx.post(
                self.chat_completions_url,
                headers=self.headers,
                json=data,
                timeout=600.0,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error making LLM request: {e}")
            raise

    def _make_request(self, messages: List[dict], depth: int = 0) -> str:
        """Make a request to the OpenRouter API with chunking if needed."""
        if depth > 1:
            raise ValueError("Maximum chunk processing depth exceeded")

        # Get max context length from override or model info
        context_length = self._context_length_override
        if context_length is None and self.model_info is not None:
            context_length = self.model_info.get(
                "context_length", 8192
            )  # Default to 8192 if unknown
        else:
            context_length = 8192  # Fallback default

        # Calculate total tokens in messages
        total_tokens = sum(self._get_token_count(msg["content"]) for msg in messages)

        # If within limits, proceed normally
        if total_tokens <= context_length - 1000:  # Reserve 1000 tokens for response
            return self._make_direct_request(messages)

        # If over limit, need to chunk and summarize
        logger.warning(
            f"Input exceeds token limit. Chunking input ({total_tokens} tokens)"
        )

        # Only chunk the user message, keep system message intact
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        user_msg = next((m for m in messages if m["role"] == "user"), None)

        if not user_msg:
            raise ValueError("No user message found in messages")

        chunks = self._chunk_text(user_msg["content"], context_length)
        chunk_summaries = []

        for i, chunk in enumerate(chunks):
            chunk_messages = []
            if system_msg:
                chunk_messages.append(system_msg)
            chunk_messages.append(
                {
                    "role": "user",
                    "content": f"This is part {i+1} of {len(chunks)} of the input. Please analyze this part:\n\n{chunk}",
                }
            )

            try:
                summary = self._make_direct_request(chunk_messages)
                chunk_summaries.append(summary)
            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {e}")
                continue

        # Combine chunk summaries
        if chunk_summaries:
            final_messages = []
            if system_msg:
                final_messages.append(system_msg)
            final_messages.append(
                {
                    "role": "user",
                    "content": f"Please provide a cohesive summary combining these {len(chunks)} analysis parts:\n\n"
                    + "\n\n".join(
                        f"Part {i+1}:\n{summary}"
                        for i, summary in enumerate(chunk_summaries)
                    ),
                }
            )

            return self._make_request(final_messages, depth + 1)
        else:
            raise ValueError("Failed to process any chunks")

    def summarize_changes(
        self, commits: List[CommitInfo], diff: Optional[str] = None
    ) -> str:
        """Generate a summary of changes from commits and optional diff."""
        # Create a structured summary of commits
        commit_summaries = []
        for commit in commits:
            summary = {
                "hash": commit.hash[:8],
                "message": commit.message,
                "author": commit.author,
                "date": commit.date,
                "stats": {
                    "files_changed": len(commit.files_changed),
                    "insertions": commit.insertions,
                    "deletions": commit.deletions,
                },
                "files": commit.files_changed,
            }
            commit_summaries.append(summary)

        # Create the prompt
        messages = [
            {
                "role": "system",
                "content": """You are an expert code reviewer analyzing changes made in a fork of a GitHub repository.
                Your task is to provide a clear, concise summary of the changes and innovations introduced in the fork.
                Focus on:
                1. The main themes or purposes of the changes
                2. Any significant new features or improvements
                3. Notable code refactoring or architectural changes
                4. Potential impact or value of the changes

                Provide a list of tags that apply to the changes from:
                - "installation" - changes to the installation and packaging process, including dependencies via Docker, pip, conda etc
                - "feature" - adds a significant new feature
                - "functionality" - changes or improves the behavior of an existing feature
                - "bugfix" - fixes a bug
                - "improvement" - improves performance or reliability
                - "ui" - changes or improves the user interface, including command line interface
                - "refactor" - changes the code structure without adding new features, cleans up unused code
                - "documentation" - adds or improves documentation
                - "test" - adds or improves tests
                - "ci" - adds or improves CI/CD
                - "whitespace" - only whitespace changes, no significant code changes
                
                If no forks with notable changes are provided, say so, don't make stuff up. 
                Be objective and technical, but make the summary accessible to developers.""",
            },
            {
                "role": "user",
                "content": f"""Please analyze these changes and provide a summary:
                
                Commits: {json.dumps(commit_summaries, indent=2)}
                
                {"Diff:" + diff if diff else ""}""",
            },
        ]

        return self._make_request(messages)

    def generate_summary(self, prompt: str) -> str:
        """Generate a high-level summary using a custom prompt."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert code analyst reviewing forks of a GitHub repository.
                Your task is to identify and summarize the most interesting and impactful forks.
                Focus on forks that:
                1. Add significant new features or capabilities
                2. Make major improvements to functionality or performance
                3. Introduce innovative approaches or solutions
                4. Have potential value for the main repository

                Provide a concise, well-organized summary that highlights:
                - The most notable forks and their key contributions
                - The potential impact or value of their changes
                - Any emerging patterns or themes across multiple forks

                Be objective and technical, but make the summary accessible to developers.
                Avoid detailed descriptions of installation-focused forks unless they introduce significant architectural changes.
                
                Write one or two paragraphs in Markdown, including hyperlinks, discussing your findings.""",
            },
            {"role": "user", "content": prompt},
        ]

        return self._make_request(messages)

    async def _async_make_direct_request(self, messages: List[dict]) -> str:
        """Make an async direct request to the API without chunking."""
        data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        try:
            response = await self._async_client.post(
                self.chat_completions_url, headers=self.headers, json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error making async LLM request: {e}")
            raise

    async def _async_make_request(self, messages: List[dict], depth: int = 0) -> str:
        """Make an async request to the OpenRouter API with chunking if needed."""
        if depth > 1:
            raise ValueError("Maximum chunk processing depth exceeded")

        context_length = self._context_length_override
        if context_length is None and self.model_info is not None:
            context_length = self.model_info.get("context_length", 8192)
        else:
            context_length = 8192

        total_tokens = sum(self._get_token_count(msg["content"]) for msg in messages)

        if total_tokens <= context_length - 1000:
            return await self._async_make_direct_request(messages)

        logger.warning(
            f"Input exceeds token limit. Chunking input ({total_tokens} tokens)"
        )

        system_msg = next((m for m in messages if m["role"] == "system"), None)
        user_msg = next((m for m in messages if m["role"] == "user"), None)

        if not user_msg:
            raise ValueError("No user message found in messages")

        chunks = self._chunk_text(user_msg["content"], context_length)
        chunk_tasks = []

        for i, chunk in enumerate(chunks):
            chunk_messages = []
            if system_msg:
                chunk_messages.append(system_msg)
            chunk_messages.append(
                {
                    "role": "user",
                    "content": f"This is part {i+1} of {len(chunks)} of the input. Please analyze this part:\n\n{chunk}",
                }
            )
            chunk_tasks.append(self._async_make_direct_request(chunk_messages))

        # Use gather instead of TaskGroup for Python 3.9 compatibility
        chunk_summaries = await asyncio.gather(*chunk_tasks)

        if chunk_summaries:
            final_messages = []
            if system_msg:
                final_messages.append(system_msg)
            final_messages.append(
                {
                    "role": "user",
                    "content": f"Please provide a cohesive summary combining these {len(chunks)} analysis parts:\n\n"
                    + "\n\n".join(
                        f"Part {i+1}:\n{summary}"
                        for i, summary in enumerate(chunk_summaries)
                    ),
                }
            )

            return await self._async_make_request(final_messages, depth + 1)
        else:
            raise ValueError("Failed to process any chunks")

    async def async_summarize_changes(
        self, commits: List[CommitInfo], diff: Optional[str] = None
    ) -> str:
        """Generate an async summary of changes from commits and optional diff."""
        commit_summaries = []
        for commit in commits:
            summary = {
                "hash": commit.hash[:8],
                "message": commit.message,
                "author": commit.author,
                "date": commit.date,
                "stats": {
                    "files_changed": len(commit.files_changed),
                    "insertions": commit.insertions,
                    "deletions": commit.deletions,
                },
                "files": commit.files_changed,
            }
            commit_summaries.append(summary)

        messages = [
            {
                "role": "system",
                "content": """You are an expert code reviewer analyzing changes made in a fork of a GitHub repository.
                Your task is to provide a clear, concise summary of the changes and innovations introduced in the fork.
                Focus on:
                1. The main themes or purposes of the changes
                2. Any significant new features or improvements
                3. Notable code refactoring or architectural changes
                4. Potential impact or value of the changes

                Provide a list of tags that apply to the changes from:
                - "installation" - changes to the installation and packaging process, including dependencies via Docker, pip, conda etc
                - "feature" - adds a significant new feature
                - "functionality" - changes or improves the behavior of an existing feature
                - "bugfix" - fixes a bug
                - "improvement" - improves performance or reliability
                - "ui" - changes or improves the user interface, including command line interface
                - "refactor" - changes the code structure without adding new features, cleans up unused code
                - "documentation" - adds or improves documentation
                - "test" - adds or improves tests
                - "ci" - adds or improves CI/CD
                - "whitespace" - only whitespace changes, no significant code changes
                
                Be objective and technical, but make the summary accessible to developers.""",
            },
            {
                "role": "user",
                "content": f"""Please analyze these changes and provide a summary:
                
                Commits: {json.dumps(commit_summaries, indent=2)}
                
                {"Diff:" + diff if diff else ""}""",
            },
        ]

        return await self._async_make_request(messages)

    async def async_generate_summary(self, prompt: str) -> str:
        """Generate a high-level summary using a custom prompt asynchronously."""
        messages = [
            {
                "role": "system",
                "content": """You are an expert code analyst reviewing forks of a GitHub repository.
                Your task is to identify and summarize the most interesting and impactful forks.
                Focus on forks that:
                1. Add significant new features or capabilities
                2. Make major improvements to functionality or performance
                3. Introduce innovative approaches or solutions
                4. Have potential value for the main repository

                Provide a concise, well-organized summary that highlights:
                - The most notable forks and their key contributions
                - The potential impact or value of their changes
                - Any emerging patterns or themes across multiple forks

                Be objective and technical, but make the summary accessible to developers.
                Avoid detailed descriptions of installation-focused forks unless they introduce significant architectural changes.
                
                Write one or two paragraphs in Markdown, including hyperlinks, discussing your findings.""",
            },
            {"role": "user", "content": prompt},
        ]

        return await self._async_make_request(messages)

    # Synchronous wrappers for backward compatibility
    def sync_summarize_changes(
        self, commits: List[CommitInfo], diff: Optional[str] = None
    ) -> str:
        """Synchronous wrapper for async_summarize_changes."""
        return asyncio.run(self.async_summarize_changes(commits, diff))

    def sync_generate_summary(self, prompt: str) -> str:
        """Synchronous wrapper for async_generate_summary."""
        return asyncio.run(self.async_generate_summary(prompt))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._async_client.aclose()
