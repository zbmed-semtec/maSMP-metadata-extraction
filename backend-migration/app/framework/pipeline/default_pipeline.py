"""Default backward-compatible 5-step pipeline definition."""

from app.framework.pipeline.types import PipelineDefinition, PipelineStep


def create_default_pipeline_definition() -> PipelineDefinition:
    """Return the default extraction pipeline matching the current 5-step flow."""
    return PipelineDefinition(
        id="default_metadata_extraction",
        steps=(
            PipelineStep(
                id="platform",
                plugin_id="platform_extraction",
                inputs=("repo_url", "access_token"),
                outputs=("metadata",),
            ),
            PipelineStep(
                id="file_parsing",
                plugin_id="file_parsing",
                inputs=("repo_url", "metadata", "access_token"),
                outputs=("metadata", "doi", "reference_extracted"),
            ),
            PipelineStep(
                id="external_data",
                plugin_id="external_enrichment",
                inputs=("repo_url", "metadata", "doi", "reference_extracted", "access_token"),
                outputs=("metadata",),
            ),
            PipelineStep(
                id="llm",
                plugin_id="llm_enrichment",
                inputs=("repo_url", "metadata"),
                outputs=("metadata",),
            ),
            PipelineStep(
                id="jsonld_build",
                plugin_id="schema_build",
                inputs=("metadata", "schema"),
                outputs=("jsonld_document",),
            ),
        ),
        metadata={"version": 1, "compatibility": "legacy-5-step"},
    )
