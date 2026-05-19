"""Ordered GitLab repository core-field extract steps."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_code_repository_step import (
    ExtractGitlabCodeRepositoryStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_description_step import (
    ExtractGitlabRepositoryDescriptionStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_name_step import (
    ExtractGitlabRepositoryNameStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_repository_web_url_step import (
    ExtractGitlabRepositoryWebUrlStep,
)


def gitlab_basic_info_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractGitlabRepositoryNameStep(),
        ExtractGitlabRepositoryDescriptionStep(),
        ExtractGitlabRepositoryWebUrlStep(),
        ExtractGitlabCodeRepositoryStep(),
    )


__all__ = ["gitlab_basic_info_steps"]
