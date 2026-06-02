"""Run the default README extraction pipeline for in-memory README content."""

from typing import Tuple

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.steps.step_bundles import default_readme_steps


class ReadmeExtractionWorkflow:
    """Orchestrates ``default_readme_steps`` for README text."""

    def __init__(self) -> None:
        self._runner = ExtractionPipelineRunner()
        self._pipeline = ExtractionPipeline(steps=default_readme_steps())

    def run(
        self,
        readme_content: str,
        metadata: SoftwareMetadata,
    ) -> Tuple[SoftwareMetadata, bool]:
        context = StepContext(repo_url="", domain="software", schema="maSMP")
        state = StepState(
            metadata=metadata,
            data={"readme_content": readme_content, "identifier_set_by_readme": False},
        )
        result = self._runner.run(self._pipeline, context, state)
        return result.metadata, bool(result.data.get("identifier_set_by_readme"))


__all__ = ["ReadmeExtractionWorkflow"]
