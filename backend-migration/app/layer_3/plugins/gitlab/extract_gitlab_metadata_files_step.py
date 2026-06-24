"""GitLab README/CHANGELOG discovery steps."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabMetadataFilesStep(ExtractionPlugin):
    """Prepare likely GitLab metadata file URLs for downstream fetch steps."""

    name = "gitlab.extract_metadata_files"
    platforms = {"gitlab"}
    extracts = {"codemeta:readme", "maSMP:changelog"}
    priority_level = 101

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get("platform-payloads-plugin")
        ppp.gitlab_file_fetcher(context, state)
        base_url = (state.data.get("normalized_repo_url") or context.repo_url or "").rstrip("/")
        branches = ("main", "master")
        state.data["metadata_file_candidates"] = {
            "readme": [f"{base_url}/-/blob/{branch}/README.md" for branch in branches],
            "changelog": [f"{base_url}/-/blob/{branch}/CHANGELOG.md" for branch in branches],
        }
        return state
