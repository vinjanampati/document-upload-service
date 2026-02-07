from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
import json

from app.models import UploadConfig, UploadResponse, CollectionInfo, ChunkingStrategy
from app.services.document import get_document_service
from app.services.vectorstore import get_vectorstore_service
from app.config import settings

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    config_json: str = Form(...)
):
    """
    Upload and process a document with specified chunking strategy

    Args:
        file: The document file to upload
        config_json: JSON string containing UploadConfig
    """
    try:
        # Parse config
        config_data = json.loads(config_json)
        config = UploadConfig(**config_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid config JSON")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config: {str(e)}")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_file_size_mb}MB"
        )

    # Save file
    doc_service = get_document_service()
    file_id, file_path = doc_service.save_file(file.filename, content)

    try:
        # Process and upload
        result = await doc_service.process_and_upload(
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            config=config
        )

        return UploadResponse(**result)

    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/collections", response_model=List[str])
async def list_collections():
    """List all available collections"""
    vectorstore = get_vectorstore_service()
    return vectorstore.list_collections()


@router.get("/collections/{collection_name}", response_model=CollectionInfo)
async def get_collection_info(collection_name: str):
    """Get information about a specific collection"""
    vectorstore = get_vectorstore_service()
    info = vectorstore.get_collection_info(collection_name)

    if info is None:
        raise HTTPException(status_code=404, detail="Collection not found")

    return CollectionInfo(**info)


@router.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a collection"""
    vectorstore = get_vectorstore_service()
    try:
        vectorstore.delete_collection(collection_name)
        return {"message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/defaults")
async def get_default_config():
    """Get default upload configuration"""
    return {
        "chunking_strategy": ChunkingStrategy.FIXED,
        "chunk_size": settings.default_chunk_size,
        "chunk_overlap": settings.default_chunk_overlap,
        "embedding_provider": "openai",
        "embedding_model": "text-embedding-3-small",
        "embedding_dimension": settings.default_embedding_dimension,
        "collection_name": settings.qdrant_collection,
        "parent_chunk_size": 2048,
        "child_chunk_size": 512,
        "semantic_threshold": 0.7
    }
