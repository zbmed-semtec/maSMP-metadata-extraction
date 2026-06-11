"""Extraction provenance: protocol and default in-memory collector."""
from __future__ import annotations

from app.layer_3.extraction_metadata.in_memory import InMemoryExtractionMetadataCollector
from app.layer_3.extraction_metadata.protocol import ExtractionMetadataCollector

__all__ = [
    "ExtractionMetadataCollector",
    "InMemoryExtractionMetadataCollector",
]
