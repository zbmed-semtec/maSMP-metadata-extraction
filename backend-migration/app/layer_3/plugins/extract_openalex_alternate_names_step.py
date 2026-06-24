"""Extract alternate-name candidates from OpenAlex."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.openalex_client_plugin import OpenAlexClient
from app.layer_3.plugins.openalex_work_lookup import get_openalex_work


class ExtractOpenAlexAlternateNamesStep(ExtractionPlugin):
    """Extract OpenAlex title candidates for metadata.alternateName."""

    name = "openalex.extract_alternate_names"
    client : OpenAlexClient
    extracts = {"alternateName"}
    platforms = {'github', 'gitlab'}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        self.client = self.plugin_manager.get("openalex_client_plugin")
        _, work_data = get_openalex_work(state, self.client)
        if work_data and work_data.get("title"):
            state.data["extracted_openalex_title"] = str(work_data["title"])
        return state

    def applicable(self, context):
        return True



