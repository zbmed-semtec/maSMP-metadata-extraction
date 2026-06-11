"""Backward-compatible aliases for software maSMP profiles."""
from __future__ import annotations

from app.layer_3.steps.contracts.pipeline import ExtractionPipeline
from app.layer_3.composers.profiles.software_github_masmp import (
    build_software_github_masmp_pipeline,
)
from app.layer_3.composers.profiles.software_gitlab_masmp import (
    build_software_gitlab_masmp_pipeline,
)


def build_software_masmp_github_pipeline() -> ExtractionPipeline:
    return build_software_github_masmp_pipeline()


def build_software_masmp_gitlab_pipeline() -> ExtractionPipeline:
    return build_software_gitlab_masmp_pipeline()


def build_software_masmp_pipeline(platform: str | None = None) -> ExtractionPipeline:
    """Return software extraction pipeline tuned for maSMP output."""
    normalized_platform = (platform or "").strip().lower()
    if normalized_platform in {"", "github"}:
        return build_software_masmp_github_pipeline()
    if normalized_platform == "gitlab":
        return build_software_masmp_gitlab_pipeline()
    raise ValueError(
        f"Unsupported platform for software/maSMP: {platform!r}. "
        "Expected one of: 'github', 'gitlab', or None."
    )
