"""Extract project ``description`` from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
    record_field,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabRepositoryDescriptionStep(ExtractionPlugin):
    name = "gitlab.extract_repository_description"
    platforms = {"gitlab"}
    extracts = {"description"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.description = project.get("description")
        if metadata.description is not None and record:
            record("description")

        return state


__all__ = ["ExtractGitlabRepositoryDescriptionStep"]
