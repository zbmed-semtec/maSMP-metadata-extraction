"""Single pipeline unit for URL normalization and platform flags (not domain property extraction)."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import ExtractionContext, ExtractionState

class CommonPlatformPreambleStep(ExtractionPlugin):
    """Runs shared non-extract setup: normalized URL and ``state.data[\"platform\"]``."""

    name = "platform.setup_context"
    
    # higher priority, runs before other plugins
    priority_level = 102

    extracts = {"https://codemeta.github.io/terms/readme", "https://discovery.biothings.io/ns/maSMP/changeLog", "softwareRequirements"}
    
    # always applicable
    platforms = {}
    def applicable(self, context):
        return True

    def extract(self, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        state.data["normalized_repo_url"] = (context.repo_url or "").strip().rstrip("/")
        state.data["platform"] = (context.platform or "").strip().lower()
        return state


