"""Pipeline engine (validation-first scaffold)."""

from typing import Any, Callable, Dict, Optional

from app.framework.functions.plugin import FunctionContext
from app.framework.functions.registry import FunctionRegistry
from app.framework.pipeline.types import PipelineDefinition, PipelineStep


class PipelineValidationError(ValueError):
    """Raised when a pipeline definition is invalid."""


class PipelineExecutionError(RuntimeError):
    """Raised when pipeline execution fails."""


class PipelineEngine:
    """
    Validation-first pipeline engine.

    This scaffold validates plugin references and supports basic sequential
    execution over registered function plugins.
    """

    def __init__(self, function_registry: FunctionRegistry) -> None:
        self._function_registry = function_registry

    def validate(self, pipeline: PipelineDefinition) -> None:
        """Validate plugin existence, unique step IDs, and simple wiring."""
        if not pipeline.steps:
            raise PipelineValidationError("Pipeline must define at least one step")

        seen_ids: set[str] = set()
        available_keys: set[str] = set()

        for step in pipeline.steps:
            self._validate_step_id(step, seen_ids)
            self._validate_plugin_exists(step)
            self._validate_input_wiring(step, available_keys)
            available_keys.update(step.outputs)

    def execute(
        self,
        pipeline: PipelineDefinition,
        initial_payload: Optional[Dict[str, Any]] = None,
        initial_metadata: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[str, str], None]] = None,
    ) -> Dict[str, Any]:
        """Execute pipeline sequentially and return the final payload context."""
        self.validate(pipeline)

        payload: Dict[str, Any] = dict(initial_payload or {})
        metadata: Dict[str, Any] = dict(initial_metadata or {})

        for step in pipeline.steps:
            plugin = self._function_registry.require(step.plugin_id)
            if progress_callback:
                progress_callback(step.id, "started")
            try:
                result = plugin.run(FunctionContext(payload=payload, metadata=metadata))
            except Exception as exc:
                raise PipelineExecutionError(
                    f"Step '{step.id}' failed while running plugin '{step.plugin_id}'"
                ) from exc

            payload.update(result.payload)
            metadata.update(result.metadata)

            if progress_callback:
                progress_callback(step.id, "completed")

        return payload

    def _validate_step_id(self, step: PipelineStep, seen_ids: set[str]) -> None:
        if step.id in seen_ids:
            raise PipelineValidationError(f"Duplicate pipeline step id '{step.id}'")
        seen_ids.add(step.id)

    def _validate_plugin_exists(self, step: PipelineStep) -> None:
        if self._function_registry.get(step.plugin_id) is None:
            raise PipelineValidationError(
                f"Step '{step.id}' references unknown plugin '{step.plugin_id}'"
            )

    def _validate_input_wiring(self, step: PipelineStep, available_keys: set[str]) -> None:
        # Inputs may be supplied by pipeline start context or previous steps.
        missing = [key for key in step.inputs if key not in available_keys]
        if not missing:
            return
        if len(available_keys) == 0:
            return
        missing_csv = ", ".join(sorted(set(missing)))
        raise PipelineValidationError(
            f"Step '{step.id}' has unresolved inputs: {missing_csv}"
        )
