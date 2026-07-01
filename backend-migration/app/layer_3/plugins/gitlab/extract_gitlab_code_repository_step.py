"""Extract ``codeRepository`` (clone URL) from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabCodeRepositoryStep(ExtractionPlugin):
    name = "gitlab.extract_code_repository"
    platforms = {"gitlab"}
    extracts = {"https://schema.org/codeRepository"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        record: Callable[[str], None] | None = state.data.get("record_field")

        codeRepository = project.get("http_url_to_repo")
        state.metadata_collector.collect(self.name, "https://schema.org/codeRepository", codeRepository)

        return state



