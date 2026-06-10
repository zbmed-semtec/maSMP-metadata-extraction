"""Placeholder step for future LLM-based property extraction."""

from typing import Optional

from app.layer_3.steps.contracts import StepContext, StepState


class ExtractLlmPropertyStep:
    """No-op LLM property extraction step until real LLM extraction is implemented."""

    name = "llm.extract_property"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or "llama-3.1-70b-versatile"

    def run(self, context: StepContext, state: StepState) -> StepState:
        """
        Future implementation point for LLM-backed property extraction.

        The configured LLM client/adapter should be injected through the
        constructor, read the current metadata from state.metadata, and write
        extracted candidate values to state.data for later merge steps.
        """
        return state


__all__ = ["ExtractLlmPropertyStep"]

