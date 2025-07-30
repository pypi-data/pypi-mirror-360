"""Text preprocessing utilities."""

import re
from typing import Dict, Any
from ..utils.logging import LoggerMixin


class TextPreprocessor(LoggerMixin):
    """Text preprocessing for documents."""
    
    def __init__(
        self,
        remove_extra_whitespace: bool = True,
        normalize_unicode: bool = True,
        remove_urls: bool = False,
        remove_emails: bool = False
    ):
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_unicode = normalize_unicode
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
    
    def preprocess(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Preprocess text."""
        processed_text = text
        
        if self.normalize_unicode:
            processed_text = self._normalize_unicode(processed_text)
        
        if self.remove_urls:
            processed_text = self._remove_urls(processed_text)
        
        if self.remove_emails:
            processed_text = self._remove_emails(processed_text)
        
        if self.remove_extra_whitespace:
            processed_text = self._remove_extra_whitespace(processed_text)
        
        return processed_text
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters."""
        import unicodedata
        return unicodedata.normalize('NFKC', text)
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def _remove_emails(self, text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.sub(email_pattern, '', text)
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace."""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
