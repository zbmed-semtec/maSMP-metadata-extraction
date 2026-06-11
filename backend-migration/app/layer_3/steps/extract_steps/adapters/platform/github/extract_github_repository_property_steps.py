"""Ordered GitHub repository core-field extract steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_code_repository_step import (
    ExtractGithubCodeRepositoryStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_description_step import (
    ExtractGithubRepositoryDescriptionStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_name_step import (
    ExtractGithubRepositoryNameStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_repository_web_url_step import (
    ExtractGithubRepositoryWebUrlStep,
)


def github_basic_info_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractGithubRepositoryNameStep(),
        ExtractGithubRepositoryDescriptionStep(),
        ExtractGithubRepositoryWebUrlStep(),
        ExtractGithubCodeRepositoryStep(),
    )


__all__ = ["github_basic_info_steps"]
