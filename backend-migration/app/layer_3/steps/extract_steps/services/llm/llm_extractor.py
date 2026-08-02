"""Compatibility adapter for future LLM-backed extraction."""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.steps.extract_steps.services.llm.extract_llm_property_step import (
    ExtractLlmPropertyStep,
)
from app.layer_3.utils.url_pattern_matcher import URLPatternMatcher

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
        platform = URLPatternMatcher.detect_platform(repo_url)
        if platform not in {"github", "gitlab"}:
            raise ValueError("Unsupported repository platform. Supported: GitHub, GitLab")

        context = StepContext(
            repo_url=repo_url,
            domain="software",
            schema="",
            platform=platform,
        )
        state = StepState(metadata=metadata)
        return ExtractionPipelineRunner().run(pipeline, context, state).metadata


__all__ = ["LLMExtractor"]
