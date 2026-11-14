
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database import init_db
from backend.app.routes.vision import router as vision_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="StructuraAI",
    description="AI-Powered Structural Health Monitoring Platform",
    version="0.3.0",
    lifespan=lifespan,
)

# Allow the React development server to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Welcome to StructuraAI",
        "version": "0.3.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "StructuraAI Backend"
    }


app.include_router(vision_router)
