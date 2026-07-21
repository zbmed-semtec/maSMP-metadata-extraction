from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts.step import ExtractionContext, ExtractionState
from app.layer_3.plugins.codeberg.codeberg_client import CodebergClient

class CodebergBaseExtractor(ExtractionPlugin):

    platforms = {'codeberg.org'}
    name = "please.specify.plugin.name"
    extracts = {'please.specify.what.is.being.extracted'}

    def get_client(self, context: ExtractionContext, state: ExtractionState) -> CodebergClient:
        return CodebergClient.get_or_create(context, state)
    