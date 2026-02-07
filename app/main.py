from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.routers.upload import router as upload_router
from app.config import settings

app = FastAPI(
    title="Document Upload Service",
    description="Upload documents with configurable chunking strategies and embedding options",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api", tags=["upload"])


@app.get("/")
async def root():
    return {
        "message": "Document Upload Service",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "qdrant_url": settings.qdrant_url,
        "max_file_size_mb": settings.max_file_size_mb
    }
