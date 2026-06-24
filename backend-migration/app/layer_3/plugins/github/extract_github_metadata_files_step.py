"""GitHub README/CHANGELOG discovery steps."""

from app.layer_3.steps.contracts import ExtractionStep
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubMetadataFilesStep(ExtractionPlugin):
    """Prepare likely GitHub metadata file URLs for downstream fetch steps."""

    name = "github.extract_metadata_files"

    extracts = {"codemeta:readme", "maSMP:changelog"}
    platforms = {"github"}
    priority_level = 101

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        ppp.github_file_fetcher(context, state)
        base_url = (state.data.get("normalized_repo_url") or context.repo_url or "").rstrip("/")
        branches = ("main", "master")
        state.data["metadata_file_candidates"] = {
            "readme": [f"{base_url}/blob/{branch}/README.md" for branch in branches],
            "changelog": [f"{base_url}/blob/{branch}/CHANGELOG.md" for branch in branches],
        }
        return state

