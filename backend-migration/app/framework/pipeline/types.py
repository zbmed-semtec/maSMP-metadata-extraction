"""Core pipeline definition types."""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class PipelineStep:
    """A single pipeline step bound to a function plugin ID."""

    id: str
    plugin_id: str
    inputs: Tuple[str, ...] = field(default_factory=tuple)
    outputs: Tuple[str, ...] = field(default_factory=tuple)
    config: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineDefinition:
    """Ordered pipeline definition with optional metadata."""

    id: str
    steps: Tuple[PipelineStep, ...]
    metadata: Dict[str, object] = field(default_factory=dict)
