from __future__ import annotations
from typing import Any, Dict, List

from app.layer_1.provenance.software.sources import MULTI_SOURCE_PROPERTIES


def _dedupe_source_entries(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set[str] = set()
    deduped: List[Dict[str, Any]] = []
    for entry in entries:
        source = entry.get("source")
        if source in seen:
            continue
        seen.add(source)
        deduped.append(entry)
    return deduped


def _aggregate_confidence(entries: List[Dict[str, Any]]) -> float:
    if not entries:
        return 0.0
    total = sum(e.get("confidence", 0) for e in entries)
    return round(total / len(entries), 2)


class InMemoryExtractionMetadataCollector:
    def __init__(self) -> None:
        self._records: Dict[str, Any] = {}

    def record(self, entity_field: str, source: str, confidence: float) -> None:
        rounded = round(confidence, 2)
        if entity_field in MULTI_SOURCE_PROPERTIES:
            if entity_field not in self._records:
                self._records[entity_field] = []
            self._records[entity_field].append({"source": source, "confidence": rounded})
        else:
            self._records[entity_field] = {"source": source, "confidence": rounded}

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        result: Dict[str, Dict[str, Any]] = {}
        for field, value in self._records.items():
            if isinstance(value, list):
                entries = _dedupe_source_entries(value)
                result[field] = {
                    "source": [e["source"] for e in entries],
                    "confidence": _aggregate_confidence(entries),
                }
            else:
                result[field] = dict(value)
        return result


__all__ = ["InMemoryExtractionMetadataCollector"]
