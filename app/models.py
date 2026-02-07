from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List


class ChunkingStrategy(str, Enum):
    FIXED = "fixed"
    SEMANTIC = "semantic"
    HIERARCHICAL = "hierarchical"


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    FASTEMBED = "fastembed"


class UploadConfig(BaseModel):
    """Configuration for document upload and chunking"""
    chunking_strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.FIXED,
        description="Chunking strategy to use"
    )
    chunk_size: int = Field(
        default=512,
        ge=100,
        le=4000,
        description="Size of each chunk in characters/tokens"
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Overlap between chunks"
    )
    embedding_provider: str = Field(
        default="openai",
        description="Embedding provider (e.g., 'openai', 'cohere')"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Specific embedding model to use"
    )
    embedding_dimension: int = Field(
        default=1536,
        description="Embedding vector dimension"
    )
    collection_name: Optional[str] = Field(
        default=None,
        description="Custom collection name (defaults to 'documents')"
    )
    # Hierarchical chunking specific
    parent_chunk_size: Optional[int] = Field(
        default=2048,
        description="Parent chunk size for hierarchical chunking"
    )
    child_chunk_size: Optional[int] = Field(
        default=512,
        description="Child chunk size for hierarchical chunking"
    )
    # Semantic chunking specific
    semantic_threshold: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for semantic chunking"
    )


class ChunkInfo(BaseModel):
    """Information about a single chunk"""
    chunk_id: str
    text: str
    start_char: int
    end_char: int
    metadata: dict


class UploadResponse(BaseModel):
    """Response after successful upload"""
    file_id: str
    filename: str
    file_size: int
    total_chunks: int
    chunking_strategy: ChunkingStrategy
    embedding_model: str
    collection_name: str
    chunks_preview: List[ChunkInfo] = Field(
        default_factory=list,
        description="Preview of first few chunks"
    )
    status: str = "success"


class UploadStatus(BaseModel):
    """Status of an upload job"""
    file_id: str
    filename: str
    status: str  # processing, completed, failed
    progress: int  # 0-100
    total_chunks: Optional[int] = None
    error: Optional[str] = None


class CollectionInfo(BaseModel):
    """Information about a Qdrant collection"""
    name: str
    vectors_count: int
    indexed_vectors_count: int
    points_count: int
    status: str
