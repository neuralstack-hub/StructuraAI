
from fastapi import FastAPI

app = FastAPI(
    title="StructuraAI",
    description="AI-Powered Structural Health Monitoring Platform",
    version="0.1.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to StructuraAI",
        "version": "0.1.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "StructuraAI Backend"
    }
