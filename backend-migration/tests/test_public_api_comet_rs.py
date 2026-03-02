import comet_rs


def test_public_api_extract_metadata_monkeypatched(monkeypatch):
    calls = {}

    def fake_run_extraction(*, repo_url, schema, access_token, with_enrichment):
        calls["args"] = {
            "repo_url": repo_url,
            "schema": schema,
            "access_token": access_token,
            "with_enrichment": with_enrichment,
        }
        return {"name": "dummy"}, {"enriched": True} if with_enrichment else None

    # Monkeypatch the underlying service function used by the public API
    monkeypatch.setattr(
        comet_rs,
        "run_extraction",
        fake_run_extraction,
    )

    doc, enriched = comet_rs.extract_metadata(
        "https://example.com/repo",
        schema="maSMP",
        token="abc",
        with_enrichment=True,
    )

    assert calls["args"]["repo_url"] == "https://example.com/repo"
    assert calls["args"]["schema"] == "maSMP"
    assert calls["args"]["access_token"] == "abc"
    assert calls["args"]["with_enrichment"] is True
    assert doc["name"] == "dummy"
    assert enriched == {"enriched": True}


def test_public_api_assess_fairness_monkeypatched(monkeypatch):
    calls = {}

    def fake_run_fairness_assessment(*, repo_url, schema, access_token, with_enrichment):
        calls["args"] = {
            "repo_url": repo_url,
            "schema": schema,
            "access_token": access_token,
            "with_enrichment": with_enrichment,
        }
        dummy_doc = {"name": "dummy"}

        class DummyReport:
            overall_score = 1.0

        return dummy_doc, DummyReport()  # type: ignore[return-value]

    monkeypatch.setattr(
        comet_rs,
        "run_fairness_assessment",
        fake_run_fairness_assessment,
    )

    doc, report = comet_rs.assess_fairness(
        "https://example.com/repo",
        schema="CODEMETA",
        token=None,
    )

    assert calls["args"]["repo_url"] == "https://example.com/repo"
    assert calls["args"]["schema"] == "CODEMETA"
    assert calls["args"]["access_token"] is None
    assert calls["args"]["with_enrichment"] is False
    assert doc["name"] == "dummy"
    # Report is passed through
    assert getattr(report, "overall_score", None) == 1.0

