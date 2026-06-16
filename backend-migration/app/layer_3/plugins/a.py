"""Extract authors from CITATION.cff into step state."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded
from app.layer_2.base_plugin import BasePlugin

class PluginA(BasePlugin):
    """Extract top-level CFF authors without mutating metadata."""

    name = "test.plugin.a"
    label = "implementing method x"
    extracts = {} # nothing
    platforms = {} # don't care
    aliases = {'a'}

    def extract(self, prop: str, context: StepContext, state: StepState) -> StepState:
        return None

    def x(self):
        return "you called me!"

__all__ = ["PluginA"]

