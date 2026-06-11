"""GitHub requirements links steps."""
from __future__ import annotations

from app.layer_3.steps.contracts import ExtractionStep, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_file_fetcher,
    github_repo_payload,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils.platform_payloads import (
    record_field,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils.requirements_discovery import (
    discover_requirement_urls_from_state,
)


class ExtractGithubRequirementsLinksStep:
    """Extract requirements links for GitHub repositories."""

    name = "github.extract_requirements_links"

    def run(self, context: StepContext, state: StepState) -> StepState:
        github_file_fetcher(context, state)
        github_repo_payload(context, state)
        urls = discover_requirement_urls_from_state(
            state_data=state.data,
            platform="github",
            repo_url=context.repo_url,
        )
        if urls:
            state.metadata.softwareRequirements = urls
            record_field(state, "softwareRequirements")
        return state


def github_requirements_link_steps() -> tuple[ExtractionStep, ...]:
    return (ExtractGithubRequirementsLinksStep(),)
