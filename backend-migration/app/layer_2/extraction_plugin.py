from abc import ABC, abstractmethod, abstractproperty
from app.layer_2.base_plugin import BasePlugin
from app.layer_2.contracts import ExtractionStep, ExtractionContext

class ExtractionPlugin(BasePlugin, ExtractionStep, ABC):
    
    @property
    @abstractmethod
    def name():
        ...

    @abstractmethod
    def extract(self, context, state):
        ...

    def applicable(self, context : ExtractionContext):
        return any([platform in context.platform for platform in self.platforms])