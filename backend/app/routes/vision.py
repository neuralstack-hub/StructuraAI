
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

router = APIRouter(prefix="/vision", tags=["Vision"])

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
}

ALLOWED_FORMATS = {"JPEG", "PNG"}


@router.post("/analyze")
async def analyze_crack_image(file: UploadFile = File(...)):
    # Check the declared content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only JPEG and PNG images are accepted."
        )

    # Read at most 5 MB plus one byte to detect oversized files
    image_bytes = await file.read(MAX_FILE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image size must not exceed 5 MB."
        )

    # Validate the actual image content, not just the filename
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=415,
                    detail="The actual image must be JPEG or PNG."
                )

            image.verify()

        # Reopen after verify() to read image metadata
        with Image.open(BytesIO(image_bytes)) as image:
            width, height = image.size
            image_format = image.format

    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image."
        )

    return {
        "status": "image_validated",
        "filename": file.filename,
        "image_format": image_format,
        "width": width,
        "height": height,
        "size_bytes": len(image_bytes),
        "analysis_status": "pending_ml_model",
        "message": (
            "Image validation successful. "
            "Crack classification is not yet implemented."
        )
    }
