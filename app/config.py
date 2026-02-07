from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None

    # Vector Store
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documents"

    # Upload settings
    max_file_size_mb: int = 50
    upload_dir: str = "./uploads"
    allowed_extensions: list[str] = [".txt", ".md", ".pdf", ".docx", ".html"]

    # Default chunking settings
    default_chunk_size: int = 512
    default_chunk_overlap: int = 50
    default_embedding_model: str = "openai:text-embedding-3-small"
    default_embedding_dimension: int = 1536


settings = Settings()
