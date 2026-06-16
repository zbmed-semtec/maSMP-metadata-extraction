"""Extract ``codeRepository`` (clone URL) from the GitHub API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
    record_field,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubCodeRepositoryStep(ExtractionPlugin):
    name = "github.extract_code_repository"

    extracts = {"codeRepository"}
    platforms = {"github"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        html_url = repo_data.get("html_url")
        if html_url:
            metadata.codeRepository = f"{html_url}.git"
        if metadata.codeRepository is not None and record:
            record("codeRepository")

        return state


__all__ = ["ExtractGithubCodeRepositoryStep"]
