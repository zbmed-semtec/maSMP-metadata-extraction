"""Pipeline contracts and default runner for composable extraction steps."""

from dataclasses import dataclass

from app.layer_3.steps.contracts.step import ExtractionStep, StepContext, StepState


@dataclass(frozen=True)
class ExtractionPipeline:
    """Ordered extraction pipeline."""

    steps: tuple[ExtractionStep, ...]


class ExtractionPipelineRunner:
    """Executes extraction steps sequentially."""

    def run(self, pipeline: ExtractionPipeline, context: StepContext, state: StepState) -> StepState:
        current = state
        for step in pipeline.steps:
            current = step._run(context, current)
        return current
