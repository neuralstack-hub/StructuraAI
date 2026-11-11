
from fastapi import FastAPI

from backend.app.routes.vision import router as vision_router

app = FastAPI(
    title="StructuraAI",
    description="AI-Powered Structural Health Monitoring Platform",
    version="0.2.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to StructuraAI",
        "version": "0.2.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "StructuraAI Backend"
    }


app.include_router(vision_router)
