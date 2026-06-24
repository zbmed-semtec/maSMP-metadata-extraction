"""Tests for per-source provenance recording in merge steps."""

from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_1.provenance.software.defaults import (
    CONFIDENCE_CITATION,
    CONFIDENCE_OPENALEX,
    CONFIDENCE_PLATFORM,
    CONFIDENCE_README,
    SOURCE_CITATION_CFF,
    SOURCE_GITHUB_API,
    SOURCE_OPENALEX,
    SOURCE_README_PARSER,
    SOURCE_SOFTWARE_HERITAGE,
    SOURCE_WAYBACK,
    SOURCE_ZENODO_BADGE,
)
from app.layer_3.extraction_metadata import InMemoryExtractionMetadataCollector
from app.layer_3.steps.contracts import ExtractionPipeline, ExtractionPipelineRunner, ExtractionContext, ExtractionState
from app.layer_3.steps.merge_steps.software import (
    MergeSoftwareArchivedUrlsStep,
    MergeSoftwareAuthorsStep,
    MergeSoftwareCitationEntriesStep,
    MergeSoftwareKeywordsStep,
)
from app.layer_4.builders.enriched_metadata import build_enriched_metadata


def _record_field(collector: InMemoryExtractionMetadataCollector):
    def record(field: str, *, source=None, confidence=None):
        collector.record(
            field,
            source if source is not None else SOURCE_GITHUB_API,
            confidence if confidence is not None else CONFIDENCE_PLATFORM,
        )

    return record


def test_merge_authors_records_each_contributing_source():
    collector = InMemoryExtractionMetadataCollector()
    state = ExtractionState(
        metadata=SoftwareMetadata(),
        data={
            "record_field": _record_field(collector),
            "extracted_citation_authors": [{"familyName": "A", "givenName": "B"}],
            "all_readme_authors": [{"familyName": "C", "givenName": "D"}],
            "extracted_openalex_authors": [{"familyName": "E", "givenName": "F"}],
        },
    )
    context = ExtractionContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )

    MergeSoftwareAuthorsStep().run(context, state)
    meta = collector.get_all()["author"]

    assert meta["source"] == [SOURCE_CITATION_CFF, SOURCE_README_PARSER, SOURCE_OPENALEX]
    assert meta["confidence"] == round(
        (CONFIDENCE_CITATION + CONFIDENCE_README + CONFIDENCE_OPENALEX) / 3,
        2,
    )


def test_merge_keywords_records_platform_and_openalex_without_duplicates():
    collector = InMemoryExtractionMetadataCollector()
    state = ExtractionState(
        metadata=SoftwareMetadata(),
        data={
            "record_field": _record_field(collector),
            "extracted_platform_keywords": ["python"],
            "extracted_openalex_keywords": ["research"],
        },
    )
    context = ExtractionContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )

    MergeSoftwareKeywordsStep().run(context, state)
    meta = collector.get_all()["keywords"]

    assert meta["source"] == [SOURCE_GITHUB_API, SOURCE_OPENALEX]
    assert "python" in state.metadata.keywords
    assert "research" in state.metadata.keywords


def test_merge_citation_entries_records_citation_field():
    collector = InMemoryExtractionMetadataCollector()
    state = ExtractionState(
        metadata=SoftwareMetadata(),
        data={
            "record_field": _record_field(collector),
            "extracted_top_level_citation_entry": {"@type": "Article", "title": "Paper"},
        },
    )
    context = ExtractionContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )

    MergeSoftwareCitationEntriesStep().run(context, state)
    meta = collector.get_all()["citation"]

    assert meta["source"] == SOURCE_CITATION_CFF
    assert meta["confidence"] == CONFIDENCE_CITATION


def test_enriched_metadata_maps_citation_and_software_requirements():
    jsonld = {
        "maSMP:SoftwareSourceCode": {
            "@context": ["https://w3id.org/maSMP/"],
            "@type": "SoftwareSourceCode",
            "citation": [{"@type": "Article"}],
            "softwareRequirements": ["https://github.com/org/repo/blob/main/requirements.txt"],
        }
    }
    extraction_metadata = {
        "citation": {"source": SOURCE_CITATION_CFF, "confidence": CONFIDENCE_CITATION},
        "softwareRequirements": {"source": SOURCE_GITHUB_API, "confidence": CONFIDENCE_PLATFORM},
    }

    enriched = build_enriched_metadata(jsonld, extraction_metadata, "maSMP")
    profile = enriched["maSMP:SoftwareSourceCode"]

    assert profile["citation"]["source"] == SOURCE_CITATION_CFF
    assert profile["citation"]["confidence"] == CONFIDENCE_CITATION
    assert profile["softwareRequirements"]["source"] == SOURCE_GITHUB_API
    assert profile["softwareRequirements"]["confidence"] == CONFIDENCE_PLATFORM


def test_merge_archived_urls_records_each_archive_source():
    collector = InMemoryExtractionMetadataCollector()
    state = ExtractionState(
        metadata=SoftwareMetadata(),
        data={
            "record_field": _record_field(collector),
            "extracted_zenodo_archive_urls": ["https://zenodo.org/record/1"],
            "extracted_software_heritage_archive_url": "https://archive.softwareheritage.org/1",
            "extracted_wayback_archive_url": "https://web.archive.org/web/example",
        },
    )
    context = ExtractionContext(
        repo_url="https://github.com/org/repo",
        domain="software",
        schema="CODEMETA",
        platform="github",
    )

    MergeSoftwareArchivedUrlsStep().run(context, state)
    meta = collector.get_all()["archivedAt"]

    assert meta["source"] == [SOURCE_ZENODO_BADGE, SOURCE_SOFTWARE_HERITAGE, SOURCE_WAYBACK]
