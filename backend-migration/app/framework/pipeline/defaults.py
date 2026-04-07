"""Factories for default pipeline engine + definition bootstrap."""

from pathlib import Path

from app.framework.functions import create_default_function_registry
from app.framework.pipeline.default_pipeline import create_default_pipeline_definition
from app.framework.pipeline.engine import PipelineEngine
from app.framework.pipeline.types import PipelineDefinition
from app.framework.pipeline.yaml_loader import load_pipeline_definition_from_yaml


def create_validated_default_pipeline() -> PipelineDefinition:
    """Build and validate the default pipeline against default function plugins."""
    function_registry = create_default_function_registry()
    engine = PipelineEngine(function_registry=function_registry)
    pipeline = create_default_pipeline_definition()
    engine.validate(pipeline)
    return pipeline


def load_and_validate_pipeline_from_yaml(path: str | Path) -> PipelineDefinition:
    """Load a pipeline from YAML and validate against default function plugins."""
    function_registry = create_default_function_registry()
    engine = PipelineEngine(function_registry=function_registry)
    pipeline = load_pipeline_definition_from_yaml(path)
    engine.validate(pipeline)
    return pipeline
