from typing import List, Dict, Any
from .base import BaseChunker, Chunk
from .fixed import FixedChunker


class HierarchicalChunker(BaseChunker):
    """
    Hierarchical chunking creates both parent (large) and child (small) chunks.
    Useful for retrieval systems that can leverage both broad context (parent)
    and specific details (child).
    """

    def __init__(
        self,
        parent_chunk_size: int = 2048,
        child_chunk_size: int = 512,
        child_chunk_overlap: int = 50
    ):
        """
        Args:
            parent_chunk_size: Size of parent chunks in characters
            child_chunk_size: Size of child chunks in characters
            child_chunk_overlap: Overlap between child chunks
        """
        if child_chunk_size >= parent_chunk_size:
            raise ValueError("child_chunk_size must be less than parent_chunk_size")

        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap

        # Create chunkers for parent and child levels
        self.parent_chunker = FixedChunker(
            chunk_size=parent_chunk_size,
            chunk_overlap=0  # No overlap for parent chunks
        )
        self.child_chunker = FixedChunker(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap
        )

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """
        Create hierarchical chunks.

        Returns a flat list of chunks where child chunks reference their parent.
        Each chunk has metadata indicating whether it's a parent or child.
        """
        if not text:
            return []

        all_chunks = []

        # First, create parent chunks
        parent_chunks = self.parent_chunker.chunk(text, metadata)

        for parent_idx, parent_chunk in enumerate(parent_chunks):
            # Add parent chunk with metadata
            parent_metadata = {
                **(metadata or {}),
                "chunk_index": len(all_chunks),
                "chunk_type": "hierarchical_parent",
                "parent_index": parent_idx,
                "is_parent": True,
                "has_children": True,
            }

            parent_chunk_obj = Chunk(
                text=parent_chunk.text,
                start_char=parent_chunk.start_char,
                end_char=parent_chunk.end_char,
                metadata=parent_metadata
            )

            all_chunks.append(parent_chunk_obj)

            # Now create child chunks within this parent
            child_chunks = self.child_chunker.chunk(parent_chunk.text)

            for child_idx, child_chunk in enumerate(child_chunks):
                # Calculate absolute position in original text
                absolute_start = parent_chunk.start_char + child_chunk.start_char
                absolute_end = parent_chunk.start_char + child_chunk.end_char

                child_metadata = {
                    **(metadata or {}),
                    "chunk_index": len(all_chunks),
                    "chunk_type": "hierarchical_child",
                    "parent_index": parent_idx,
                    "child_index": child_idx,
                    "is_parent": False,
                    "parent_chunk_index": parent_chunk_obj.metadata["chunk_index"],
                }

                child_chunk_obj = Chunk(
                    text=child_chunk.text,
                    start_char=absolute_start,
                    end_char=absolute_end,
                    metadata=child_metadata
                )

                all_chunks.append(child_chunk_obj)

        return all_chunks

    def get_parent_chunks_only(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """Get only parent chunks without children"""
        chunks = self.chunk(text, metadata)
        return [c for c in chunks if c.metadata.get("is_parent", False)]

    def get_child_chunks_only(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """Get only child chunks without parents"""
        chunks = self.chunk(text, metadata)
        return [c for c in chunks if not c.metadata.get("is_parent", False)]

    def __repr__(self):
        return f"HierarchicalChunker(parent={self.parent_chunk_size}, child={self.child_chunk_size})"
