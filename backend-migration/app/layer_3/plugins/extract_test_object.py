"""Extract alternate-name candidates from OpenAlex."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.openalex_client_plugin import OpenAlexClient
from app.layer_3.plugins.openalex_work_lookup import get_openalex_work


class ExtractOpenAlexAlternateNamesStep(ExtractionPlugin):
    """Extract OpenAlex title candidates for metadata.alternateName."""

    name = "extract.test_object"
    extracts = {"https://schema.org/value"}
    platforms = {'github', 'gitlab'}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        state.metadata_collector.collect(self.name, "https://schema.org/value", 43, 0.67)
        return state

    def applicable(self, context):
        return True