"""Extract title from CITATION.cff into step state."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.cff_parse import CffParsePlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractCitationTitleStep(ExtractionPlugin):
    """Extract CFF title without mutating metadata."""

    name = "citation.extract_title"
    extracts = {"https://schema.org/name"}
    platforms = {"gitlab.com", "github.com"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        cpp : CffParsePlugin = self.plugin_manager.get('cff-parse-plugin')
        cpp.ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        title = state.data["cff_data"].get("title")
        state.data["extracted_title"] = str(title) if title else None
        return state




