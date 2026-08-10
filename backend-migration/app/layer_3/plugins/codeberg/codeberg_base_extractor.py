from abc import ABC
from app.layer_3.plugins.shared.git_platform_base_extractor import GitPlatformBaseExtractor
from app.layer_3.steps.contracts.step import ExtractionContext, ExtractionState
from app.layer_3.plugins.codeberg.codeberg_client import CodebergClient

class CodebergBaseExtractor(GitPlatformBaseExtractor, ABC):

    platforms = {'codeberg.org'}
    name = "please.specify.plugin.name"
    extracts = {'please.specify.what.is.being.extracted'}

    def get_client(self, context: ExtractionContext, state: ExtractionState) -> CodebergClient:
        return CodebergClient.get_or_create(context, state)
    