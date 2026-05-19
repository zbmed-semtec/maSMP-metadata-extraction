"""GitLab requirements links steps."""

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_file_fetcher,
    gitlab_repo_payload,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils.platform_payloads import (
    record_field,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils.requirements_discovery import (
    discover_requirement_urls_from_state,
)


class ExtractGitlabRequirementsLinksStep:
    """Extract requirements links for GitLab repositories."""

    name = "gitlab.extract_requirements_links"

    def run(self, context: StepContext, state: StepState) -> StepState:
        gitlab_file_fetcher(context, state)
        gitlab_repo_payload(context, state)
        urls = discover_requirement_urls_from_state(
            state_data=state.data,
            platform="gitlab",
            repo_url=context.repo_url,
        )
        if urls:
            state.metadata.softwareRequirements = urls
            record_field(state, "softwareRequirements")
        return state


def gitlab_requirements_link_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGitlabRequirementsLinksStep(),)
