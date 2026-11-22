"""
Test 1: Health endpoint.
Verifies GET /api/health returns healthy/degraded status, database info, and providers.
"""

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert "providers" in data
    assert "OmniMind AI" in data["service"]
