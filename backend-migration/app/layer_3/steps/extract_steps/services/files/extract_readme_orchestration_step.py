"""Apply README property orchestration: file parsing + optional LLM enrichment."""
from __future__ import annotations

from typing import Optional

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.contracts.step import ExtractionStep
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)
from app.config import readme_llm_settings


class ApplyReadmeOrchestrationStep:
    """Run deterministic README extraction and optional LLM-backed enrichment.

    This step keeps README parsing behaviour local (identifiers, bibtex, authors)
    and delegates to the LLM adapter when the feature is enabled in config.
    """

    name = "readme.apply_orchestration"

    def __init__(self, llm_settings=None):
        self.llm_settings = llm_settings or readme_llm_settings

    def run(self, context: StepContext, state: StepState) -> StepState:
        # Ensure README content is available in state.data
        content = repository_file_content(
            context,
            state,
            "readme_content",
            ("README.md", "README.rst", "README.txt", "README"),
        )

        # Run the existing deterministic README workflow to extract identifiers/bibtex/authors
        from app.layer_3.steps.extract_steps.services.files.workflows.readme_extraction_workflow import (
            ReadmeExtractionWorkflow,
        )

        workflow = ReadmeExtractionWorkflow()
        updated_metadata, _identifier_set = workflow.run(content, state.metadata)
        state.metadata = updated_metadata

        # Optional: call LLM extractor to enrich properties
        if self.llm_settings.enabled:
            from app.layer_3.steps.extract_steps.services.llm.llm_extractor import LLMExtractor

            extractor = LLMExtractor(api_key=self.llm_settings.api_key, model=self.llm_settings.model)
            state.metadata = extractor.extract_with_llm(
                state.metadata, repo_url=context.repo_url, extraction_metadata=None
            )

        return state


__all__ = ["ApplyReadmeOrchestrationStep"]
