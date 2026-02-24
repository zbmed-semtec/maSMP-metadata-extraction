"""
End-to-end tests for ExtractMetadataUseCase.
Use stubbed dependencies and a simple in-memory collector to verify
step ordering, propagation of metadata, and extraction_metadata contents.
"""
from typing import Optional, Dict, Any, List, Tuple

from app.application.use_cases.extract_metadata import (
    ExtractMetadataUseCase,
    ExtractMetadataResult,
    ExtractionMetadataCollector,
)
from app.core.entities.repository_metadata import RepositoryMetadata


class DummyCollector:
    def __init__(self) -> None:
        self._data: Dict[str, List[tuple[str, float]]] = {}

    def record(self, entity_field: str, source: str, confidence: float) -> None:  # type: ignore[override]
        self._data.setdefault(entity_field, []).append((source, confidence))

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        # Simple aggregation: keep first source and average confidence
        result: Dict[str, Dict[str, Any]] = {}
        for field, entries in self._data.items():
            sources, confidences = zip(*entries)
            result[field] = {
                "source": list(sources),
                "confidence": sum(confidences) / len(confidences),
            }
        return result


class StubPlatformExtractor:
    def extract_platform_metadata(
        self,
        repo_url: str,
        access_token: Optional[str] = None,
        extraction_metadata: Optional[ExtractionMetadataCollector] = None,
    ) -> RepositoryMetadata:
        md = RepositoryMetadata(name="FromPlatform")
        if extraction_metadata is not None:
            extraction_metadata.record("name", "platform", 0.9)
        return md


class StubFileParser:
    def parse_files(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        access_token: Optional[str] = None,
        extraction_metadata: Optional[ExtractionMetadataCollector] = None,
    ) -> Tuple[RepositoryMetadata, Optional[str], bool]:
        metadata.description = "FromFiles"
        if extraction_metadata is not None:
            extraction_metadata.record("description", "files", 0.8)
        # return a DOI and mark that no reference was yet extracted
        return metadata, "10.1234/abcd", False


class StubExternalFetcher:
    def fetch_external_data(
        self,
        repo_url: str,
        metadata: RepositoryMetadata,
        doi: Optional[str] = None,
        reference_extracted: bool = False,
        access_token: Optional[str] = None,
        extraction_metadata: Optional[ExtractionMetadataCollector] = None,
    ) -> RepositoryMetadata:
        metadata.keywords = ["ext"]
        if extraction_metadata is not None:
            extraction_metadata.record("keywords", "external", 0.7)
        return metadata


class StubLLMExtractor:
    def extract_with_llm(
        self,
        metadata: RepositoryMetadata,
        repo_url: str,
        extraction_metadata: Optional[ExtractionMetadataCollector] = None,
    ) -> RepositoryMetadata:
        metadata.alternateName = ["FromLLM"]
        if extraction_metadata is not None:
            extraction_metadata.record("alternateName", "llm", 0.6)
        return metadata


class StubJSONLDBuilder:
    def __init__(self) -> None:
        self.calls: list[tuple[RepositoryMetadata, str, bool]] = []

    def build_jsonld(self, metadata: RepositoryMetadata, schema: str, has_release: bool) -> dict:
        self.calls.append((metadata, schema, has_release))
        return {"schema": schema, "name": metadata.name, "description": metadata.description}


def test_extract_metadata_usecase_happy_path():
    collector = DummyCollector()
    platform = StubPlatformExtractor()
    files = StubFileParser()
    external = StubExternalFetcher()
    llm = StubLLMExtractor()
    builder = StubJSONLDBuilder()

    usecase = ExtractMetadataUseCase(
        platform_extractor=platform,
        file_parser=files,
        external_data_fetcher=external,
        llm_extractor=llm,
        jsonld_builder=builder,
        extraction_metadata_collector=collector,
    )

    progress_steps: list[tuple[str, str]] = []

    def progress(step_id: str, status: str) -> None:
        progress_steps.append((step_id, status))

    result: ExtractMetadataResult = usecase.execute(
        repo_url="https://example.com/repo",
        schema="maSMP",
        access_token=None,
        progress_callback=progress,
    )

    # Verify progress ordering and statuses
    expected_order = ["platform", "file_parsing", "external_data", "llm", "jsonld_build"]
    assert [s for (s, _status) in progress_steps if _status == "started"] == expected_order
    assert [s for (s, _status) in progress_steps if _status == "completed"] == expected_order

    # JSON-LD builder was called with final metadata and schema
    assert builder.calls
    md_called, schema_called, has_release = builder.calls[0]
    assert schema_called == "maSMP"
    assert isinstance(md_called, RepositoryMetadata)

    # JSON-LD output reflects metadata modifications
    assert result.jsonld_document["name"] == "FromPlatform"
    assert result.jsonld_document["description"] == "FromFiles"

    # Extraction metadata was aggregated from all steps
    meta = result.extraction_metadata
    assert "name" in meta and meta["name"]["source"] == ["platform"]
    assert "description" in meta
    assert "keywords" in meta
    assert "alternateName" in meta

