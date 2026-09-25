from fastapi.testclient import TestClient
from app.config import Settings

def test_configuration_loading():
    settings = Settings(PROJECT_NAME="OverrideTest", ENVIRONMENT="production")
    assert settings.PROJECT_NAME == "OverrideTest"
    assert settings.ENVIRONMENT == "production"
    assert isinstance(settings.ALLOWED_ORIGINS, list)

def test_root_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["environment"] == "testing"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_api_v1_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"