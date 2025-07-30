"""Tests for vector store implementations."""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path

from agentic_rag.retrieval.vector_stores import (
    BaseVectorStore,
    ChromaVectorStore,
    FAISSVectorStore,
    Document,
    SearchResult
)
from agentic_rag.utils.exceptions import VectorStoreError


class TestDocument:
    """Test Document model."""
    
    def test_document_creation(self):
        """Test creating a document."""
        doc = Document(
            id="test_1",
            content="This is a test document",
            metadata={"source": "test.txt", "type": "text"}
        )
        
        assert doc.id == "test_1"
        assert doc.content == "This is a test document"
        assert doc.metadata["source"] == "test.txt"
        assert doc.embedding is None
    
    def test_document_with_embedding(self):
        """Test creating a document with embedding."""
        embedding = [0.1, 0.2, 0.3, 0.4]
        doc = Document(
            id="test_2",
            content="Test with embedding",
            embedding=embedding
        )
        
        assert doc.embedding == embedding


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a search result."""
        doc = Document(id="test_1", content="Test content")
        result = SearchResult(
            document=doc,
            score=0.95,
            rank=1
        )
        
        assert result.document.id == "test_1"
        assert result.score == 0.95
        assert result.rank == 1


@pytest.mark.asyncio
class TestFAISSVectorStore:
    """Test FAISS vector store implementation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def faiss_store(self, temp_dir):
        """Create FAISS vector store for testing."""
        persist_path = os.path.join(temp_dir, "test_index.faiss")
        return FAISSVectorStore(
            dimension=384,
            persist_path=persist_path,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    def test_faiss_initialization(self, faiss_store):
        """Test FAISS store initialization."""
        assert faiss_store.dimension == 384
        assert faiss_store._index is not None
        assert faiss_store._documents == {}
    
    async def test_add_documents(self, faiss_store):
        """Test adding documents to FAISS."""
        documents = [
            Document(id="doc1", content="This is about artificial intelligence"),
            Document(id="doc2", content="Machine learning is a subset of AI"),
            Document(id="doc3", content="Natural language processing uses neural networks")
        ]
        
        # Skip if sentence-transformers not available
        if not faiss_store._embedding_function:
            pytest.skip("sentence-transformers not available")
        
        doc_ids = await faiss_store.add_documents(documents)
        
        assert len(doc_ids) == 3
        assert doc_ids == ["doc1", "doc2", "doc3"]
        assert len(faiss_store._documents) == 3
    
    async def test_search_documents(self, faiss_store):
        """Test searching documents in FAISS."""
        documents = [
            Document(id="doc1", content="Python programming language"),
            Document(id="doc2", content="Machine learning algorithms"),
            Document(id="doc3", content="Data science and analytics")
        ]
        
        # Skip if sentence-transformers not available
        if not faiss_store._embedding_function:
            pytest.skip("sentence-transformers not available")
        
        await faiss_store.add_documents(documents)
        
        results = await faiss_store.search("programming", top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)
        if results:
            assert results[0].rank == 1
    
    async def test_get_document(self, faiss_store):
        """Test getting a document by ID."""
        doc = Document(id="test_doc", content="Test content")
        await faiss_store.add_documents([doc])
        
        retrieved_doc = await faiss_store.get_document("test_doc")
        
        assert retrieved_doc is not None
        assert retrieved_doc.id == "test_doc"
        assert retrieved_doc.content == "Test content"
    
    async def test_count_documents(self, faiss_store):
        """Test counting documents."""
        assert await faiss_store.count_documents() == 0
        
        documents = [
            Document(id="doc1", content="Content 1"),
            Document(id="doc2", content="Content 2")
        ]
        await faiss_store.add_documents(documents)
        
        assert await faiss_store.count_documents() == 2
    
    async def test_delete_documents(self, faiss_store):
        """Test deleting documents."""
        documents = [
            Document(id="doc1", content="Content 1"),
            Document(id="doc2", content="Content 2")
        ]
        await faiss_store.add_documents(documents)
        
        success = await faiss_store.delete_documents(["doc1"])
        
        assert success is True
        assert await faiss_store.count_documents() == 1
        assert await faiss_store.get_document("doc1") is None


@pytest.mark.asyncio
class TestChromaVectorStore:
    """Test ChromaDB vector store implementation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def chroma_store(self, temp_dir):
        """Create ChromaDB vector store for testing."""
        try:
            return ChromaVectorStore(
                collection_name="test_collection",
                persist_directory=temp_dir,
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
        except VectorStoreError as e:
            if "chromadb not installed" in str(e):
                pytest.skip("ChromaDB not available")
            raise
    
    def test_chroma_initialization(self, chroma_store):
        """Test ChromaDB store initialization."""
        assert chroma_store.collection_name == "test_collection"
        assert chroma_store._client is not None
        assert chroma_store._collection is not None
    
    async def test_add_documents_chroma(self, chroma_store):
        """Test adding documents to ChromaDB."""
        documents = [
            Document(id="doc1", content="Artificial intelligence research"),
            Document(id="doc2", content="Deep learning neural networks")
        ]
        
        # Skip if sentence-transformers not available
        if not chroma_store._embedding_function:
            pytest.skip("sentence-transformers not available")
        
        doc_ids = await chroma_store.add_documents(documents)
        
        assert len(doc_ids) == 2
        assert doc_ids == ["doc1", "doc2"]
    
    async def test_search_documents_chroma(self, chroma_store):
        """Test searching documents in ChromaDB."""
        documents = [
            Document(id="doc1", content="Python programming tutorial"),
            Document(id="doc2", content="JavaScript web development"),
            Document(id="doc3", content="Data analysis with pandas")
        ]
        
        # Skip if sentence-transformers not available
        if not chroma_store._embedding_function:
            pytest.skip("sentence-transformers not available")
        
        await chroma_store.add_documents(documents)
        
        results = await chroma_store.search("Python programming", top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)
        if results:
            assert 0.0 <= results[0].score <= 1.0
    
    async def test_get_document_chroma(self, chroma_store):
        """Test getting a document by ID from ChromaDB."""
        doc = Document(
            id="test_doc",
            content="Test content for retrieval",
            metadata={"type": "test"}
        )
        await chroma_store.add_documents([doc])
        
        retrieved_doc = await chroma_store.get_document("test_doc")
        
        assert retrieved_doc is not None
        assert retrieved_doc.id == "test_doc"
        assert retrieved_doc.content == "Test content for retrieval"
        assert retrieved_doc.metadata["type"] == "test"
    
    async def test_count_documents_chroma(self, chroma_store):
        """Test counting documents in ChromaDB."""
        initial_count = await chroma_store.count_documents()
        
        documents = [
            Document(id="doc1", content="Content 1"),
            Document(id="doc2", content="Content 2"),
            Document(id="doc3", content="Content 3")
        ]
        await chroma_store.add_documents(documents)
        
        final_count = await chroma_store.count_documents()
        assert final_count == initial_count + 3
    
    async def test_delete_documents_chroma(self, chroma_store):
        """Test deleting documents from ChromaDB."""
        documents = [
            Document(id="doc1", content="Content to delete"),
            Document(id="doc2", content="Content to keep")
        ]
        await chroma_store.add_documents(documents)
        
        initial_count = await chroma_store.count_documents()
        success = await chroma_store.delete_documents(["doc1"])
        final_count = await chroma_store.count_documents()
        
        assert success is True
        assert final_count == initial_count - 1
        assert await chroma_store.get_document("doc1") is None
        assert await chroma_store.get_document("doc2") is not None


class TestBaseVectorStore:
    """Test base vector store functionality."""
    
    def test_embedding_initialization(self):
        """Test embedding function initialization."""
        # Create a mock vector store
        class MockVectorStore(BaseVectorStore):
            async def add_documents(self, documents):
                pass
            async def search(self, query, top_k=5, filters=None):
                pass
            async def delete_documents(self, document_ids):
                pass
            async def update_document(self, document):
                pass
            async def get_document(self, document_id):
                pass
            async def count_documents(self):
                pass
        
        store = MockVectorStore()
        
        # Test that embedding model is set
        assert store.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_embed_text_without_model(self):
        """Test embedding text without model raises error."""
        class MockVectorStore(BaseVectorStore):
            def __init__(self):
                super().__init__()
                self._embedding_function = None  # Simulate no model
            
            async def add_documents(self, documents):
                pass
            async def search(self, query, top_k=5, filters=None):
                pass
            async def delete_documents(self, document_ids):
                pass
            async def update_document(self, document):
                pass
            async def get_document(self, document_id):
                pass
            async def count_documents(self):
                pass
        
        store = MockVectorStore()
        
        with pytest.raises(VectorStoreError, match="Embedding function not initialized"):
            store._embed_text("test text")
