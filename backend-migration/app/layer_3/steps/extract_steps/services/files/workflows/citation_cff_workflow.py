"""Run the default CITATION.cff extraction pipeline for in-memory file content."""
from __future__ import annotations

from typing import Callable, Optional

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, StepContext, StepState
from app.layer_3.steps.extract_steps.adapters.platform.github.extract_github_metadata_files_step import (
    github_readme_changelog_link_steps,
)
from app.layer_3.steps.extract_steps.adapters.platform.gitlab.extract_gitlab_metadata_files_step import (
    gitlab_readme_changelog_link_steps,
)
from app.layer_3.steps.step_bundles import default_citation_steps


class CitationCffWorkflow:
    """Orchestrates ``default_citation_steps`` for a CFF string plus optional platform link steps."""

    def __init__(self) -> None:
        self._runner = ExtractionPipelineRunner()
        self._pipeline = ExtractionPipeline(steps=default_citation_steps())

    def run(
        self,
        cff_content: str,
        metadata: SoftwareMetadata,
        *,
        repo_url: str = "",
        platform: str | None = None,
        is_file_reachable_fn: Callable[[str], bool] | None = None,
    ) -> tuple[SoftwareMetadata, Optional[str], bool]:
        context = StepContext(
            repo_url=repo_url,
            domain="software",
            schema="maSMP",
            platform=platform,
            access_token=None,
        )
        state = StepState(
            metadata=metadata,
            data={
                "cff_content": cff_content,
                "doi": None,
                "reference_extracted": False,
                "is_file_reachable_fn": is_file_reachable_fn,
            },
        )
        pipeline = self._pipeline
        if platform == "github":
            pipeline = ExtractionPipeline(
                steps=self._pipeline.steps + github_readme_changelog_link_steps()
            )
        elif platform == "gitlab":
            pipeline = ExtractionPipeline(
                steps=self._pipeline.steps + gitlab_readme_changelog_link_steps()
            )
        result = self._runner.run(pipeline, context, state)
        if not result.data.get("valid"):
            return metadata, None, False
        return (result.metadata, result.data.get("doi"), bool(result.data.get("reference_extracted")))


__all__ = ["CitationCffWorkflow"]
