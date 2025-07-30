"""
Comprehensive tests for all vector store implementations.
"""
import pytest
import asyncio
import tempfile
import os
from typing import List
from unittest.mock import Mock, patch

from agentic_rag.retrieval.vector_stores import (
    ChromaVectorStore,
    FAISSVectorStore,
    PineconeVectorStore,
    WeaviateVectorStore,
    VectorStoreError,
    Document,
    SearchResult
)


class TestVectorStoreComplete:
    """Test all vector store implementations comprehensively."""

    @pytest.fixture
    def sample_documents(self) -> List[Document]:
        """Create sample documents for testing."""
        return [
            Document(
                id="doc1",
                content="Artificial intelligence is transforming industries.",
                metadata={"source": "ai_article.txt", "topic": "AI"},
                embedding=[0.1, 0.2, 0.3, 0.4, 0.5]
            ),
            Document(
                id="doc2", 
                content="Machine learning algorithms are powerful tools.",
                metadata={"source": "ml_guide.pdf", "topic": "ML"},
                embedding=[0.2, 0.3, 0.4, 0.5, 0.6]
            ),
            Document(
                id="doc3",
                content="Deep learning networks process complex data.",
                metadata={"source": "dl_paper.pdf", "topic": "DL"},
                embedding=[0.3, 0.4, 0.5, 0.6, 0.7]
            )
        ]

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.mark.asyncio
    async def test_chroma_vector_store_complete(self, sample_documents, temp_dir):
        """Test ChromaDB vector store completely."""
        # Use a mock embedding function to avoid dimension mismatch
        with patch('agentic_rag.retrieval.vector_stores.SentenceTransformer') as mock_st:
            # Mock the embedding function to return embeddings with same dimension as test data
            mock_encoder = Mock()
            mock_encoder.encode.return_value = Mock()
            mock_encoder.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_st.return_value = mock_encoder

            store = ChromaVectorStore(
                collection_name="test_collection",
                persist_directory=temp_dir
            )

            # Test adding documents
            ids = await store.add_documents(sample_documents)
            assert len(ids) == 3

            # Test counting documents
            count = await store.count_documents()
            assert count == 3

            # Test searching
            results = await store.search("artificial intelligence", top_k=2)
            assert len(results) <= 2
            assert all(isinstance(r, SearchResult) for r in results)

            # Test getting document
            doc = await store.get_document("doc1")
            assert doc is not None
            assert doc.id == "doc1"
            assert "artificial intelligence" in doc.content.lower()

            # Test updating document
            updated_doc = Document(
                id="doc1",
                content="Updated: AI is revolutionizing technology.",
                metadata={"source": "updated_ai.txt", "topic": "AI"},
                embedding=[0.15, 0.25, 0.35, 0.45, 0.55]
            )
            success = await store.update_document(updated_doc)
            assert success

            # Test deleting documents
            success = await store.delete_documents(["doc1"])
            assert success

            # Verify deletion
            count = await store.count_documents()
            assert count == 2

    @pytest.mark.asyncio
    async def test_faiss_vector_store_complete(self, sample_documents, temp_dir):
        """Test FAISS vector store completely."""
        persist_path = os.path.join(temp_dir, "faiss_index.bin")
        
        store = FAISSVectorStore(
            dimension=5,
            persist_path=persist_path
        )
        
        # Test adding documents
        ids = await store.add_documents(sample_documents)
        assert len(ids) == 3
        
        # Test counting documents
        count = await store.count_documents()
        assert count == 3
        
        # Test searching
        results = await store.search("machine learning", top_k=2)
        assert len(results) <= 2
        
        # Test getting document
        doc = await store.get_document("doc2")
        assert doc is not None
        assert doc.id == "doc2"
        
        # Test persistence
        store._save_index()
        assert os.path.exists(persist_path)
        
        # Test loading from persistence
        new_store = FAISSVectorStore(
            dimension=5,
            persist_path=persist_path
        )
        count = await new_store.count_documents()
        assert count == 3

    @pytest.mark.asyncio
    async def test_pinecone_vector_store_mock(self, sample_documents):
        """Test Pinecone vector store with mocking."""
        with patch('pinecone.Pinecone') as mock_pinecone_class:
            # Mock Pinecone client and index
            mock_client = Mock()
            mock_index = Mock()
            mock_pinecone_class.return_value = mock_client
            mock_client.Index.return_value = mock_index
            
            # Mock upsert response
            mock_index.upsert.return_value = {"upserted_count": 3}
            
            # Mock query response
            mock_index.query.return_value = {
                "matches": [
                    {
                        "id": "doc1",
                        "score": 0.95,
                        "metadata": {"content": "AI content", "source": "ai.txt"}
                    }
                ]
            }
            
            # Mock stats response
            mock_index.describe_index_stats.return_value = Mock(total_vector_count=3)
            
            store = PineconeVectorStore(
                api_key="test-key",
                environment="test-env",
                index_name="test-index"
            )
            
            # Test adding documents
            ids = await store.add_documents(sample_documents)
            assert len(ids) == 3
            
            # Test searching
            results = await store.search("test query", top_k=1)
            assert len(results) == 1
            assert results[0].score == 0.95
            
            # Test counting
            count = await store.count_documents()
            assert count == 3

    @pytest.mark.asyncio
    async def test_weaviate_vector_store_mock(self, sample_documents):
        """Test Weaviate vector store with mocking."""
        with patch('weaviate.connect_to_local') as mock_connect:
            # Mock Weaviate client and collection
            mock_client = Mock()
            mock_collection = Mock()
            mock_connect.return_value = mock_client
            mock_client.collections.exists.return_value = True
            mock_client.collections.get.return_value = mock_collection
            
            # Mock insert response
            mock_collection.data.insert.return_value = "uuid-123"
            
            # Mock query response
            mock_query_result = Mock()
            mock_query_result.objects = [
                Mock(
                    uuid="uuid-123",
                    properties={"content": "AI content", "source": "ai.txt"},
                    metadata=Mock(distance=0.1)
                )
            ]
            mock_collection.query.near_vector.return_value = mock_query_result
            
            # Mock aggregate response
            mock_aggregate_result = Mock()
            mock_aggregate_result.total_count = 3
            mock_collection.aggregate.over_all.return_value = mock_aggregate_result
            
            store = WeaviateVectorStore(
                url="http://localhost:8080",
                class_name="TestClass"
            )
            
            # Test adding documents
            ids = await store.add_documents(sample_documents)
            assert len(ids) == 3
            
            # Test searching
            results = await store.search("test query", top_k=1)
            assert len(results) == 1
            
            # Test counting
            count = await store.count_documents()
            assert count == 3

    @pytest.mark.asyncio
    async def test_vector_store_error_handling(self):
        """Test error handling in vector stores."""
        # Test ChromaDB with invalid directory
        with pytest.raises(VectorStoreError):
            store = ChromaVectorStore(persist_directory="/invalid/path/that/does/not/exist")
        
        # Test FAISS with invalid dimension
        with pytest.raises(VectorStoreError):
            store = FAISSVectorStore(dimension=-1)
        
        # Test Pinecone without proper credentials
        with pytest.raises(VectorStoreError):
            store = PineconeVectorStore(api_key="", environment="", index_name="")

    def test_vector_store_initialization_errors(self):
        """Test initialization errors for vector stores."""
        # Test missing dependencies
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            with pytest.raises(VectorStoreError, match="not installed"):
                ChromaVectorStore()
