"""Factories for default pipeline engine + definition bootstrap."""

from app.framework.functions import create_default_function_registry
from app.framework.pipeline.default_pipeline import create_default_pipeline_definition
from app.framework.pipeline.engine import PipelineEngine
from app.framework.pipeline.types import PipelineDefinition


def create_validated_default_pipeline() -> PipelineDefinition:
    """Build and validate the default pipeline against default function plugins."""
    function_registry = create_default_function_registry()
    engine = PipelineEngine(function_registry=function_registry)
    pipeline = create_default_pipeline_definition()
    engine.validate(pipeline)
    return pipeline
