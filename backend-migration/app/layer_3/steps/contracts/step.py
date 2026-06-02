"""Common step contracts for modular Layer 3 extraction pipelines."""

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol
from .callback_offer import CallbackOffer

@dataclass(frozen=True)
class StepContext:
    """
    Immutable context used by extraction steps.

    This is intentionally lightweight for Phase 1. It can be extended with
    domain/schema/platform-specific runtime dependencies over time.
    """

    repo_url: str
    domain: str
    schema: str
    platform: Optional[str] = None
    access_token: Optional[str] = None


@dataclass
class StepState:
    """
    Mutable state that flows across extraction steps.

    Attributes:
      metadata: current aggregate being enriched.
      data: step-local scratchpad for intermediate values.
    """

    metadata: Any 
    data: dict[str, Any] = field(default_factory=dict)


class ExtractionStep(Protocol):
    """
    Small, composable unit of extraction behavior.

    Naming convention:
    - Extract*Step lives under extract_steps/ and stores normalized values in state.data.
    - Merge*Step lives under merge_steps/ and applies state.data values to state.metadata.
    - Apply*Step may write directly when there is no separate extraction phase.
    - Reusable helper functions live under helpers/, not beside steps.
    - Step files use the snake_case version of the class name with the
      trailing `_step` suffix, e.g. ExtractCitationAuthorsStep lives in
      extract_citation_authors_step.py.

    Extract step names should include the source scope, such as
    "citation.extract_authors". Merge step names should include the target
    domain and property, such as "software.merge_authors".
    """

    name: str
    
    def __init__(self):
        self.on_before_run = CallbackOffer()
        self.on_after_run = CallbackOffer()

    def _run(self, context: StepContext, state: StepState) -> StepState:
        self.on_before_run.callback(self.name, 'started')
        result = self.run(context, state)  # type: ignore
        self.on_after_run.callback(self.name, 'completed')
        return result

    def run(self, context: StepContext, state: StepState) -> StepState:
        """Apply this step and return updated state."""
        ...
