"""GitLab programming language metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_languages_payload,
    record_field,
)


class ExtractGitlabProgrammingLanguagesStep(ExtractionStep):
    name = "gitlab.extract_programming_languages"

    def run(self, context: StepContext, state: StepState) -> StepState:
        languages = gitlab_languages_payload(context, state)
        if languages:
            state.metadata.programmingLanguage = list(languages.keys())
            record_field(state, "programmingLanguage")
        return state


def gitlab_programming_language_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabProgrammingLanguagesStep(),)


__all__ = ["ExtractGitlabProgrammingLanguagesStep", "gitlab_programming_language_steps"]

