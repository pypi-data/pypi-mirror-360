"""Tests for memory management components."""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from agentic_rag.core.memory import (
    MemoryItem,
    Memory,
    WorkingMemory,
    LongTermMemory
)
from agentic_rag.utils.exceptions import MemoryError


class TestMemoryItem:
    """Test MemoryItem model."""
    
    def test_memory_item_creation(self):
        """Test creating a memory item."""
        item = MemoryItem(
            content="Test memory content",
            metadata={"type": "test"},
            importance=0.8
        )
        
        assert item.content == "Test memory content"
        assert item.metadata["type"] == "test"
        assert item.importance == 0.8
        assert item.access_count == 0
        assert item.last_accessed is None
    
    def test_memory_item_access(self):
        """Test accessing a memory item."""
        item = MemoryItem(content="Test content")
        
        initial_count = item.access_count
        item.access()
        
        assert item.access_count == initial_count + 1
        assert item.last_accessed is not None
    
    def test_memory_item_expiration(self):
        """Test memory item expiration."""
        # Create item with old timestamp
        old_time = datetime.now() - timedelta(hours=2)
        item = MemoryItem(content="Test content", timestamp=old_time)
        
        # Test expiration with 1 hour TTL
        ttl = timedelta(hours=1)
        assert item.is_expired(ttl) is True
        
        # Test with longer TTL
        ttl = timedelta(hours=3)
        assert item.is_expired(ttl) is False


@pytest.mark.asyncio
class TestWorkingMemory:
    """Test WorkingMemory implementation."""
    
    def test_working_memory_initialization(self):
        """Test working memory initialization."""
        memory = WorkingMemory(max_size=50, ttl_minutes=30)
        
        assert memory.max_size == 50
        assert memory.ttl == timedelta(minutes=30)
        assert memory.size() == 0
    
    async def test_store_memory_item(self):
        """Test storing a memory item."""
        memory = WorkingMemory(max_size=10)

        item_id = memory.store(
            "Test memory content",
            metadata={"type": "test"},
            importance=0.7
        )
        
        assert item_id is not None
        assert memory.size() == 1
        
        # Retrieve the item
        item = memory.get(item_id)
        assert item is not None
        assert item.content == "Test memory content"
        assert item.importance == 0.7
    
    async def test_retrieve_memory_items(self):
        """Test retrieving memory items."""
        memory = WorkingMemory(max_size=10)

        # Store multiple items
        memory.store("Python programming language", importance=0.8)
        memory.store("Machine learning algorithms", importance=0.9)
        memory.store("Data science techniques", importance=0.7)

        # Retrieve items related to "programming"
        results = memory.retrieve("programming", top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(item, MemoryItem) for item in results)
        
        # Check that items were accessed
        for item in results:
            assert item.access_count > 0
    
    async def test_update_memory_item(self):
        """Test updating a memory item."""
        memory = WorkingMemory(max_size=10)

        item_id = memory.store("Original content")

        # Update the item
        success = memory.update(
            item_id,
            content="Updated content",
            metadata={"updated": True}
        )
        
        assert success is True
        
        item = memory.get(item_id)
        assert item.content == "Updated content"
        assert item.metadata["updated"] is True
    
    async def test_delete_memory_item(self):
        """Test deleting a memory item."""
        memory = WorkingMemory(max_size=10)

        item_id = memory.store("Content to delete")
        assert memory.size() == 1

        success = memory.delete(item_id)
        assert success is True
        assert memory.size() == 0
        assert memory.get(item_id) is None
    
    async def test_memory_eviction(self):
        """Test memory eviction when at capacity."""
        memory = WorkingMemory(max_size=2)

        # Fill memory to capacity
        id1 = memory.store("Content 1", importance=0.3)
        id2 = memory.store("Content 2", importance=0.7)

        assert memory.size() == 2

        # Add another item, should evict the least important
        id3 = memory.store("Content 3", importance=0.5)
        
        assert memory.size() == 2
        assert memory.get(id1) is None  # Should be evicted (lowest importance)
        assert memory.get(id2) is not None
        assert memory.get(id3) is not None
    
    async def test_expired_item_cleanup(self):
        """Test cleanup of expired items."""
        memory = WorkingMemory(max_size=10, ttl_minutes=0)  # Immediate expiration

        # Store an item
        item_id = memory.store("Expiring content")
        assert memory.size() == 1

        # Wait a bit and try to retrieve (should trigger cleanup)
        await asyncio.sleep(0.01)
        results = memory.retrieve("content")
        
        # Item should be expired and cleaned up
        assert len(results) == 0
        assert memory.size() == 0
    
    def test_clear_memory(self):
        """Test clearing all memory."""
        memory = WorkingMemory(max_size=10)
        memory._items["test"] = MemoryItem(content="Test")
        
        assert memory.size() == 1
        memory.clear()
        assert memory.size() == 0


