"""
End-to-end tests for ExtractMetadataUseCase.
Use stubbed dependencies and a simple in-memory collector to verify
step ordering, propagation of metadata, and extraction_metadata contents.
"""
from __future__ import annotations
from typing import Dict, Any, List

from app.layer_2.use_cases.extract_metadata import (
    ExtractMetadataUseCase,
    ExtractMetadataResult,
)
from app.layer_1.entities.software_metadata import SoftwareMetadata
from app.layer_3.steps.contracts import ExtractionPipeline


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


class StubComposer:
    def compose(self, *, domain: str, schema: str, platform: str | None = None) -> ExtractionPipeline:
        assert domain == "software"
        assert platform == "github"
        return ExtractionPipeline(steps=())


class StubPipelineRunner:
    def run(
        self,
        pipeline: ExtractionPipeline,
        context,
        state,
    ):
        state.metadata.name = "FromPlatform"
        state.metadata.description = "FromFiles"
        state.metadata.keywords = ["ext"]
        state.metadata.alternateName = ["FromLLM"]
        state.data["record_field"]("name")
        state.data["record_field"]("description")
        state.data["record_field"]("keywords")
        state.data["record_field"]("alternateName")
        return state


class StubJSONLDBuilder:
    def __init__(self) -> None:
        self.calls: list[tuple[SoftwareMetadata, str, bool]] = []

    def build_jsonld(self, metadata: SoftwareMetadata, schema: str, has_release: bool) -> dict:
        self.calls.append((metadata, schema, has_release))
        return {"schema": schema, "name": metadata.name, "description": metadata.description}


def test_extract_metadata_usecase_happy_path():
    collector = DummyCollector()
    runner = StubPipelineRunner()
    builder = StubJSONLDBuilder()

    usecase = ExtractMetadataUseCase(
        jsonld_builder=builder,
        pipeline_composer=StubComposer(),
        pipeline_runner=runner,
        extraction_metadata_collector=collector,
    )

    progress_steps: list[tuple[str, str]] = []

    def progress(step_id: str, status: str) -> None:
        progress_steps.append((step_id, status))

    result: ExtractMetadataResult = usecase.execute(
        repo_url="https://github.com/org/repo",
        schema="maSMP",
        access_token=None,
        progress_callback=progress,
    )

    # Verify progress ordering and statuses
    expected_order = ["pipeline", "jsonld_build"]
    assert [s for (s, _status) in progress_steps if _status == "started"] == expected_order
    assert [s for (s, _status) in progress_steps if _status == "completed"] == expected_order

    # JSON-LD builder was called with final metadata and schema
    assert builder.calls
    md_called, schema_called, has_release = builder.calls[0]
    assert schema_called == "maSMP"
    assert isinstance(md_called, SoftwareMetadata)

    # JSON-LD output reflects metadata modifications
    assert result.jsonld_document["name"] == "FromPlatform"
    assert result.jsonld_document["description"] == "FromFiles"

    # Internal metadata is exposed for downstream services (e.g. FAIRness)
    assert isinstance(result.metadata, SoftwareMetadata)
    assert result.metadata.name == "FromPlatform"

    # Extraction metadata was aggregated from all steps
    meta = result.extraction_metadata
    assert "name" in meta and meta["name"]["source"] == ["github_api"]
    assert "description" in meta
    assert "keywords" in meta
    assert "alternateName" in meta

