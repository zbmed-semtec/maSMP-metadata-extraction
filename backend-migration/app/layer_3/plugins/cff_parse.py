"""Load and parse CITATION.cff content into ``ExtractionState.data`` (shared by citation extract steps)."""

from __future__ import annotations

import yaml

from app.layer_3.steps.contracts import ExtractionContext, ExtractionState
from app.layer_3.plugins.repository_files import RepositoryFilesPlugin
from app.layer_2.base_plugin import BasePlugin

_CFF_YAML_LOADED = "_cff_yaml_loaded"

class CffParsePlugin(BasePlugin):

    name = "cff-parse-plugin"

    def ensure_cff_yaml_loaded(self, context: ExtractionContext, state: ExtractionState) -> None:
        """
        Populate ``valid`` and ``cff_data`` from repository file or pre-injected ``cff_content``.

        Idempotent: safe to call from every citation property extract step.
        """
        if state.data.get(_CFF_YAML_LOADED):
            return
        state.data[_CFF_YAML_LOADED] = True

        rfp : RepositoryFilesPlugin = self.plugin_manager.get("repository-files-plugin")

        cff_content = rfp.repository_file_content(
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
