from app.framework.api import metadata_runtime


def test_run_extraction_uses_pipeline_when_flag_enabled(monkeypatch):
    monkeypatch.setenv("COMET_RS_USE_PIPELINE_RUNTIME", "1")

    calls = {"pipeline": 0, "legacy": 0}

    def fake_canonical_schema_name(registry, schema):  # type: ignore[no-untyped-def]
        return schema

    def fake_run_extraction_via_pipeline(repo_url, schema, access_token, progress_callback=None):  # type: ignore[no-untyped-def]
        calls["pipeline"] += 1
        return {"name": "from-pipeline"}, {}

    def fake_create_extraction_use_case(repo_url, access_token, with_enrichment):  # type: ignore[no-untyped-def]
        calls["legacy"] += 1
        raise AssertionError("Legacy path should not be used when pipeline flag is enabled")

    monkeypatch.setattr(metadata_runtime, "canonical_schema_name", fake_canonical_schema_name)
    monkeypatch.setattr(metadata_runtime, "run_extraction_via_pipeline", fake_run_extraction_via_pipeline)
    monkeypatch.setattr(metadata_runtime, "create_extraction_use_case", fake_create_extraction_use_case)

    jsonld_document, enriched = metadata_runtime.run_extraction(
        repo_url="https://github.com/example/repo",
        schema="maSMP",
        access_token=None,
        with_enrichment=False,
    )

    assert calls["pipeline"] == 1
    assert calls["legacy"] == 0
    assert jsonld_document == {"name": "from-pipeline"}
    assert enriched is None


def test_run_extraction_uses_legacy_when_flag_disabled(monkeypatch):
    monkeypatch.delenv("COMET_RS_USE_PIPELINE_RUNTIME", raising=False)

    calls = {"pipeline": 0, "legacy": 0}

    class _LegacyUseCase:
        def execute(self, **kwargs):  # type: ignore[no-untyped-def]
            calls["legacy"] += 1
            return type(
                "Result",
                (),
                {
                    "metadata": object(),
                    "jsonld_document": {"name": "from-legacy"},
                    "extraction_metadata": {},
                },
            )()

    monkeypatch.setattr(metadata_runtime, "canonical_schema_name", lambda registry, schema: schema)
    monkeypatch.setattr(
        metadata_runtime,
        "run_extraction_via_pipeline",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Pipeline path should not be used when flag is disabled")),
    )
    monkeypatch.setattr(
        metadata_runtime,
        "create_extraction_use_case",
        lambda repo_url, access_token, with_enrichment: (_LegacyUseCase(), None),
    )
    monkeypatch.setattr(
        metadata_runtime,
        "_build_jsonld_via_plugin",
        lambda metadata, schema, fallback_jsonld: fallback_jsonld,
    )

    jsonld_document, enriched = metadata_runtime.run_extraction(
        repo_url="https://github.com/example/repo",
        schema="maSMP",
        access_token=None,
        with_enrichment=False,
    )

    assert calls["legacy"] == 1
    assert calls["pipeline"] == 0
    assert jsonld_document == {"name": "from-legacy"}
    assert enriched is None
