"""GitHub source code URL metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_repo_payload,
    record_field,
)


class ExtractGithubSourceCodeStep(ExtractionStep):
    name = "github.extract_source_code"

    def run(self, context: StepContext, state: StepState) -> StepState:
        repo_data = github_repo_payload(context, state)
        html_url = repo_data.get("html_url")
        if not html_url:
            return state
        source_url = f"{html_url}#id"
        state.metadata.hasSourceCode = source_url
        state.metadata.codemeta_hasSourceCode = source_url
        record_field(state, "hasSourceCode")
        record_field(state, "codemeta_hasSourceCode")
        return state


def github_source_code_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubSourceCodeStep(),)


__all__ = ["ExtractGithubSourceCodeStep", "github_source_code_steps"]

