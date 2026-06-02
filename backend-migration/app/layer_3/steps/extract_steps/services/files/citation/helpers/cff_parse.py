"""Load and parse CITATION.cff content into ``StepState.data`` (shared by citation extract steps)."""

from __future__ import annotations

import yaml

from app.layer_3.steps.contracts import StepContext, StepState
from app.layer_3.steps.extract_steps.services.files.helpers.repository_files import (
    repository_file_content,
)

_CFF_YAML_LOADED = "_cff_yaml_loaded"


def ensure_cff_yaml_loaded(context: StepContext, state: StepState) -> None:
    """
    Populate ``valid`` and ``cff_data`` from repository file or pre-injected ``cff_content``.

    Idempotent: safe to call from every citation property extract step.
    """
    if state.data.get(_CFF_YAML_LOADED):
        return
    state.data[_CFF_YAML_LOADED] = True

    cff_content = repository_file_content(
        context,
        state,
        "cff_content",
        ("CITATION.cff", "citation.cff"),
    )
    if not cff_content:
        state.data["valid"] = False
        state.data["cff_data"] = {}
        return
    try:
        cff_data = yaml.safe_load(cff_content)
    except yaml.YAMLError:
        state.data["valid"] = False
        state.data["cff_data"] = {}
        return
    state.data["valid"] = bool(cff_data)
    state.data["cff_data"] = cff_data or {}


__all__ = ["ensure_cff_yaml_loaded"]
