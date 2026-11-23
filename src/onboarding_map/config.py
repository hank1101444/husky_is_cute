"""Settings loaded from the environment / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_MODEL = "claude-sonnet-5-5"
DEFAULT_DB_PATH = "data/onboarding.db"


@dataclass(frozen=True)
class FetchLimits:
    pulls: int = 30
    issues: int = 30
    commits: int = 50


@dataclass(frozen=True)
class Settings:
    anthropic_model: str
    github_token: str | None
    db_path: Path


def load_settings() -> Settings:
    """Read settings; ANTHROPIC_API_KEY itself is read by the anthropic SDK."""
    load_dotenv()
    return Settings(
        anthropic_model=os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODEL,
        github_token=os.getenv("GITHUB_TOKEN") or None,
        db_path=Path(os.getenv("ONBOARDING_DB_PATH") or DEFAULT_DB_PATH),
    )
