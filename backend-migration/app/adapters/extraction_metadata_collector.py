"""
Layer 3: Adapters
In-memory implementation of ExtractionMetadataCollector.
Stores per-property source and confidence for UI enrichment.
"""
from typing import Dict, Any, List

from app.domain.property_extraction_sources import MULTI_SOURCE_PROPERTIES


def _aggregate_confidence(entries: List[Dict[str, Any]]) -> float:
    """Aggregate confidence when multiple sources contribute (e.g. average)."""
    if not entries:
        return 0.0
    total = sum(e.get("confidence", 0) for e in entries)
    return round(total / len(entries), 2)


class InMemoryExtractionMetadataCollector:
    """
    Collects extraction metadata (source, confidence) per entity field.
    For single-source properties: last writer wins.
    For multi-source properties (e.g. keywords): each source appends;
    get_all() returns combined sources and aggregated confidence.
    """

    def __init__(self) -> None:
        self._records: Dict[str, Any] = {}  # field -> {source, confidence} or list of same

    def record(self, entity_field: str, source: str, confidence: float) -> None:
        """Record that a property was set by the given source with the given confidence."""
        rounded = round(confidence, 2)
        if entity_field in MULTI_SOURCE_PROPERTIES:
            if entity_field not in self._records:
                self._records[entity_field] = []
            self._records[entity_field].append({"source": source, "confidence": rounded})
        else:
            self._records[entity_field] = {"source": source, "confidence": rounded}

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Return all records: entity_field -> {source, confidence}.
        For multi-source properties, source is a list and confidence is aggregated (average).
        """
        result: Dict[str, Dict[str, Any]] = {}
        for field, value in self._records.items():
            if isinstance(value, list):
                result[field] = {
                    "source": [e["source"] for e in value],
                    "confidence": _aggregate_confidence(value),
                }
            else:
                result[field] = dict(value)
        return result
