"""Runtime pipeline selection helpers (default vs YAML)."""

from dataclasses import dataclass
from typing import Optional

from app.framework.pipeline.defaults import (
    create_validated_default_pipeline,
    load_and_validate_pipeline_from_yaml,
)
from app.framework.pipeline.types import PipelineDefinition


@dataclass(frozen=True)
class PipelineRuntimeConfig:
    """Configuration for selecting the active pipeline definition."""

    yaml_path: Optional[str] = None


def resolve_pipeline_definition(config: Optional[PipelineRuntimeConfig] = None) -> PipelineDefinition:
    """Return validated pipeline from config, defaulting to built-in 5-step pipeline."""
    config = config or PipelineRuntimeConfig()
    if config.yaml_path:
        return load_and_validate_pipeline_from_yaml(config.yaml_path)
    return create_validated_default_pipeline()
