"""Single pipeline unit for URL normalization and platform flags (not domain property extraction)."""

from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts import StepContext, StepState


class CommonPlatformPreambleStep(ExtractionPlugin):
    """Runs shared non-extract setup: normalized URL and ``state.data[\"platform\"]``."""

    name = "platform.setup_context"
    priority_level = 101
    extracts = {"codemeta:readme", "maSMP:changelog"}
    platforms = {}

    def applicable(self, context):
        return True

    def extract(self, context: StepContext, state: StepState) -> StepState:
        state.data["normalized_repo_url"] = (context.repo_url or "").strip().rstrip("/")
        state.data["platform"] = (context.platform or "").strip().lower() or "github"
        return state

__all__ = ["CommonPlatformPreambleStep"]
