"""GitLab README/CHANGELOG discovery steps."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.common.extract_codemeta_readme_link_step import (
    ExtractCodemetaReadmeLinkStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.common.extract_masmp_changelog_link_step import (
    ExtractMasmpChangelogLinkStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    gitlab_file_fetcher,
)


class ExtractGitlabMetadataFilesStep:
    """Prepare likely GitLab metadata file URLs for downstream fetch steps."""

    name = "gitlab.extract_metadata_files"

    def run(self, context: StepContext, state: StepState) -> StepState:
        gitlab_file_fetcher(context, state)
        base_url = (state.data.get("normalized_repo_url") or context.repo_url or "").rstrip("/")
        branches = ("main", "master")
        state.data["metadata_file_candidates"] = {
            "readme": [f"{base_url}/-/blob/{branch}/README.md" for branch in branches],
            "changelog": [f"{base_url}/-/blob/{branch}/CHANGELOG.md" for branch in branches],
        }
        return state


def gitlab_readme_changelog_link_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractGitlabMetadataFilesStep(),
        ExtractCodemetaReadmeLinkStep(),
        ExtractMasmpChangelogLinkStep(),
    )
