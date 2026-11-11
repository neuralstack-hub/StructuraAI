
from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app

client = TestClient(app)


def create_test_png():
    image = Image.new("RGB", (100, 80), color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to StructuraAI"
    assert response.json()["version"] == "0.2.0"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_documentation():
    response = client.get("/docs")

    assert response.status_code == 200


def test_valid_crack_image_upload():
    image_data = create_test_png()

    response = client.post(
        "/vision/analyze",
        files={
            "file": (
                "concrete.png",
                image_data,
                "image/png"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "image_validated"
    assert result["image_format"] == "PNG"
    assert result["width"] == 100
    assert result["height"] == 80
    assert result["analysis_status"] == "pending_ml_model"


def test_reject_invalid_image():
    response = client.post(
        "/vision/analyze",
        files={
            "file": (
                "fake.png",
                b"this is not an image",
                "image/png"
            )
        }
    )

    assert response.status_code == 400


def test_reject_unsupported_file_type():
    response = client.post(
        "/vision/analyze",
        files={
            "file": (
                "document.txt",
                b"sample text",
                "text/plain"
            )
        }
    )

    assert response.status_code == 415
