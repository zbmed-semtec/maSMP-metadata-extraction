"""
Tests for multi-source extraction metadata (e.g. keywords: merge from all sources, multiple sources + aggregated confidence).
"""
import pytest

from app.domain.extraction_sources import (
    SOURCE_GITHUB_API,
    SOURCE_CITATION_CFF,
    SOURCE_OPENALEX,
    CONFIDENCE_PLATFORM,
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
)
from app.adapters.extraction_metadata_collector import InMemoryExtractionMetadataCollector


class TestMultiSourceKeywords:
    """Keywords can be contributed by multiple sources; collector stores all and aggregates confidence."""

    def test_keywords_multiple_sources_appended(self):
        collector = InMemoryExtractionMetadataCollector()
        collector.record("keywords", SOURCE_GITHUB_API, CONFIDENCE_PLATFORM)
        collector.record("keywords", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)
        collector.record("keywords", SOURCE_OPENALEX, CONFIDENCE_OPENALEX)
        all_records = collector.get_all()
        assert "keywords" in all_records
        assert all_records["keywords"]["source"] == [
            SOURCE_GITHUB_API,
            SOURCE_CITATION_CFF,
            SOURCE_OPENALEX,
        ]
        # Confidence = average of 1.0, 0.95, 0.9
        assert all_records["keywords"]["confidence"] == pytest.approx(0.95, abs=0.01)

    def test_single_source_property_still_overwrites(self):
        collector = InMemoryExtractionMetadataCollector()
        collector.record("name", SOURCE_GITHUB_API, CONFIDENCE_PLATFORM)
        collector.record("name", SOURCE_CITATION_CFF, CONFIDENCE_CITATION)  # would overwrite in old impl
        all_records = collector.get_all()
        # Single-source property: last writer wins (current design)
        assert all_records["name"]["source"] == SOURCE_CITATION_CFF
        assert all_records["name"]["confidence"] == CONFIDENCE_CITATION
