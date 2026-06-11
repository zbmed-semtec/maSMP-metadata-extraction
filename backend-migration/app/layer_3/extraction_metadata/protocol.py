"""Cross-layer metadata collection contract."""
from __future__ import annotations

from typing import Any, Dict, Protocol


class ExtractionMetadataCollector(Protocol):
    """Collect per-property extraction provenance metadata."""

    def record(self, entity_field: str, source: str, confidence: float) -> None:
        ...

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        ...
