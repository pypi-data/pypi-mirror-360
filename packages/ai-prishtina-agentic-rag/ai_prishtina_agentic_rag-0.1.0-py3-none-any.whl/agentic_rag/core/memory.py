"""Memory management for agentic RAG systems."""

import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..utils.exceptions import MemoryError
from ..utils.logging import LoggerMixin


class MemoryItem(BaseModel):
    """Represents a single memory item."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(description="Memory content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(default=None)
    
    def access(self) -> None:
        """Mark this memory item as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def is_expired(self, ttl: timedelta) -> bool:
        """Check if this memory item has expired."""
        if self.last_accessed:
            return datetime.now() - self.last_accessed > ttl
        return datetime.now() - self.timestamp > ttl


class Memory(ABC, LoggerMixin):
    """Abstract base class for memory systems."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._items: Dict[str, MemoryItem] = {}
    
    @abstractmethod
    def store(self, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 0.5) -> str:
        """Store a memory item."""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memory items."""
        pass
    
    @abstractmethod
    def update(self, item_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory item."""
        pass
    
    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """Delete a memory item."""
        pass
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """Get a specific memory item by ID."""
        item = self._items.get(item_id)
        if item:
            item.access()
        return item
    
    def list_all(self) -> List[MemoryItem]:
        """List all memory items."""
        return list(self._items.values())
    
    def clear(self) -> None:
        """Clear all memory items."""
        self._items.clear()
        self.logger.info("Memory cleared")
    
    def size(self) -> int:
        """Get the number of memory items."""
        return len(self._items)
    
    def is_full(self) -> bool:
        """Check if memory is at capacity."""
        return len(self._items) >= self.max_size
    
    def _evict_items(self, count: int = 1) -> None:
        """Evict the least important/oldest items."""
        if count <= 0:
            return
        
        # Sort by importance (ascending) and last accessed (ascending)
        items_to_evict = sorted(
            self._items.values(),
            key=lambda x: (x.importance, x.last_accessed or x.timestamp)
        )[:count]
        
        for item in items_to_evict:
            del self._items[item.id]
            self.logger.debug(f"Evicted memory item: {item.id}")


class WorkingMemory(Memory):
    """Working memory for short-term context and reasoning."""
    
    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        super().__init__(max_size)
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def store(self, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 0.5) -> str:
        """Store a memory item in working memory."""
        # Clean expired items first
        self._clean_expired()
        
        # Evict items if at capacity
        if self.is_full():
            self._evict_items(1)
        
        item = MemoryItem(
            content=content,
            metadata=metadata or {},
            importance=importance
        )
        
        self._items[item.id] = item
        self.logger.debug(f"Stored working memory item: {item.id}")
        return item.id
    
    def retrieve(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memory items from working memory."""
        self._clean_expired()
        
        # Simple keyword-based retrieval (can be enhanced with embeddings)
        query_words = set(query.lower().split())
        scored_items = []
        
        for item in self._items.values():
            content_words = set(item.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            if overlap > 0:
                score = overlap / len(query_words) * item.importance
                scored_items.append((score, item))
        
        # Sort by score and return top_k
        scored_items.sort(key=lambda x: x[0], reverse=True)
        result = [item for _, item in scored_items[:top_k]]
        
        # Mark as accessed
        for item in result:
            item.access()
        
        return result
    
    def update(self, item_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory item in working memory."""
        if not item_id or item_id not in self._items:
            return False

        item = self._items[item_id]
        if content is not None:
            item.content = content
        if metadata is not None:
            item.metadata.update(metadata)

        item.access()
        self.logger.debug(f"Updated working memory item: {item_id}")
        return True
    
    def delete(self, item_id: str) -> bool:
        """Delete a memory item from working memory."""
        if item_id in self._items:
            del self._items[item_id]
            self.logger.debug(f"Deleted working memory item: {item_id}")
            return True
        return False
    
    def _clean_expired(self) -> None:
        """Remove expired items from working memory."""
        expired_ids = [
            item_id for item_id, item in self._items.items()
            if item.is_expired(self.ttl)
        ]
        
        for item_id in expired_ids:
            del self._items[item_id]
            self.logger.debug(f"Expired working memory item: {item_id}")


class LongTermMemory(Memory):
    """Long-term memory for persistent knowledge and experiences."""
    
    def __init__(self, max_size: int = 10000, persistence_file: Optional[str] = None):
        super().__init__(max_size)
        self.persistence_file = persistence_file
        
        if self.persistence_file:
            self._load_from_file()
    
    def store(self, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 0.5) -> str:
        """Store a memory item in long-term memory."""
        # Evict items if at capacity
        if self.is_full():
            self._evict_items(1)
        
        item = MemoryItem(
            content=content,
            metadata=metadata or {},
            importance=importance
        )
        
        self._items[item.id] = item
        self.logger.debug(f"Stored long-term memory item: {item.id}")
        
        if self.persistence_file:
            self._save_to_file()
        
        return item.id
    
    def retrieve(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memory items from long-term memory."""
        # Enhanced retrieval with importance weighting
        query_words = set(query.lower().split())
        scored_items = []
        
        for item in self._items.values():
            content_words = set(item.content.lower().split())
            overlap = len(query_words.intersection(content_words))
            if overlap > 0:
                # Score based on overlap, importance, and recency
                recency_factor = 1.0 / (1.0 + (datetime.now() - item.timestamp).days / 30.0)
                score = (overlap / len(query_words)) * item.importance * recency_factor
                scored_items.append((score, item))
        
        # Sort by score and return top_k
        scored_items.sort(key=lambda x: x[0], reverse=True)
        result = [item for _, item in scored_items[:top_k]]
        
        # Mark as accessed
        for item in result:
            item.access()
        
        if self.persistence_file:
            self._save_to_file()
        
        return result
    
    def update(self, item_id: str, content: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory item in long-term memory."""
        if not item_id or item_id not in self._items:
            return False

        item = self._items[item_id]
        if content is not None:
            item.content = content
        if metadata is not None:
            item.metadata.update(metadata)

        item.access()
        self.logger.debug(f"Updated long-term memory item: {item_id}")

        if self.persistence_file:
            self._save_to_file()

        return True
    
    def delete(self, item_id: str) -> bool:
        """Delete a memory item from long-term memory."""
        if item_id in self._items:
            del self._items[item_id]
            self.logger.debug(f"Deleted long-term memory item: {item_id}")
            
            if self.persistence_file:
                self._save_to_file()
            
            return True
        return False
    
    def _save_to_file(self) -> None:
        """Save memory to persistence file."""
        if not self.persistence_file:
            return
        
        try:
            data = {
                item_id: item.model_dump() for item_id, item in self._items.items()
            }
            with open(self.persistence_file, 'w') as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            raise MemoryError(f"Failed to save memory to file: {e}")
    
    def _load_from_file(self) -> None:
        """Load memory from persistence file."""
        if not self.persistence_file:
            return

        try:
            with open(self.persistence_file, 'r') as f:
                content = f.read().strip()
                if not content:
                    # Empty file, start with empty memory
                    self.logger.info("Empty memory file, starting with empty memory")
                    return
                data = json.loads(content)

            for item_id, item_data in data.items():
                # Convert timestamp strings back to datetime objects
                if 'timestamp' in item_data:
                    item_data['timestamp'] = datetime.fromisoformat(item_data['timestamp'])
                if 'last_accessed' in item_data and item_data['last_accessed']:
                    item_data['last_accessed'] = datetime.fromisoformat(item_data['last_accessed'])

                self._items[item_id] = MemoryItem(**item_data)

            self.logger.info(f"Loaded {len(self._items)} items from memory file")
        except FileNotFoundError:
            self.logger.info("Memory file not found, starting with empty memory")
        except Exception as e:
            raise MemoryError(f"Failed to load memory from file: {e}")
