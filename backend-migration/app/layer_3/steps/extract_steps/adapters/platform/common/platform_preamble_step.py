"""Single pipeline unit for URL normalization and platform flags (not domain property extraction)."""
from __future__ import annotations

from app.layer_3.steps.contracts import StepContext, StepState


class CommonPlatformPreambleStep:
    """Runs shared non-extract setup: normalized URL and ``state.data[\"platform\"]``."""

    name = "platform.setup_context"

    def run(self, context: StepContext, state: StepState) -> StepState:
        state.data["normalized_repo_url"] = (context.repo_url or "").strip().rstrip("/")
        state.data["platform"] = (context.platform or "").strip().lower() or "github"
        return state


__all__ = ["CommonPlatformPreambleStep"]
