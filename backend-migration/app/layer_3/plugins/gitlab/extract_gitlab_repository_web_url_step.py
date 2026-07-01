"""Extract canonical web ``url`` from the GitLab API payload."""

from typing import Callable

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.platform_payloads_plugin import PlatformPayloadsPlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGitlabRepositoryWebUrlStep(ExtractionPlugin):
    name = "gitlab.extract_repository_web_url"
    platforms = {"gitlab"}
    extracts = {"https://schema.org/url"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp : PlatformPayloadsPlugin = self.plugin_manager.get('platform-payloads-plugin')
        project = ppp.gitlab_repo_payload(context, state)
        
        record: Callable[[str], None] | None = state.data.get("record_field")

        url = project.get("web_url")
        state.metadata_collector.collect(self.name, "https://schema.org/url", url)

        return state



