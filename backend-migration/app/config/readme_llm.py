"""Configuration for README property orchestration and LLM-backed extraction."""
from __future__ import annotations

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ReadmeLlmSettings(BaseSettings):
    """Settings for the optional README property orchestration path."""

    enabled: bool = False
    provider: str = "vllm"
    model: str = "llama-3.1-70b-versatile"
    property_type: str = "software"
    prompt_template: str = "Extract README properties for the configured property type."
    hints: list[str] = Field(default_factory=list)
    property_types: dict[str, list[str]] = Field(default_factory=lambda: {
        "software": ["identifier", "author", "alternateName", "keywords", "citation"],
    })
    api_key: Optional[str] = None

    class Config:
        env_prefix = "README_LLM_"
        env_file = ".env"
        case_sensitive = False


readme_llm_settings = ReadmeLlmSettings()


__all__ = ["ReadmeLlmSettings", "readme_llm_settings"]