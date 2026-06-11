"""GitHub download URL metadata steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
)


class ExtractGithubDownloadUrlStep:
    name = "github.extract_download_url"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        archive_url = repo_data.get("archive_url", "")
        if archive_url:
            metadata.downloadUrl = archive_url.replace("{archive_format}{/ref}", "zipball/master")
            if callable(record):
                record("downloadUrl")
        return state


def github_download_url_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubDownloadUrlStep(),)
