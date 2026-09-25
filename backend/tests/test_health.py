from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Verify that GET /api/health returns 200 OK and expected service metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "lexguard-backend"
    assert "version" in data
