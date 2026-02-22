from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    PointStruct,
    CollectionInfo as QdrantCollectionInfo
)

from app.config import settings
from app.chunking.base import Chunk


class VectorStoreService:
    """Service for managing Qdrant vector store operations"""

    def __init__(self, url: str = None):
        self.url = url or settings.qdrant_url
        self._client = None

    @property
    def client(self) -> QdrantClient:
        """Lazy load Qdrant client"""
        if self._client is None:
            self._client = QdrantClient(url=self.url)
        return self._client

    def ensure_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: Distance = Distance.COSINE
    ):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if collection_name not in collection_names:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "dense": VectorParams(
                        size=vector_size,
                        distance=distance,
                    )
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(),
                },
            )

    def upsert_chunks(
        self,
        collection_name: str,
        chunks: List[Chunk],
        embeddings: List[List[float]],
        file_metadata: Dict[str, Any] = None
    ) -> List[str]:
        """
        Insert chunks with their embeddings into the vector store

        Returns:
            List of point IDs
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")

        points = []
        point_ids = []

        for chunk, embedding in zip(chunks, embeddings):
            point_id = str(uuid.uuid4())
            point_ids.append(point_id)

            # Combine chunk metadata with file metadata
            payload = {
                "text": chunk.text,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                **(chunk.metadata or {}),
                **(file_metadata or {})
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector={"dense": embedding},
                    payload=payload
                )
            )

        # Batch upsert
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

        return point_ids

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection"""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count or 0,
                "indexed_vectors_count": info.indexed_vectors_count or 0,
                "points_count": info.points_count or 0,
                "status": info.status.value if info.status else "unknown"
            }
        except Exception as e:
            return None

    def list_collections(self) -> List[str]:
        """List all collection names"""
        collections = self.client.get_collections().collections
        return [c.name for c in collections]

    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        self.client.delete_collection(collection_name)

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        results = self.client.search(
            collection_name=collection_name,
            query_vector=("dense", query_vector),
            limit=limit,
            query_filter=filters
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]


# Singleton instance
_vectorstore_service = None


def get_vectorstore_service() -> VectorStoreService:
    """Get or create the vector store service"""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = VectorStoreService()
    return _vectorstore_service
