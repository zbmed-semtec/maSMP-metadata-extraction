"""GitHub keyword metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
)


class ExtractGithubKeywordsStep(ExtractionStep):
    name = "github.extract_keywords"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        topics = repo_data.get("topics") or []
        if topics:
            state.data["extracted_platform_keywords"] = list(topics)
        return state


def github_keyword_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubKeywordsStep(),)
