import pytest
from typing import Generator
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings, Settings

def get_test_settings() -> Settings:
    return Settings(
        PROJECT_NAME="CareerPilotAI-Test",
        ENVIRONMENT="testing",
        DEBUG=False,
        ALLOWED_ORIGINS="http://localhost:3000"
    )

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()