@pytest.mark.asyncio
class TestLongTermMemory:
    """Test LongTermMemory implementation."""
    
    @pytest.fixture
    def temp_file(self):
        """Create temporary file for persistence testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_long_term_memory_initialization(self):
        """Test long-term memory initialization."""
        memory = LongTermMemory(max_size=1000)
        
        assert memory.max_size == 1000
        assert memory.size() == 0
        assert memory.persistence_file is None
    
    def test_long_term_memory_with_persistence(self, temp_file):
        """Test long-term memory with persistence file."""
        memory = LongTermMemory(max_size=100, persistence_file=temp_file)
        
        assert memory.persistence_file == temp_file
        # File may be created during initialization, that's okay
    
    async def test_store_and_retrieve(self):
        """Test storing and retrieving from long-term memory."""
        memory = LongTermMemory(max_size=100)

        # Store items with different importance
        id1 = memory.store("Important information", importance=0.9)
        id2 = memory.store("Less important info", importance=0.3)
        id3 = memory.store("Machine learning concepts", importance=0.8)

        assert memory.size() == 3

        # Retrieve items related to "machine learning"
        results = memory.retrieve("machine learning", top_k=2)
        
        assert len(results) <= 2
        # Should prioritize higher importance items
        if len(results) > 1:
            assert results[0].importance >= results[1].importance
    
    async def test_persistence_save_load(self, temp_file):
        """Test saving and loading memory from file."""
        # Create memory with persistence
        memory1 = LongTermMemory(max_size=100, persistence_file=temp_file)
        
        # Store some items
        memory1.store("Persistent memory 1", metadata={"type": "test"})
        memory1.store("Persistent memory 2", importance=0.8)
        
        assert memory1.size() == 2
        assert os.path.exists(temp_file)
        
        # Create new memory instance and load from file
        memory2 = LongTermMemory(max_size=100, persistence_file=temp_file)
        
        assert memory2.size() == 2
        
        # Verify content is preserved
        results = memory2.retrieve("persistent", top_k=5)
        assert len(results) == 2
    
    async def test_update_with_persistence(self, temp_file):
        """Test updating items with persistence."""
        memory = LongTermMemory(max_size=100, persistence_file=temp_file)
        
        item_id = memory.store("Original content")

        # Update the item
        success = memory.update(item_id, content="Updated content")
        assert success is True
        
        # Verify persistence
        memory2 = LongTermMemory(max_size=100, persistence_file=temp_file)
        item = memory2.get(item_id)
        assert item.content == "Updated content"
    
    async def test_delete_with_persistence(self, temp_file):
        """Test deleting items with persistence."""
        memory = LongTermMemory(max_size=100, persistence_file=temp_file)
        
        item_id = memory.store("Content to delete")
        assert memory.size() == 1

        success = memory.delete(item_id)
        assert success is True
        assert memory.size() == 0
        
        # Verify persistence
        memory2 = LongTermMemory(max_size=100, persistence_file=temp_file)
        assert memory2.size() == 0
    
    async def test_importance_based_retrieval(self):
        """Test retrieval based on importance and recency."""
        memory = LongTermMemory(max_size=100)
        
        # Store items with different importance and simulate age
        old_time = datetime.now() - timedelta(days=30)
        
        # Old but important item
        item1 = MemoryItem(
            content="Old important information",
            importance=0.9,
            timestamp=old_time
        )
        memory._items["old_important"] = item1
        
        # Recent but less important item
        memory.store("Recent less important info", importance=0.3)

        # Recent and important item
        memory.store("Recent important information", importance=0.8)

        # Retrieve items
        results = memory.retrieve("important information", top_k=3)
        
        # Should consider both importance and recency
        assert len(results) >= 2
        
        # Recent important should score higher than old important due to recency
        recent_important = next((r for r in results if "Recent important" in r.content), None)
        old_important = next((r for r in results if "Old important" in r.content), None)
        
        if recent_important and old_important:
            # Both should be retrieved, but recent should be ranked higher
            recent_rank = next(i for i, r in enumerate(results) if r == recent_important)
            old_rank = next(i for i, r in enumerate(results) if r == old_important)
            assert recent_rank <= old_rank
    
    def test_memory_error_handling(self):
        """Test memory error handling."""
        # Test with invalid persistence file path
        with pytest.raises(MemoryError):
            memory = LongTermMemory(persistence_file="/invalid/path/file.json")
            memory._save_to_file()


class TestMemoryIntegration:
    """Integration tests for memory components."""
    
    @pytest.mark.asyncio
    async def test_memory_workflow(self):
        """Test complete memory workflow."""
        working_memory = WorkingMemory(max_size=5, ttl_minutes=60)
        long_term_memory = LongTermMemory(max_size=100)
        
        # Store information in working memory
        query = "What is machine learning?"
        response = "Machine learning is a subset of AI that enables computers to learn from data."
        
        working_id = working_memory.store(
            f"Q: {query}\nA: {response}",
            metadata={"type": "qa_pair"},
            importance=0.7
        )

        # Store important information in long-term memory
        long_term_id = long_term_memory.store(
            "Machine learning is a fundamental concept in AI",
            metadata={"domain": "ai", "concept": "machine_learning"},
            importance=0.9
        )

        # Retrieve from both memories
        working_results = working_memory.retrieve("machine learning", top_k=3)
        long_term_results = long_term_memory.retrieve("machine learning", top_k=3)
        
        assert len(working_results) >= 1
        assert len(long_term_results) >= 1
        
        # Verify content
        working_item = working_results[0]
        long_term_item = long_term_results[0]
        
        assert "machine learning" in working_item.content.lower()
        assert "machine learning" in long_term_item.content.lower()
        assert working_item.access_count > 0
        assert long_term_item.access_count > 0
