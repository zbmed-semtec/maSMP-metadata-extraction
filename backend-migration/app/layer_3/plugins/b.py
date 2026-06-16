"""Extract authors from CITATION.cff into step state."""

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.citation.helpers import ensure_cff_yaml_loaded
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.plugins.a import PluginA

class PluginB(ExtractionPlugin):
    """Extract top-level CFF authors without mutating metadata."""

    name = "test.plugin.b"
    label = "implementing method x"
    extracts = {'friendship', 'hate'} # nothing
    platforms = {'github'} # don't care
    aliases = {'b'}

    def extract(self, prop: str, context: StepContext, state: StepState) -> StepState:
        if prop == 'friendship':
            print("this is b!")
            print("im going to ask my friend plugin out!")
            a : PluginA = self.plugin_manager.get('test.plugin.a')
            print('now im calling it now!')
            print("a says:", a.x())
        elif prop == 'hate':
            print("this is b!")
            print("im going to ask my most-hated plugin out!")
            a : PluginA = self.plugin_manager.get('a')
            print('now im calling it now!')
            print("a says:", a.x())

__all__ = ["PluginB"]

