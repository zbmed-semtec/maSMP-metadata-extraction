"""Extract canonical web ``url`` from the GitHub API payload."""

from typing import Callable

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
    record_field,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubRepositoryWebUrlStep(ExtractionPlugin):
    name = "github.extract_repository_web_url"
    extracts = {"url"}
    platforms = {"github"}
    def extract(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record: Callable[[str], None] | None = state.data.get("record_field")

        metadata.url = repo_data.get("html_url")
        if metadata.url is not None and record:
            record("url")

        return state


__all__ = ["ExtractGithubRepositoryWebUrlStep"]
