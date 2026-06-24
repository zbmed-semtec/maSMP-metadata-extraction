"""Extract keywords from CITATION.cff into step state."""

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.cff_parse import CffParsePlugin


from app.layer_2.extraction_plugin import ExtractionPlugin


class ExtractCitationKeywordsStep(ExtractionPlugin):
    """Extract CFF keywords without mutating metadata."""

    name = "citation.extract_keywords"
    extracts = {"citation"}
    platforms = {"gitlab", "github"}

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        cpp : CffParsePlugin = self.plugin_manager.get('cff-parse-plugin')
        cpp.ensure_cff_yaml_loaded(context, state)
        if not state.data.get("valid"):
            return state
        keywords = state.data["cff_data"].get("keywords")
        state.data["extracted_keywords"] = list(keywords) if isinstance(keywords, list) else []
        return state




