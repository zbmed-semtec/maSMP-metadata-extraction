"""GitHub contributor metadata steps."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractGithubContributorsStep(ExtractionPlugin):
    name = "github.extract_contributors"

    extracts = {"https://schema.org/contributor"}
    platforms = {"github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        ppp = self.plugin_manager.get("platform-payloads-plugin")
        payload = ppp.github_contributors_payload(context, state)
        if payload:
            contributor = [{"@type": "Person", "url": c.get("html_url")} for c in payload]
            state.metadata_collector.collect(self.name, "https://schema.org/contributor", contributor)
        return state

