"""Backward-compatible aliases for software CodeMeta profiles."""

from app.layer_3.steps.contracts.pipeline import ExtractionPipeline
from app.layer_3.composers.profiles.software_github_codemeta import (
    build_software_github_codemeta_pipeline,
)
from app.layer_3.composers.profiles.software_gitlab_codemeta import (
    build_software_gitlab_codemeta_pipeline,
)


def build_software_codemeta_github_pipeline() -> ExtractionPipeline:
    return build_software_github_codemeta_pipeline()


def build_software_codemeta_gitlab_pipeline() -> ExtractionPipeline:
    return build_software_gitlab_codemeta_pipeline()


def build_software_codemeta_pipeline(platform: str | None = None) -> ExtractionPipeline:
    """Return software extraction pipeline tuned for CodeMeta output."""
    normalized_platform = (platform or "").strip().lower()
    if normalized_platform in {"", "github"}:
        return build_software_codemeta_github_pipeline()
    if normalized_platform == "gitlab":
        return build_software_codemeta_gitlab_pipeline()
    raise ValueError(
        f"Unsupported platform for software/codemeta: {platform!r}. "
        "Expected one of: 'github', 'gitlab', or None."
    )
