from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_available():
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["service"] == "metadata-extractor"


def test_platforms_endpoint_available():
    response = client.get("/api/platforms")
    assert response.status_code == 200
    payload = response.json()
    assert "platforms" in payload
    assert len(payload["platforms"]) >= 2
