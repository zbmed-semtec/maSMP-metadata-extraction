"""Configuration for README property orchestration and LLM-backed extraction."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ReadmeLlmSettings(BaseSettings):
    """Settings for the optional README property orchestration path."""

    enabled: bool = True
    provider: str = "ollama"
    model: str = "qwen2.5:7b"
    base_url: Optional[str] = "http://127.0.0.1:11435"
    property_type: str = "software"
    prompt_template: str = "Extract README properties for the configured property type."
    hints: list[str] = Field(default_factory=list)
    property_types: dict[str, list[str]] = Field(default_factory=lambda: {
        "software": ["identifier", "author", "alternateName", "keywords", "citation", "license"],
    })
    temperature: float = 0.0
    max_tokens: int = 1024
    request_timeout: int = 120
    api_key: Optional[str] = None

    class Config:
        env_prefix = "README_LLM_"
        env_file = Path(__file__).resolve().parents[2] / ".env"
        case_sensitive = False


readme_llm_settings = ReadmeLlmSettings()
# print(readme_llm_settings.enabled)


__all__ = ["ReadmeLlmSettings", "readme_llm_settings"]