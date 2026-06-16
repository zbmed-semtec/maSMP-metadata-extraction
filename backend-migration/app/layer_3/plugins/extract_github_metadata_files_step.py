"""GitHub README/CHANGELOG discovery steps."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.common.extract_codemeta_readme_link_step import (
    ExtractCodemetaReadmeLinkStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.common.extract_masmp_changelog_link_step import (
    ExtractMasmpChangelogLinkStep,
)
from app.layer_3.steps.extract_steps.adapters.platform.helpers.shared_utils import (
    github_file_fetcher,
)


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubMetadataFilesStep(ExtractionPlugin):
    """Prepare likely GitHub metadata file URLs for downstream fetch steps."""

    name = "github.extract_metadata_files"

    extracts = {"codemeta:readme", "maSMP:changelog"}
    platforms = {"github"}
    priority_level = 101

    def extract(self, context: StepContext, state: StepState) -> StepState:
        github_file_fetcher(context, state)
        base_url = (state.data.get("normalized_repo_url") or context.repo_url or "").rstrip("/")
        branches = ("main", "master")
        state.data["metadata_file_candidates"] = {
            "readme": [f"{base_url}/blob/{branch}/README.md" for branch in branches],
            "changelog": [f"{base_url}/blob/{branch}/CHANGELOG.md" for branch in branches],
        }
        return state


def github_readme_changelog_link_steps() -> tuple[ExtractionStep, ...]:
    return (
        ExtractGithubMetadataFilesStep(),
        ExtractCodemetaReadmeLinkStep(),
        ExtractMasmpChangelogLinkStep(),
    )
