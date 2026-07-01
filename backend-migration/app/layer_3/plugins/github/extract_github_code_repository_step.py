"""Extract ``codeRepository`` (clone URL) from the GitHub API payload."""

from typing import Callable
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin

class ExtractGithubCodeRepositoryStep(ExtractionPlugin):
    name = "github.extract_code_repository"

    extracts = {"https://schema.org/codeRepository"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        plugin = self.plugin_manager.get("platform-payloads-plugin")
        repo_data = plugin.github_repo_payload(context, state)

        html_url = repo_data.get("html_url")
        if html_url:
            state.metadata_collector.collect(self.name, "https://schema.org/codeRepository", f"{html_url}.git")

        return state



