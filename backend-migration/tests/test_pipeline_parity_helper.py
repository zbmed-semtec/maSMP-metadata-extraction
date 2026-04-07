from app.application.use_cases.extract_metadata import ExtractMetadataResult
from app.framework.api import metadata_runtime


class _StubUseCase:
    def __init__(self, result: ExtractMetadataResult) -> None:
        self._result = result

    def execute(self, **kwargs):  # type: ignore[no-untyped-def]
        return self._result


def test_compare_legacy_and_pipeline_extraction_match(monkeypatch):
    legacy_result = ExtractMetadataResult(
        jsonld_document={"name": "demo"},
        extraction_metadata={"name": {"source": "platform", "confidence": 0.9}},
        metadata=object(),  # not used because _build_jsonld_via_plugin is patched
    )

    monkeypatch.setattr(
        metadata_runtime,
        "canonical_schema_name",
        lambda registry, schema: schema,
    )
    monkeypatch.setattr(
        metadata_runtime,
        "create_extraction_use_case",
        lambda repo_url, access_token, with_enrichment: (_StubUseCase(legacy_result), None),
    )
    monkeypatch.setattr(
        metadata_runtime,
        "_build_jsonld_via_plugin",
        lambda metadata, schema, fallback_jsonld: fallback_jsonld,
    )
    monkeypatch.setattr(
        metadata_runtime,
        "run_extraction_via_pipeline",
        lambda repo_url, schema, access_token: (
            {"name": "demo"},
            {"name": {"source": "platform", "confidence": 0.9}},
        ),
    )
    monkeypatch.setattr(
        metadata_runtime,
        "_build_enriched_metadata_via_plugin",
        lambda jsonld_document, extraction_metadata, schema: {"profile": {"name": {}}},
    )

    result = metadata_runtime.compare_legacy_and_pipeline_extraction(
        repo_url="https://example.com/repo",
        schema="maSMP",
        access_token=None,
        with_enrichment=True,
    )

    assert result["jsonld_keys_match"] is True
    assert result["enriched_profiles_match"] is True
    assert result["jsonld_exact_match"] is True
    assert result["enriched_exact_match"] is True


def test_compare_legacy_and_pipeline_extraction_detects_key_mismatch(monkeypatch):
    legacy_result = ExtractMetadataResult(
        jsonld_document={"name": "demo"},
        extraction_metadata={},
        metadata=object(),
    )

    monkeypatch.setattr(
        metadata_runtime,
        "canonical_schema_name",
        lambda registry, schema: schema,
    )
    monkeypatch.setattr(
        metadata_runtime,
        "create_extraction_use_case",
        lambda repo_url, access_token, with_enrichment: (_StubUseCase(legacy_result), None),
    )
    monkeypatch.setattr(
        metadata_runtime,
        "_build_jsonld_via_plugin",
        lambda metadata, schema, fallback_jsonld: fallback_jsonld,
    )
    monkeypatch.setattr(
        metadata_runtime,
        "run_extraction_via_pipeline",
        lambda repo_url, schema, access_token: ({"title": "demo"}, {}),
    )

    result = metadata_runtime.compare_legacy_and_pipeline_extraction(
        repo_url="https://example.com/repo",
        schema="maSMP",
        access_token=None,
        with_enrichment=False,
    )

    assert result["jsonld_keys_match"] is False
    assert result["jsonld_exact_match"] is False
