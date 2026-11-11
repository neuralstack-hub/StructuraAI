
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to StructuraAI",
        "version": "0.1.0"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "StructuraAI Backend"
    }


def test_api_documentation():
    response = client.get("/docs")

    assert response.status_code == 200
