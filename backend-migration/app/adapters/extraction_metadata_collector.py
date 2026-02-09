"""
Layer 3: Adapters
In-memory implementation of ExtractionMetadataCollector.
Stores per-property source and confidence for UI enrichment.
"""
from typing import Dict, Any


class InMemoryExtractionMetadataCollector:
    """
    Collects extraction metadata (source, confidence) per entity field.
    Last writer wins when the same field is set by multiple extractors.
    """

    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, Any]] = {}

    def record(self, entity_field: str, source: str, confidence: float) -> None:
        """Record that a property was set by the given source with the given confidence."""
        self._records[entity_field] = {
            "source": source,
            "confidence": round(confidence, 2),
        }

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Return all records: entity_field -> {source, confidence}."""
        return dict(self._records)
