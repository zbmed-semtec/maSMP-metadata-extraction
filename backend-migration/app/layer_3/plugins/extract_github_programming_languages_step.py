"""GitHub programming language metadata step."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_languages_payload,
    record_field,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubProgrammingLanguagesStep(ExtractionPlugin):
    name = "github.extract_programming_languages"

    extracts = {"programmingLanguage"}
    platforms = {"github"}

    def extract(self, context: StepContext, state: StepState) -> StepState:
        languages = github_languages_payload(context, state)
        if languages:
            state.metadata.programmingLanguage = list(languages.keys())
            record_field(state, "programmingLanguage")
        return state


def github_programming_language_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubProgrammingLanguagesStep(),)


__all__ = ["ExtractGithubProgrammingLanguagesStep", "github_programming_language_steps"]

