
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


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_documentation():
    response = client.get("/docs")

    assert response.status_code == 200


def test_model_status():
    response = client.get("/vision/model-status")

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["status"] == "loaded"
    assert result["model"] == "CrackCNN"
    assert result["checkpoint_epoch"] == 8
    assert result["image_size"] == 128


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

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["status"] == "analysis_completed"
    assert result["image_format"] == "PNG"
    assert result["width"] == 100
    assert result["height"] == 80

    analysis = result["analysis"]

    assert analysis["prediction"] in ["cracked", "uncracked"]
    assert 0 <= analysis["crack_probability"] <= 1
    assert 0 <= analysis["confidence"] <= 1
    assert analysis["model_epoch"] == 8


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
