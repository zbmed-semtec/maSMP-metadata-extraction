"""Pipeline contracts and default runner for composable extraction steps."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.layer_3.steps.contracts.step import ExtractionStep, StepContext, StepState


@dataclass(frozen=True)
class ExtractionPipeline:
    """Ordered extraction pipeline."""

    steps: tuple[ExtractionStep, ...]


class ExtractionPipelineRunner:
    """Executes extraction steps sequentially."""

    def run(
        self,
        pipeline: ExtractionPipeline,
        context: StepContext,
        state: StepState,
        step_progress_callback: Callable[[str, int, int, str], None] | None = None,
    ) -> StepState:
        current = state
        total_steps = len(pipeline.steps)
        for index, step in enumerate(pipeline.steps, start=1):
            if step_progress_callback:
                step_progress_callback(step.name, index, total_steps, "started")
            current = step.run(context, current)
            if step_progress_callback:
                step_progress_callback(step.name, index, total_steps, "completed")
        return current
