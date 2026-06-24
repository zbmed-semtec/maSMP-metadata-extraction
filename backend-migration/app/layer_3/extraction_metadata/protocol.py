"""Cross-layer metadata collection contract."""

from typing import Any, Dict
from abc import ABC, abstractmethod

class ExtractionMetadataCollector(ABC):
    """Collect per-property extraction provenance metadata."""

    @abstractmethod
    def record(self, entity_field: str, source: str, confidence: float) -> None:
        ...

    @abstractmethod
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        ...
