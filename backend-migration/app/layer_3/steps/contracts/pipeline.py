from traceback import print_exc
from app.layer_2.contracts.pipeline import ExtractionPipeline
from app.layer_2.contracts.step import ExtractionContext, ExtractionState

class ExtractionPipelineRunner:
    """Implements app.layer_2.contracts.pipeline.PipelineRunner (structural typing, no inheritance needed)."""
    def run(self, pipeline, context, state):
        current = state
        for step in pipeline.steps:
            try:
                current = step.extract(context, current)
            except Exception:
                print_exc()
        return current