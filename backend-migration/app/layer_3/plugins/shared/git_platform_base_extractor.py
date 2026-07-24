from abc import ABC, abstractmethod
from app.layer_2.extraction_plugin import ExtractionPlugin
from app.layer_3.steps.contracts.step import ExtractionContext, ExtractionState
from app.layer_3.plugins.shared.git_platform_client import GitPlatformClient

class GitPlatformBaseExtractor(ExtractionPlugin, ABC):
    @abstractmethod
    def get_client(self, context : ExtractionContext, state: ExtractionState) -> GitPlatformClient:
        ...