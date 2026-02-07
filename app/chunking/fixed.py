from typing import List, Dict, Any
from .base import BaseChunker, Chunk


class FixedChunker(BaseChunker):
    """
    Fixed-size chunking with overlap.
    Splits text into chunks of approximately equal size with configurable overlap.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be non-negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """Split text into fixed-size chunks with overlap"""
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate end position for this chunk
            end = min(start + self.chunk_size, text_length)

            # Extract chunk text
            chunk_text = text[start:end].strip()

            # Only add non-empty chunks
            if chunk_text:
                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": len(chunks),
                    "chunk_type": "fixed",
                    "chunk_size": len(chunk_text),
                }

                chunks.append(
                    Chunk(
                        text=chunk_text,
                        start_char=start,
                        end_char=end,
                        metadata=chunk_metadata
                    )
                )

            # Move start position for next chunk (with overlap)
            start = start + self.chunk_size - self.chunk_overlap

            # Prevent infinite loop if we're at the end
            if start >= text_length:
                break

        return chunks

    def __repr__(self):
        return f"FixedChunker(chunk_size={self.chunk_size}, overlap={self.chunk_overlap})"
