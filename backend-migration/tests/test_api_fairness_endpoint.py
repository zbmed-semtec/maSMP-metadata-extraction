from dataclasses import asdict
from typing import Any, Dict, Tuple

from fastapi.testclient import TestClient

from app.api import services as api_services
from app.core.entities.fairness import FairnessReport
from app.main import app


client = TestClient(app)


def test_get_fairness_endpoint_uses_service(monkeypatch):
    calls: Dict[str, Any] = {}

    def fake_run_fairness_assessment(
        repo_url: str,
        schema: str,
        access_token: str | None = None,
        with_enrichment: bool = False,
    ) -> Tuple[Dict[str, Any], FairnessReport]:
        calls["args"] = {
            "repo_url": repo_url,
            "schema": schema,
            "access_token": access_token,
            "with_enrichment": with_enrichment,
        }
        dummy_doc = {"name": "dummy"}
        dummy_report = FairnessReport(
            overall_score=1.0,
            findable=1.0,
            accessible=0.0,
            interoperable=0.0,
            reusable=1.0,
            indicators=[],
        )
        return dummy_doc, dummy_report

    monkeypatch.setattr(
        api_services.fairness_service,
        "run_fairness_assessment",
        fake_run_fairness_assessment,
    )

    response = client.get(
        "/api/fairness",
        params={
            "repo_url": "https://github.com/example/repo",
            "schema": "maSMP",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    # Service was called with expected parameters
    assert calls["args"]["repo_url"] == "https://github.com/example/repo"
    assert calls["args"]["schema"] == "maSMP"
    assert calls["args"]["with_enrichment"] is False

    # Response shape matches FairnessResponse contract
    assert payload["status"] == "success"
    assert payload["schema"] == "maSMP"
    assert payload["results"]["name"] == "dummy"
    assert payload["fairness"]["overall_score"] == 1.0

