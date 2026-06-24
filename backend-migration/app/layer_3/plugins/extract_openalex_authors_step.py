"""Extract author candidates from OpenAlex."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.openalex_work_lookup import get_openalex_work
from app.layer_3.plugins.openalex_authors_from_work import authors_from_openalex_work

class ExtractOpenAlexAuthorsStep(ExtractionPlugin):
    """Extract OpenAlex author candidates for metadata.author."""

    name = "openalex.extract_authors"
    extracts = {} # this plugin is not called directly, but is a sub-plugin to 'extract_author'
    platforms = {"github", "gitlab"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        self.client = self.plugin_manager.get("openalex_client_plugin")
        _, work_data = get_openalex_work(state, self.client)
        if work_data:
            state.data["extracted_openalex_authors"] = authors_from_openalex_work(work_data)
        return state



