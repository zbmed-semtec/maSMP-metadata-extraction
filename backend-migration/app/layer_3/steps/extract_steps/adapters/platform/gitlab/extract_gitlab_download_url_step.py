"""GitLab download URL metadata steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
)


class ExtractGitlabDownloadUrlStep:
    name = "gitlab.extract_download_url"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        web_url = project.get("web_url")
        name = project.get("name")
        if web_url and name:
            metadata.downloadUrl = f"{web_url}/-/archive/master/{name}-master.zip"
            if callable(record):
                record("downloadUrl")
        return state


def gitlab_download_url_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabDownloadUrlStep(),)
