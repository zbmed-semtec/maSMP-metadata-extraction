from fastapi.testclient import TestClient

from app.framework.api import debug_router
from app.main import app


client = TestClient(app)


def test_pipeline_parity_endpoint_disabled_by_default(monkeypatch):
    monkeypatch.delenv("COMET_RS_ENABLE_PARITY_ENDPOINT", raising=False)

    response = client.get(
        "/api/debug/pipeline-parity",
        params={
            "repo_url": "https://github.com/example/repo",
            "schema": "maSMP",
        },
    )

    assert response.status_code == 404


def test_pipeline_parity_endpoint_enabled_returns_parity(monkeypatch):
    monkeypatch.setenv("COMET_RS_ENABLE_PARITY_ENDPOINT", "1")

    def fake_compare(repo_url, schema, access_token, with_enrichment):  # type: ignore[no-untyped-def]
        return {
            "schema": schema,
            "jsonld_keys_match": True,
            "enriched_profiles_match": True,
            "jsonld_exact_match": True,
            "enriched_exact_match": True,
            "legacy_jsonld_keys": ["name"],
            "pipeline_jsonld_keys": ["name"],
            "legacy_enriched_profiles": [],
            "pipeline_enriched_profiles": [],
            "legacy_jsonld": {"name": "demo"},
            "pipeline_jsonld": {"name": "demo"},
            "legacy_enriched": None,
            "pipeline_enriched": None,
        }

    monkeypatch.setattr(
        debug_router,
        "compare_legacy_and_pipeline_extraction",
        fake_compare,
    )

    response = client.get(
        "/api/debug/pipeline-parity",
        params={
            "repo_url": "https://github.com/example/repo",
            "schema": "maSMP",
            "with_enrichment": "false",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["parity"]["jsonld_exact_match"] is True


def test_pipeline_parity_endpoint_does_not_require_runtime_flag(monkeypatch):
    monkeypatch.setenv("COMET_RS_ENABLE_PARITY_ENDPOINT", "1")
    monkeypatch.delenv("COMET_RS_USE_PIPELINE_RUNTIME", raising=False)

    calls = {"count": 0}

    def fake_compare(repo_url, schema, access_token, with_enrichment):  # type: ignore[no-untyped-def]
        calls["count"] += 1
        return {
            "schema": schema,
            "jsonld_keys_match": True,
            "enriched_profiles_match": True,
            "jsonld_exact_match": True,
            "enriched_exact_match": True,
            "legacy_jsonld_keys": ["name"],
            "pipeline_jsonld_keys": ["name"],
            "legacy_enriched_profiles": [],
            "pipeline_enriched_profiles": [],
            "legacy_jsonld": {"name": "demo"},
            "pipeline_jsonld": {"name": "demo"},
            "legacy_enriched": None,
            "pipeline_enriched": None,
        }

    monkeypatch.setattr(
        debug_router,
        "compare_legacy_and_pipeline_extraction",
        fake_compare,
    )

    response = client.get(
        "/api/debug/pipeline-parity",
        params={
            "repo_url": "https://github.com/example/repo",
            "schema": "maSMP",
        },
    )

    assert response.status_code == 200
    assert calls["count"] == 1
