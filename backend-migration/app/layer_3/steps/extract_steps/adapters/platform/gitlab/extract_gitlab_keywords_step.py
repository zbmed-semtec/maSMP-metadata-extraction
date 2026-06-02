"""GitLab keyword metadata steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_repo_payload,
)


class ExtractGitlabKeywordsStep(ExtractionStep):
    name = "gitlab.extract_keywords"

    def run(self, context: StepContext, state: StepState) -> StepState:
        project = gitlab_repo_payload(context, state)
        tag_list = project.get("tag_list") or []
        if tag_list:
            state.data["extracted_platform_keywords"] = list(tag_list)
        return state


def gitlab_keyword_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabKeywordsStep(),)
