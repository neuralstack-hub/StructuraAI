
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import numpy as np
import torch
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from PIL import Image, UnidentifiedImageError

from ml.vision.models.crack_cnn import CrackCNN
from backend.app.database import (
    save_inspection,
    get_inspections,
    get_inspection,
)

router = APIRouter(prefix="/vision", tags=["Vision"])

MAX_FILE_SIZE = 5 * 1024 * 1024
IMAGE_SIZE = 128

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_FORMATS = {"JPEG", "PNG"}

LABEL_MAP = {
    0: "uncracked",
    1: "cracked",
}

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHECKPOINT_PATH = (
    PROJECT_ROOT
    / "ml"
    / "vision"
    / "experiments"
    / "grouped"
    / "best_crack_cnn_grouped_epoch8.pth"
)


# --------------------------------------------------
# LOAD MODEL ONCE
# --------------------------------------------------

@lru_cache(maxsize=1)
def load_model():

    if not CHECKPOINT_PATH.is_file():
        raise FileNotFoundError(
            f"Model checkpoint not found: {CHECKPOINT_PATH}"
        )

    checkpoint = torch.load(
        CHECKPOINT_PATH,
        map_location="cpu",
        weights_only=True,
    )

    if checkpoint.get("image_size") != IMAGE_SIZE:
        raise ValueError("Unexpected model image size.")

    if checkpoint.get("class_mapping") != {
        "uncracked": 0,
        "cracked": 1,
    }:
        raise ValueError("Unexpected model class mapping.")

    model = CrackCNN(num_classes=2)

    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, checkpoint


# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def preprocess_image(image):

    image = image.convert("RGB")

    image = image.resize(
        (IMAGE_SIZE, IMAGE_SIZE),
        Image.Resampling.BILINEAR,
    )

    array = np.asarray(image, dtype=np.float32) / 255.0
    array = np.transpose(array, (2, 0, 1))
    array = (array - 0.5) / 0.5

    tensor = torch.from_numpy(
        np.ascontiguousarray(array)
    )

    return tensor.unsqueeze(0)


# --------------------------------------------------
# MODEL PREDICTION
# --------------------------------------------------

def predict_image(image):

    model, checkpoint = load_model()
    input_tensor = preprocess_image(image)

    with torch.inference_mode():

        outputs = model(input_tensor)

        probabilities = torch.softmax(
            outputs, dim=1
        )[0]

        predicted_index = int(
            torch.argmax(probabilities).item()
        )

        crack_probability = float(probabilities[1].item())

        confidence = float(
            probabilities[predicted_index].item()
        )

    return {
        "prediction": LABEL_MAP[predicted_index],
        "crack_probability": round(crack_probability, 6),
        "confidence": round(confidence, 6),
        "model_epoch": checkpoint["epoch"],
    }


# --------------------------------------------------
# MODEL STATUS
# --------------------------------------------------

@router.get("/model-status")
def model_status():

    try:
        _, checkpoint = load_model()

        return {
            "status": "loaded",
            "model": "CrackCNN",
            "checkpoint_epoch": checkpoint["epoch"],
            "image_size": IMAGE_SIZE,
            "device": "cpu",
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Vision model unavailable: {str(error)}",
        )


# --------------------------------------------------
# INSPECTION HISTORY
# --------------------------------------------------

@router.get("/history")
def inspection_history(
    limit: int = Query(default=50, ge=1, le=100)
):

    try:
        records = get_inspections(limit)

        return {
            "total": len(records),
            "inspections": records,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve history: {str(error)}",
        )


@router.get("/history/{inspection_id}")
def inspection_details(inspection_id: int):

    try:
        record = get_inspection(inspection_id)

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Inspection not found.",
            )

        return record

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not retrieve inspection: {str(error)}",
        )


# --------------------------------------------------
# IMAGE ANALYSIS
# --------------------------------------------------

@router.post("/analyze")
async def analyze_crack_image(
    file: UploadFile = File(...)
):

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG and PNG images are accepted.",
        )

    image_bytes = await file.read(MAX_FILE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 5 MB.",
        )

    try:

        with Image.open(BytesIO(image_bytes)) as image:

            if image.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=415,
                    detail="The actual image must be JPEG or PNG.",
                )

            image.verify()

        with Image.open(BytesIO(image_bytes)) as image:

            width, height = image.size
            image_format = image.format

            prediction = predict_image(image)

    except HTTPException:
        raise

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
    ):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Model analysis failed: {str(error)}",
        )

    # Save the completed inspection.
    try:

        inspection_id = save_inspection(
            filename=file.filename or "uploaded_image",
            prediction=prediction["prediction"],
            crack_probability=prediction["crack_probability"],
            confidence=prediction["confidence"],
            image_width=width,
            image_height=height,
            model_epoch=prediction["model_epoch"],
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction completed but saving failed: {str(error)}",
        )

    return {
        "status": "analysis_completed",
        "inspection_id": inspection_id,
        "filename": file.filename,
        "image_format": image_format,
        "width": width,
        "height": height,
        "size_bytes": len(image_bytes),
        "analysis": prediction,
        "disclaimer": (
            "Experimental image-based crack classification. "
            "Not a structural safety assessment."
        ),
    }
