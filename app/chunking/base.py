from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Chunk:
    """Represents a text chunk with metadata"""

    def __init__(
        self,
        text: str,
        start_char: int,
        end_char: int,
        metadata: Dict[str, Any] = None
    ):
        self.text = text
        self.start_char = start_char
        self.end_char = end_char
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Chunk(text={self.text[:50]}..., start={self.start_char}, end={self.end_char})"


class BaseChunker(ABC):
    """Base class for all chunking strategies"""

    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        """
        Split text into chunks

        Args:
            text: The text to chunk
            metadata: Additional metadata to attach to chunks

        Returns:
            List of Chunk objects
        """
        pass
