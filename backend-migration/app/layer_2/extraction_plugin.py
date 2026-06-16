from abc import ABC, abstractmethod, abstractproperty
from app.layer_2.base_plugin import BasePlugin
from app.layer_3.steps.contracts.step import ExtractionStep, StepContext, StepState

class ExtractionPlugin(BasePlugin, ExtractionStep, ABC):
    
    @property
    @abstractmethod
    def name():
        ...

    @abstractmethod
    def extract(self, context, state):
        ...

    def applicable(self, context : StepContext):
        return context.platform in self.platforms