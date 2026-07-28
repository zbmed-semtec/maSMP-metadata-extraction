from dataclasses import dataclass
from typing import Protocol
from app.layer_2.contracts.step import ExtractionStep, ExtractionContext, ExtractionState

@dataclass(frozen=True)
class ExtractionPipeline:
    steps: tuple[ExtractionStep, ...]

class PipelineRunner(Protocol):
    def run(self, pipeline: ExtractionPipeline, context: ExtractionContext, state: ExtractionState) -> ExtractionState: ...