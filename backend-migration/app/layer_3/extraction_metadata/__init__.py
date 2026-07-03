"""Extraction provenance: protocol and default in-memory collector."""

from app.layer_3.extraction_metadata.protocol import ExtractionMetadataCollector

__all__ = [
    "ExtractionMetadataCollector",
    "InMemoryExtractionMetadataCollector",
]
