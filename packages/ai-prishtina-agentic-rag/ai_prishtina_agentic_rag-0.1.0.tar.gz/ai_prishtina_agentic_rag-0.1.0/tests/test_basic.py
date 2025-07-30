"""Basic tests for the Agentic RAG library."""

import pytest
from pathlib import Path

from agentic_rag import AgenticRAG
from agentic_rag.document_processing import DocumentLoader, Document
from agentic_rag.utils.config import Config
from agentic_rag.utils.exceptions import AgenticRAGError, DocumentProcessingError


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = Config()
        assert config.llm.provider == "openai"
        assert config.vector_store.provider == "chroma"
        assert config.agent.enable_planning is True
    
    def test_config_update(self):
        """Test configuration updates."""
        config = Config()
        updated_config = config.update(**{"llm.temperature": 0.5})
        assert updated_config.llm.temperature == 0.5


class TestDocumentLoader:
    """Test document loading functionality."""
    
    def test_document_creation(self):
        """Test Document model creation."""
        doc = Document(
            content="Test content",
            metadata={"title": "Test"},
            source="test.txt",
            doc_type="text"
        )
        assert doc.content == "Test content"
        assert doc.metadata["title"] == "Test"
    
    def test_loader_initialization(self):
        """Test DocumentLoader initialization."""
        loader = DocumentLoader()
        assert len(loader.loaders) > 0
    
    def test_load_nonexistent_file(self):
        """Test loading a non-existent file."""
        loader = DocumentLoader()
        with pytest.raises(DocumentProcessingError):
            loader.load_file("nonexistent_file.txt")


class TestAgenticRAG:
    """Test main AgenticRAG functionality."""
    
    def test_initialization(self):
        """Test AgenticRAG initialization."""
        rag = AgenticRAG()
        assert rag.config is not None
        assert rag.enable_agent is True
    
    def test_initialization_with_config(self):
        """Test AgenticRAG initialization with custom config."""
        config = Config()
        config.llm.temperature = 0.8
        
        rag = AgenticRAG(config=config)
        assert rag.config.llm.temperature == 0.8
    
    @pytest.mark.asyncio
    async def test_query_without_vector_store(self):
        """Test querying without a vector store."""
        rag = AgenticRAG()

        # Should handle gracefully or raise appropriate error
        with pytest.raises(AgenticRAGError):
            await rag.query("What is AI?")
    
    @pytest.mark.asyncio
    async def test_add_documents_without_vector_store(self):
        """Test adding documents without a vector store."""
        rag = AgenticRAG()

        with pytest.raises(AgenticRAGError):
            await rag.add_documents([{"content": "test", "source": "test.txt"}])


class TestIntegration:
    """Integration tests."""
    
    def test_basic_workflow(self):
        """Test basic workflow without external dependencies."""
        # Create sample documents
        sample_docs = [
            {
                "content": "AI is artificial intelligence",
                "metadata": {"title": "AI Intro"},
                "source": "ai.txt",
                "doc_type": "text"
            }
        ]
        
        # Initialize RAG system
        rag = AgenticRAG(enable_agent=False)
        
        # This should work even without vector store for basic functionality
        assert rag.config is not None
        assert rag.enable_agent is False


if __name__ == "__main__":
    pytest.main([__file__])
