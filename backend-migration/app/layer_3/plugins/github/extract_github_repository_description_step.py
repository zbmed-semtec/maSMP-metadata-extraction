"""Extract repository ``description`` from the GitHub API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
    record_field,
)


from app.layer_2.extraction_plugin import ExtractionPlugin

class ExtractGithubRepositoryDescriptionStep(ExtractionPlugin):
    name = "github.extract_repository_description"
    extracts = {"description"}
    platforms = {"github"}
    def extract(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.description = repo_data.get("description")
        if metadata.description is not None and record:
            record("description")

        return state


__all__ = ["ExtractGithubRepositoryDescriptionStep"]
