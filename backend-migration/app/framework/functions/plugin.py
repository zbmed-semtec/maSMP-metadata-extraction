"""Function plugin contract and execution context types."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol


RetryPolicy = Dict[str, Any]


@dataclass(frozen=True)
class FunctionContext:
    """Execution context passed to function plugins."""

    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FunctionResult:
    """Standardized function plugin output."""

    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FunctionPlugin(Protocol):
    """Contract for pluggable pipeline functions."""

    id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    retry_policy: Optional[RetryPolicy]
    plugin_metadata: Dict[str, Any]

    def run(self, context: FunctionContext) -> FunctionResult:
        """Execute plugin logic using context and return normalized output."""
        ...
