import os
import uuid
from typing import List, Dict, Any
from pathlib import Path
import mimetypes

from app.models import UploadConfig, ChunkingStrategy, ChunkInfo
from app.chunking.fixed import FixedChunker
from app.chunking.semantic import SemanticChunker
from app.chunking.hierarchical import HierarchicalChunker
from app.services.embedding import get_embedding_service
from app.services.vectorstore import get_vectorstore_service
from app.config import settings


class DocumentService:
    """Service for processing and uploading documents"""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)

    def save_file(self, filename: str, content: bytes) -> tuple[str, Path]:
        """
        Save uploaded file to disk

        Returns:
            (file_id, file_path)
        """
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        file_path = self.upload_dir / f"{file_id}{file_ext}"

        with open(file_path, "wb") as f:
            f.write(content)

        return file_id, file_path

    def extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        suffix = file_path.suffix.lower()

        if suffix in [".txt", ".md"]:
            return self._extract_text_file(file_path)
        elif suffix == ".pdf":
            return self._extract_pdf(file_path)
        elif suffix == ".docx":
            return self._extract_docx(file_path)
        elif suffix == ".html":
            return self._extract_html(file_path)
        else:
            # Fallback: try to read as text
            try:
                return self._extract_text_file(file_path)
            except Exception as e:
                raise ValueError(f"Unsupported file format: {suffix}")

    def _extract_text_file(self, file_path: Path) -> str:
        """Extract text from plain text files"""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            import pypdf
            text = []
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    text.append(page.extract_text())
            return "\n\n".join(text)
        except ImportError:
            raise ValueError("pypdf not installed. Install with: pip install pypdf")

    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ValueError("python-docx not installed. Install with: pip install python-docx")

    def _extract_html(self, file_path: Path) -> str:
        """Extract text from HTML files"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                return soup.get_text()
        except ImportError:
            raise ValueError("beautifulsoup4 not installed. Install with: pip install beautifulsoup4")

    def create_chunker(self, config: UploadConfig, embedding_function=None):
        """Create appropriate chunker based on config"""
        if config.chunking_strategy == ChunkingStrategy.FIXED:
            return FixedChunker(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap
            )
        elif config.chunking_strategy == ChunkingStrategy.SEMANTIC:
            return SemanticChunker(
                embedding_function=embedding_function,
                similarity_threshold=config.semantic_threshold or 0.7,
                min_chunk_size=100,
                max_chunk_size=config.chunk_size
            )
        elif config.chunking_strategy == ChunkingStrategy.HIERARCHICAL:
            return HierarchicalChunker(
                parent_chunk_size=config.parent_chunk_size or 2048,
                child_chunk_size=config.child_chunk_size or 512,
                child_chunk_overlap=config.chunk_overlap
            )
        else:
            raise ValueError(f"Unknown chunking strategy: {config.chunking_strategy}")

    async def process_and_upload(
        self,
        file_id: str,
        filename: str,
        file_path: Path,
        config: UploadConfig
    ) -> Dict[str, Any]:
        """
        Process document: extract text, chunk, embed, and upload to vector store

        Returns:
            Upload result with metadata
        """
        # Extract text
        text = self.extract_text(file_path)

        # Get embedding service
        embedding_service = get_embedding_service(
            provider=config.embedding_provider,
            model=config.embedding_model,
            dimension=config.embedding_dimension
        )

        # Create embedding function for semantic chunking if needed
        embedding_func = None
        if config.chunking_strategy == ChunkingStrategy.SEMANTIC:
            embedding_func = lambda txt: embedding_service.embed_text(txt)

        # Create chunker
        chunker = self.create_chunker(config, embedding_func)

        # Create chunks
        file_metadata = {
            "file_id": file_id,
            "filename": filename,
            "file_size": file_path.stat().st_size
        }

        chunks = chunker.chunk(text, metadata=file_metadata)

        if not chunks:
            raise ValueError("No chunks created from document")

        # Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = embedding_service.embed_batch(chunk_texts)

        # Upload to vector store
        collection_name = config.collection_name or settings.qdrant_collection
        vectorstore = get_vectorstore_service()

        # Ensure collection exists
        vectorstore.ensure_collection(
            collection_name=collection_name,
            vector_size=config.embedding_dimension
        )

        # Upsert chunks
        point_ids = vectorstore.upsert_chunks(
            collection_name=collection_name,
            chunks=chunks,
            embeddings=embeddings,
            file_metadata=file_metadata
        )

        # Create preview of first few chunks
        chunks_preview = [
            ChunkInfo(
                chunk_id=point_ids[i],
                text=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                metadata=chunk.metadata
            )
            for i, chunk in enumerate(chunks[:3])  # First 3 chunks
        ]

        return {
            "file_id": file_id,
            "filename": filename,
            "file_size": file_path.stat().st_size,
            "total_chunks": len(chunks),
            "chunking_strategy": config.chunking_strategy,
            "embedding_model": f"{config.embedding_provider}:{config.embedding_model}",
            "collection_name": collection_name,
            "chunks_preview": chunks_preview,
            "point_ids": point_ids
        }


# Singleton instance
_document_service = None


def get_document_service() -> DocumentService:
    """Get or create document service"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
