"""Pipeline contracts and default runner for composable extraction steps."""

from dataclasses import dataclass

from app.layer_3.steps.contracts.step import ExtractionStep, StepContext, StepState
from .progress_observer import ProgressObserver


@dataclass(frozen=True)
class ExtractionPipeline:
    """Ordered extraction pipeline."""

    steps: tuple[ExtractionStep, ...]


class ExtractionPipelineRunner:
    """Executes extraction steps sequentially."""

    def run(self, pipeline: ExtractionPipeline, context: StepContext, state: StepState, progress_observer: ProgressObserver = None) -> StepState:
        current = state
        if progress_observer:
            progress_observer.on_pipeline_started(pipeline)
        for step in pipeline.steps:
            if progress_observer:
                progress_observer.on_step_started(step)
            current = step.run(context, current)
            if progress_observer:
                progress_observer.on_step_completed(step)
        if progress_observer:
            progress_observer.on_pipeline_completed(pipeline)
        return current
