"""GitHub contributor metadata steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_contributors_payload,
)


class ExtractGithubContributorsStep:
    name = "github.extract_contributors"

    def run(self, context: StepContext, state: StepState) -> StepState:
        payload = github_contributors_payload(context, state)
        metadata = state.metadata
        record = state.data.get("record_field")
        if payload:
            metadata.contributor = [{"@type": "Person", "url": c.get("html_url")} for c in payload]
            if callable(record):
                record("contributor")
        return state


def github_contributor_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubContributorsStep(),)
