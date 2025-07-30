"""Document chunking strategies."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from ..utils.logging import LoggerMixin


class BaseChunker(ABC, LoggerMixin):
    """Abstract base class for document chunkers."""
    
    @abstractmethod
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Chunk text into smaller pieces."""
        pass


class FixedSizeChunker(BaseChunker):
    """Fixed-size text chunker."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Chunk text into fixed-size pieces."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                "content": chunk_text,
                "metadata": metadata or {},
                "start_index": start,
                "end_index": end
            })
            
            start = end - self.overlap
        
        return chunks


class SemanticChunker(BaseChunker):
    """Semantic-based text chunker."""
    
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Chunk text based on semantic boundaries."""
        # Placeholder - would use sentence transformers for semantic chunking
        sentences = text.split('. ')
        chunks = []
        
        for i, sentence in enumerate(sentences):
            chunks.append({
                "content": sentence,
                "metadata": metadata or {},
                "chunk_index": i
            })
        
        return chunks


class RecursiveChunker(BaseChunker):
    """Recursive text chunker."""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Recursively chunk text."""
        # Simplified recursive chunking
        if len(text) <= self.chunk_size:
            return [{
                "content": text,
                "metadata": metadata or {},
                "chunk_index": 0
            }]
        
        # Split on paragraphs first, then sentences
        paragraphs = text.split('\n\n')
        chunks = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) <= self.chunk_size:
                chunks.append({
                    "content": paragraph,
                    "metadata": metadata or {},
                    "chunk_index": i
                })
            else:
                # Further split large paragraphs
                sentences = paragraph.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) <= self.chunk_size:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append({
                                "content": current_chunk.strip(),
                                "metadata": metadata or {},
                                "chunk_index": len(chunks)
                            })
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append({
                        "content": current_chunk.strip(),
                        "metadata": metadata or {},
                        "chunk_index": len(chunks)
                    })
        
        return chunks
