"""GitLab source code URL metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
    record_field,
)


class ExtractGitlabSourceCodeStep(ExtractionStep):
    name = "gitlab.extract_source_code"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        web_url = project.get("web_url")
        if not web_url:
            return state
        state.metadata.hasSourceCode = web_url
        state.metadata.codemeta_hasSourceCode = web_url
        record_field(state, "hasSourceCode")
        record_field(state, "codemeta_hasSourceCode")
        return state


def gitlab_source_code_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabSourceCodeStep(),)


__all__ = ["ExtractGitlabSourceCodeStep", "gitlab_source_code_steps"]

