from pathlib import Path
from typing import Optional
import sys

from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


class Config(BaseModel):
    github_token: str = Field(..., description="GitHub API token")
    openai_api_key: str = Field(..., description="OpenAI-compatible API key")
    api_key_source: str = Field(
        ..., description="Environment variable that provided the API key"
    )
    openai_api_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenAI-compatible API base URL",
    )
    cache_dir: Path = Field(
        default=Path.home() / ".cache" / "git-fork-recon",
        description="Directory for caching repository data",
    )
    model: str = Field(
        default="deepseek/deepseek-chat-v3-0324:free",
        description="OpenRouter model to use",
    )
    context_length: Optional[int] = Field(
        default=None,
        description="Override model context length (if not set, uses OpenRouter API value)",
    )


def load_config(
    env_file: Optional[Path] = None,
    api_key_env_var: Optional[str] = None,
) -> Config:
    """Load configuration from environment variables and .env file."""
    print("Loading config...", file=sys.stderr)
    print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Looking for .env file: {env_file or '.env'}", file=sys.stderr)

    # Only load from env_file if explicitly provided, since we load .env at startup
    if env_file:
        print(f"Loading .env from {env_file}", file=sys.stderr)
        load_dotenv(env_file)
    else:
        # Try loading the default .env file if no specific path is given
        print("Attempting to load default .env file", file=sys.stderr)
        dotenv_loaded = load_dotenv()
        print(f"load_dotenv() result: {dotenv_loaded}", file=sys.stderr)

    github_token = os.getenv("GITHUB_TOKEN")
    openai_api_base_url = os.getenv(
        "OPENAI_API_BASE_URL", "https://openrouter.ai/api/v1"
    )

    # Get API key based on precedence rules
    openai_api_key = None
    api_key_source = None

    if api_key_env_var:
        # If api_key_env_var is specified, try that first
        openai_api_key = os.getenv(api_key_env_var)
        if openai_api_key:
            api_key_source = api_key_env_var

    if not openai_api_key:
        # If no key found and using OpenRouter, try OPENROUTER_API_KEY
        if "/openrouter.ai/" in openai_api_base_url:
            openai_api_key = os.getenv("OPENROUTER_API_KEY")
            if openai_api_key:
                api_key_source = "OPENROUTER_API_KEY"
        # Otherwise try OPENAI_API_KEY
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                api_key_source = "OPENAI_API_KEY"

    cache_dir = os.getenv("CACHE_DIR") or str(Path.home() / ".cache" / "git-fork-recon")
    model = os.getenv("MODEL") or "deepseek/deepseek-chat-v3-0324:free"
    context_length = os.getenv("CONTEXT_LENGTH")
    if context_length is not None:
        try:
            context_length = int(context_length)
        except ValueError:
            print(
                f"Error: CONTEXT_LENGTH must be an integer, got {context_length}",
                file=sys.stderr,
            )
            sys.exit(1)

    if not github_token:
        print("Error: GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)
    if not openai_api_key:
        print(
            "Error: OPENAI_API_KEY or OPENROUTER_API_KEY environment variable is required",
            file=sys.stderr,
        )
        sys.exit(1)

    # Create config with model_validate to ensure proper type handling
    return Config.model_validate(
        {
            "github_token": github_token,
            "openai_api_key": openai_api_key,
            "api_key_source": api_key_source,
            "openai_api_base_url": openai_api_base_url,
            "cache_dir": cache_dir,
            "model": model,
            "context_length": context_length,
        }
    )
