"""Pipeline contracts and default runner for composable extraction steps."""

from dataclasses import dataclass
from traceback import print_exc

from app.layer_3.steps.contracts.step import ExtractionStep, ExtractionContext, ExtractionState


@dataclass(frozen=True)
class ExtractionPipeline:
    """Ordered extraction pipeline."""

    steps: tuple[ExtractionStep, ...]


class ExtractionPipelineRunner:
    """Executes extraction steps sequentially."""

    def run(self, pipeline: ExtractionPipeline, context: ExtractionContext, state: ExtractionState) -> ExtractionState:
        current = state
        for step in pipeline.steps:
            try:
                current = step.extract(context, current)
            except Exception as e:
                print_exc()
        return current
