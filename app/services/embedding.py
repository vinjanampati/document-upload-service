from typing import List, Optional
import numpy as np
from functools import lru_cache

from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using various providers"""

    def __init__(self, provider: str, model: str, dimension: int = 1536):
        self.provider = provider.lower()
        self.model = model
        self.dimension = dimension
        self._client = None

    def _get_openai_client(self):
        """Lazy load OpenAI client"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key)

    def _get_cohere_client(self):
        """Lazy load Cohere client"""
        if not settings.cohere_api_key:
            raise ValueError("Cohere API key not configured")

        import cohere
        return cohere.Client(settings.cohere_api_key)

    def _get_google_client(self):
        """Lazy load Google client"""
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")

        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        return genai

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []

        if self.provider == "openai":
            return self._embed_openai(texts)
        elif self.provider == "cohere":
            return self._embed_cohere(texts)
        elif self.provider == "google":
            return self._embed_google(texts)
        elif self.provider == "fastembed":
            return self._embed_fastembed(texts)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

    def _embed_openai(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using OpenAI"""
        client = self._get_openai_client()

        response = client.embeddings.create(
            model=self.model,
            input=texts
        )

        embeddings = [np.array(item.embedding, dtype=np.float32) for item in response.data]
        return embeddings

    def _embed_cohere(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using Cohere"""
        client = self._get_cohere_client()

        response = client.embed(
            texts=texts,
            model=self.model,
            input_type="search_document"
        )

        embeddings = [np.array(emb, dtype=np.float32) for emb in response.embeddings]
        return embeddings

    def _embed_google(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using Google"""
        genai = self._get_google_client()

        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(np.array(result['embedding'], dtype=np.float32))

        return embeddings

    def _embed_fastembed(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings using FastEmbed (local)"""
        from fastembed import TextEmbedding

        # Initialize embedding model (cached)
        if not hasattr(self, '_fastembed_model'):
            self._fastembed_model = TextEmbedding(model_name=self.model)

        embeddings = list(self._fastembed_model.embed(texts))
        return [np.array(emb, dtype=np.float32) for emb in embeddings]


@lru_cache(maxsize=10)
def get_embedding_service(provider: str, model: str, dimension: int) -> EmbeddingService:
    """Get or create a cached embedding service"""
    return EmbeddingService(provider, model, dimension)
