"""Compatibility adapter for future LLM-backed extraction."""

from typing import Optional, TYPE_CHECKING

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.steps.extract_steps.services.llm.extract_llm_property_step import (
    ExtractLlmPropertyStep,
)

if TYPE_CHECKING:
    from app.layer_3.extraction_metadata import ExtractionMetadataCollector


class LLMExtractor:
    """Thin adapter around the placeholder LLM extraction step."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model

    def extract_with_llm(
        self,
        metadata: SoftwareMetadata,
        repo_url: str,
        extraction_metadata: Optional["ExtractionMetadataCollector"] = None,
    ) -> SoftwareMetadata:
        pipeline = ExtractionPipeline(
            steps=(ExtractLlmPropertyStep(api_key=self.api_key, model=self.model),)
        )
        context = StepContext(
            repo_url=repo_url,
            domain="software",
            schema="",
        )
        state = StepState(metadata=metadata)
        return ExtractionPipelineRunner().run(pipeline, context, state).metadata


__all__ = ["LLMExtractor"]

