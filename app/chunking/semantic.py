import re
from typing import List, Dict, Any, Optional
from .base import BaseChunker, Chunk
import numpy as np


class SemanticChunker(BaseChunker):
    """
    Semantic chunking based on sentence boundaries and similarity.
    Splits text at natural sentence boundaries and groups sentences
    based on semantic similarity.
    """

    def __init__(
        self,
        embedding_function: Optional[callable] = None,
        similarity_threshold: float = 0.7,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000
    ):
        """
        Args:
            embedding_function: Function to generate embeddings for text
            similarity_threshold: Threshold for sentence similarity (0-1)
            min_chunk_size: Minimum chunk size in characters
            max_chunk_size: Maximum chunk size in characters
        """
        self.embedding_function = embedding_function
        self.similarity_threshold = similarity_threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _split_into_sentences(self, text: str) -> List[tuple]:
        """
        Split text into sentences and track their positions.

        Returns:
            List of (sentence_text, start_pos, end_pos) tuples
        """
        # Enhanced sentence splitting with position tracking
        sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
        sentences = []
        current_pos = 0

        # Split on sentence boundaries
        parts = sentence_endings.split(text)

        for part in parts:
            if not part.strip():
                continue

            start = text.find(part, current_pos)
            end = start + len(part)
            sentences.append((part.strip(), start, end))
            current_pos = end

        return sentences

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """Split text into semantic chunks"""
        if not text:
            return []

        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        # If no embedding function, fall back to sentence-based chunking
        if self.embedding_function is None:
            return self._chunk_by_sentences(sentences, metadata)

        # Generate embeddings for each sentence
        try:
            sentence_texts = [s[0] for s in sentences]
            embeddings = [self.embedding_function(s) for s in sentence_texts]

            return self._chunk_by_similarity(sentences, embeddings, metadata)
        except Exception as e:
            # Fall back to sentence-based chunking on error
            print(f"Error generating embeddings: {e}. Falling back to sentence chunking.")
            return self._chunk_by_sentences(sentences, metadata)

    def _chunk_by_sentences(
        self,
        sentences: List[tuple],
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Chunk by grouping sentences without embedding similarity.
        Groups sentences until max_chunk_size is reached.
        """
        chunks = []
        current_chunk_sentences = []
        current_chunk_size = 0
        chunk_start = 0

        for sentence_text, start, end in sentences:
            sentence_len = len(sentence_text)

            # Start new chunk if adding this sentence exceeds max size
            if current_chunk_size + sentence_len > self.max_chunk_size and current_chunk_sentences:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk_sentences)
                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": len(chunks),
                    "chunk_type": "semantic_fallback",
                    "num_sentences": len(current_chunk_sentences),
                }

                chunks.append(
                    Chunk(
                        text=chunk_text,
                        start_char=chunk_start,
                        end_char=end,
                        metadata=chunk_metadata
                    )
                )

                # Reset for new chunk
                current_chunk_sentences = []
                current_chunk_size = 0
                chunk_start = start

            current_chunk_sentences.append(sentence_text)
            current_chunk_size += sentence_len

        # Add final chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk_metadata = {
                **(metadata or {}),
                "chunk_index": len(chunks),
                "chunk_type": "semantic_fallback",
                "num_sentences": len(current_chunk_sentences),
            }

            chunks.append(
                Chunk(
                    text=chunk_text,
                    start_char=chunk_start,
                    end_char=sentences[-1][2],
                    metadata=chunk_metadata
                )
            )

        return chunks

    def _chunk_by_similarity(
        self,
        sentences: List[tuple],
        embeddings: List[np.ndarray],
        metadata: Dict[str, Any] = None
    ) -> List[Chunk]:
        """
        Chunk by grouping semantically similar sentences.
        """
        if not sentences:
            return []

        chunks = []
        current_group = [0]  # Start with first sentence
        chunk_start = sentences[0][1]

        for i in range(1, len(sentences)):
            # Calculate similarity with previous sentence
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            # Get current chunk size
            current_size = sum(len(sentences[idx][0]) for idx in current_group)

            # Decide whether to add to current chunk or start new one
            should_split = (
                similarity < self.similarity_threshold or
                current_size + len(sentences[i][0]) > self.max_chunk_size
            )

            if should_split and current_size >= self.min_chunk_size:
                # Create chunk from current group
                chunk_sentences = [sentences[idx][0] for idx in current_group]
                chunk_text = " ".join(chunk_sentences)
                chunk_end = sentences[current_group[-1]][2]

                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": len(chunks),
                    "chunk_type": "semantic",
                    "num_sentences": len(current_group),
                    "avg_similarity": None,  # Could calculate if needed
                }

                chunks.append(
                    Chunk(
                        text=chunk_text,
                        start_char=chunk_start,
                        end_char=chunk_end,
                        metadata=chunk_metadata
                    )
                )

                # Start new chunk
                current_group = [i]
                chunk_start = sentences[i][1]
            else:
                # Add to current chunk
                current_group.append(i)

        # Add final chunk
        if current_group:
            chunk_sentences = [sentences[idx][0] for idx in current_group]
            chunk_text = " ".join(chunk_sentences)
            chunk_end = sentences[current_group[-1]][2]

            chunk_metadata = {
                **(metadata or {}),
                "chunk_index": len(chunks),
                "chunk_type": "semantic",
                "num_sentences": len(current_group),
            }

            chunks.append(
                Chunk(
                    text=chunk_text,
                    start_char=chunk_start,
                    end_char=chunk_end,
                    metadata=chunk_metadata
                )
            )

        return chunks

    def __repr__(self):
        return f"SemanticChunker(threshold={self.similarity_threshold}, min={self.min_chunk_size}, max={self.max_chunk_size})"
