"""GitHub date extraction steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
)


class ExtractGithubDatesStep:
    name = "github.extract_dates"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        if repo_data.get("created_at"):
            metadata.dateCreated = str(repo_data.get("created_at"))[:10]
            if callable(record):
                record("dateCreated")
        if repo_data.get("updated_at"):
            metadata.dateModified = str(repo_data.get("updated_at"))[:10]
            if callable(record):
                record("dateModified")
        if repo_data.get("pushed_at"):
            metadata.datePublished = str(repo_data.get("pushed_at"))[:10]
            if callable(record):
                record("datePublished")
        return state


def github_date_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubDatesStep(),)
