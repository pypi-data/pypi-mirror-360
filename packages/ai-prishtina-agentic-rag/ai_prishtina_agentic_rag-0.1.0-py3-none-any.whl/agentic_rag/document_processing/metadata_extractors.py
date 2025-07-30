"""Metadata extraction utilities."""

from typing import Dict, Any
from ..utils.logging import LoggerMixin


class MetadataExtractor(LoggerMixin):
    """Extract metadata from documents."""
    
    def extract(self, text: str, source: str = None) -> Dict[str, Any]:
        """Extract metadata from text."""
        metadata = {}
        
        # Basic text statistics
        metadata.update({
            "char_count": len(text),
            "word_count": len(text.split()),
            "line_count": len(text.split('\n')),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
        })
        
        if source:
            metadata["source"] = source
        
        return metadata
