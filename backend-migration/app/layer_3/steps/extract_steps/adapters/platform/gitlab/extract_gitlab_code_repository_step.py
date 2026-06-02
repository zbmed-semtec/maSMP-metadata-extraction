"""Extract ``codeRepository`` (clone URL) from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
    record_field,
)


class ExtractGitlabCodeRepositoryStep(ExtractionStep):
    name = "gitlab.extract_code_repository"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.codeRepository = project.get("http_url_to_repo")
        if metadata.codeRepository is not None and record:
            record("codeRepository")

        return state


__all__ = ["ExtractGitlabCodeRepositoryStep"]
