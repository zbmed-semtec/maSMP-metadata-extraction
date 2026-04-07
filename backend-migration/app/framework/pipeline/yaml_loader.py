"""Optional YAML loader for pipeline definitions."""

from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import yaml

from app.framework.pipeline.types import PipelineDefinition, PipelineStep


def _as_tuple_of_strings(value: Any) -> Tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        raise ValueError("Expected a list of strings")
    result = tuple(str(item) for item in value)
    return result


def _parse_step(raw_step: Dict[str, Any], index: int) -> PipelineStep:
    if not isinstance(raw_step, dict):
        raise ValueError(f"Step at index {index} must be an object")

    step_id = str(raw_step.get("id", "")).strip()
    plugin_id = str(raw_step.get("plugin_id", "")).strip()
    if not step_id:
        raise ValueError(f"Step at index {index} is missing 'id'")
    if not plugin_id:
        raise ValueError(f"Step '{step_id}' is missing 'plugin_id'")

    config = raw_step.get("config", {})
    if config is None:
        config = {}
    if not isinstance(config, dict):
        raise ValueError(f"Step '{step_id}' has non-object 'config'")

    return PipelineStep(
        id=step_id,
        plugin_id=plugin_id,
        inputs=_as_tuple_of_strings(raw_step.get("inputs")),
        outputs=_as_tuple_of_strings(raw_step.get("outputs")),
        config=config,
    )


def load_pipeline_definition_from_yaml(path: str | Path) -> PipelineDefinition:
    """Load a `PipelineDefinition` from YAML file."""
    pipeline_path = Path(path)
    raw = yaml.safe_load(pipeline_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Pipeline YAML root must be an object")

    pipeline_id = str(raw.get("id", "")).strip()
    if not pipeline_id:
        raise ValueError("Pipeline YAML is missing required top-level 'id'")

    raw_steps = raw.get("steps", [])
    if not isinstance(raw_steps, list):
        raise ValueError("Pipeline YAML field 'steps' must be a list")

    steps = tuple(_parse_step(step, idx) for idx, step in enumerate(raw_steps))

    metadata = raw.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("Pipeline YAML field 'metadata' must be an object")

    return PipelineDefinition(id=pipeline_id, steps=steps, metadata=metadata)
