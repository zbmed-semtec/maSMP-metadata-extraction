from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.framework.api.endpoint_config import EndpointRegistrationConfig
from app.framework.api.endpoint_registry import register_default_endpoints


def test_debug_endpoint_absent_when_debug_group_disabled(monkeypatch):
    monkeypatch.setenv("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", "0")
    monkeypatch.setenv("COMET_RS_INCLUDE_METADATA_ENDPOINTS", "1")
    monkeypatch.setenv("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", "1")

    app = FastAPI()
    register_default_endpoints(app, config=EndpointRegistrationConfig.from_env())
    client = TestClient(app)

    # Debug endpoint group is not registered.
    debug_response = client.get(
        "/api/debug/pipeline-parity",
        params={"repo_url": "https://github.com/example/repo", "schema": "maSMP"},
    )
    assert debug_response.status_code == 404

    # Metadata endpoint group remains registered (missing required params => 422).
    metadata_response = client.get("/api/metadata")
    assert metadata_response.status_code == 422

    # System endpoint group remains registered and functional.
    health_response = client.get("/api/health")
    assert health_response.status_code == 200


def test_system_endpoints_absent_when_system_group_disabled(monkeypatch):
    monkeypatch.setenv("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", "1")
    monkeypatch.setenv("COMET_RS_INCLUDE_METADATA_ENDPOINTS", "1")
    monkeypatch.setenv("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", "0")

    app = FastAPI()
    register_default_endpoints(app, config=EndpointRegistrationConfig.from_env())
    client = TestClient(app)

    # System endpoint group is not registered.
    health_response = client.get("/api/health")
    assert health_response.status_code == 404

    # Metadata endpoint group remains registered.
    metadata_response = client.get("/api/metadata")
    assert metadata_response.status_code == 422


def test_metadata_endpoints_absent_when_metadata_group_disabled(monkeypatch):
    monkeypatch.setenv("COMET_RS_INCLUDE_DEBUG_ENDPOINTS", "1")
    monkeypatch.setenv("COMET_RS_INCLUDE_METADATA_ENDPOINTS", "0")
    monkeypatch.setenv("COMET_RS_INCLUDE_SYSTEM_ENDPOINTS", "1")

    app = FastAPI()
    register_default_endpoints(app, config=EndpointRegistrationConfig.from_env())
    client = TestClient(app)

    # Metadata endpoint group is not registered.
    metadata_response = client.get("/api/metadata")
    assert metadata_response.status_code == 404

    # System endpoint group remains registered.
    health_response = client.get("/api/health")
    assert health_response.status_code == 200

    # Debug route exists (enable flag here), request missing query param leads to validation error.
    debug_response = client.get("/api/debug/pipeline-parity")
    assert debug_response.status_code == 422
