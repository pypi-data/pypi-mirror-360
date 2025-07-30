"""Tests for configuration management."""

import os
import tempfile
import pytest
from pathlib import Path

from agentic_rag.utils.config import (
    Config,
    LLMConfig,
    VectorStoreConfig,
    RetrievalConfig,
    DocumentProcessingConfig,
    AgentConfig,
    EvaluationConfig
)
from agentic_rag.utils.exceptions import ConfigurationError


class TestLLMConfig:
    """Test LLM configuration."""
    
    def test_llm_config_defaults(self):
        """Test LLM config default values."""
        config = LLMConfig()
        
        assert config.provider == "openai"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.timeout == 30
    
    def test_llm_config_custom_values(self):
        """Test LLM config with custom values."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-sonnet-20240229",
            temperature=0.5,
            max_tokens=2000
        )
        
        assert config.provider == "anthropic"
        assert config.model == "claude-3-sonnet-20240229"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000


class TestVectorStoreConfig:
    """Test vector store configuration."""
    
    def test_vector_store_config_defaults(self):
        """Test vector store config default values."""
        config = VectorStoreConfig()
        
        assert config.provider == "chroma"
        assert config.collection_name == "agentic_rag"
        assert config.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
    
    def test_vector_store_config_custom_values(self):
        """Test vector store config with custom values."""
        config = VectorStoreConfig(
            provider="pinecone",
            collection_name="my_collection",
            persist_directory="/custom/path"
        )
        
        assert config.provider == "pinecone"
        assert config.collection_name == "my_collection"
        assert config.persist_directory == "/custom/path"


class TestRetrievalConfig:
    """Test retrieval configuration."""
    
    def test_retrieval_config_defaults(self):
        """Test retrieval config default values."""
        config = RetrievalConfig()
        
        assert config.top_k == 5
        assert config.similarity_threshold == 0.7
        assert config.enable_reranking is True
        assert config.enable_hybrid_search is False
        assert config.dense_weight == 0.7
        assert config.sparse_weight == 0.3
    
    def test_retrieval_config_weight_validation(self):
        """Test retrieval config weight validation."""
        # Valid weights
        config = RetrievalConfig(dense_weight=0.6, sparse_weight=0.4)
        assert config.dense_weight == 0.6
        assert config.sparse_weight == 0.4
        
        # Invalid weights (don't sum to 1.0)
        with pytest.raises(ValueError, match="Dense and sparse weights must sum to 1.0"):
            RetrievalConfig(dense_weight=0.6, sparse_weight=0.5)


class TestDocumentProcessingConfig:
    """Test document processing configuration."""
    
    def test_document_processing_config_defaults(self):
        """Test document processing config default values."""
        config = DocumentProcessingConfig()
        
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.chunking_strategy == "recursive"
        assert config.enable_preprocessing is True
    
    def test_document_processing_config_custom_values(self):
        """Test document processing config with custom values."""
        config = DocumentProcessingConfig(
            chunk_size=500,
            chunk_overlap=100,
            chunking_strategy="semantic",
            enable_preprocessing=False
        )
        
        assert config.chunk_size == 500
        assert config.chunk_overlap == 100
        assert config.chunking_strategy == "semantic"
        assert config.enable_preprocessing is False


class TestAgentConfig:
    """Test agent configuration."""
    
    def test_agent_config_defaults(self):
        """Test agent config default values."""
        config = AgentConfig()
        
        assert config.enable_planning is True
        assert config.max_planning_steps == 5
        assert config.enable_memory is True
        assert config.enable_tools is True
        assert config.available_tools == ["web_search", "calculator"]
    
    def test_agent_config_custom_values(self):
        """Test agent config with custom values."""
        config = AgentConfig(
            enable_planning=False,
            max_planning_steps=3,
            available_tools=["calculator", "web_search", "code_executor"]
        )
        
        assert config.enable_planning is False
        assert config.max_planning_steps == 3
        assert len(config.available_tools) == 3
        assert "code_executor" in config.available_tools


class TestEvaluationConfig:
    """Test evaluation configuration."""
    
    def test_evaluation_config_defaults(self):
        """Test evaluation config default values."""
        config = EvaluationConfig()
        
        assert config.enable_evaluation is False
        assert config.metrics == ["relevance", "faithfulness"]
        assert config.log_level == "INFO"
    
    def test_evaluation_config_custom_values(self):
        """Test evaluation config with custom values."""
        config = EvaluationConfig(
            enable_evaluation=True,
            metrics=["relevance", "faithfulness", "answer_quality", "latency"],
            log_level="DEBUG"
        )
        
        assert config.enable_evaluation is True
        assert len(config.metrics) == 4
        assert "answer_quality" in config.metrics
        assert config.log_level == "DEBUG"


class TestConfig:
    """Test main configuration class."""
    
    def test_config_defaults(self):
        """Test config default values."""
        config = Config()
        
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.vector_store, VectorStoreConfig)
        assert isinstance(config.retrieval, RetrievalConfig)
        assert isinstance(config.document_processing, DocumentProcessingConfig)
        assert isinstance(config.agent, AgentConfig)
        assert isinstance(config.evaluation, EvaluationConfig)
    
    def test_config_custom_values(self):
        """Test config with custom values."""
        config = Config(
            llm=LLMConfig(provider="anthropic"),
            vector_store=VectorStoreConfig(provider="pinecone"),
            agent=AgentConfig(enable_planning=False)
        )
        
        assert config.llm.provider == "anthropic"
        assert config.vector_store.provider == "pinecone"
        assert config.agent.enable_planning is False
    
    def test_config_update(self):
        """Test config update functionality."""
        config = Config()
        
        # Test nested update
        updated_config = config.update(**{
            "llm.temperature": 0.5,
            "vector_store.collection_name": "test_collection",
            "agent.max_planning_steps": 3
        })
        
        assert updated_config.llm.temperature == 0.5
        assert updated_config.vector_store.collection_name == "test_collection"
        assert updated_config.agent.max_planning_steps == 3
        
        # Original config should be unchanged
        assert config.llm.temperature == 0.7
        assert config.vector_store.collection_name == "agentic_rag"
        assert config.agent.max_planning_steps == 5
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "llm": {
                "provider": "anthropic",
                "model": "claude-3-sonnet-20240229",
                "temperature": 0.8
            },
            "vector_store": {
                "provider": "faiss",
                "collection_name": "test_faiss"
            },
            "agent": {
                "enable_planning": False,
                "available_tools": ["calculator"]
            }
        }
        
        config = Config.from_dict(config_dict)
        
        assert config.llm.provider == "anthropic"
        assert config.llm.model == "claude-3-sonnet-20240229"
        assert config.llm.temperature == 0.8
        assert config.vector_store.provider == "faiss"
        assert config.vector_store.collection_name == "test_faiss"
        assert config.agent.enable_planning is False
        assert config.agent.available_tools == ["calculator"]
    
    def test_config_from_env(self):
        """Test creating config from environment variables."""
        # Set environment variables
        env_vars = {
            "AGENTIC_RAG_LLM_PROVIDER": "anthropic",
            "AGENTIC_RAG_LLM_MODEL": "claude-3-sonnet-20240229",
            "AGENTIC_RAG_LLM_TEMPERATURE": "0.8",
            "AGENTIC_RAG_VECTOR_STORE_PROVIDER": "pinecone",
            "AGENTIC_RAG_VECTOR_STORE_COLLECTION_NAME": "env_collection",
            "AGENTIC_RAG_AGENT_ENABLE_PLANNING": "false"
        }
        
        with pytest.MonkeyPatch.context() as m:
            for key, value in env_vars.items():
                m.setenv(key, value)

            # Create a fresh config instance to pick up env vars
            config = Config.from_env()
            
            assert config.llm.provider == "anthropic"
            assert config.llm.model == "claude-3-sonnet-20240229"
            assert config.llm.temperature == 0.8
            assert config.vector_store.provider == "pinecone"
            assert config.vector_store.collection_name == "env_collection"
            assert config.agent.enable_planning is False
    
    def test_config_to_file_and_from_file(self):
        """Test saving config to file and loading from file."""
        config = Config(
            llm=LLMConfig(provider="anthropic", temperature=0.8),
            vector_store=VectorStoreConfig(provider="pinecone"),
            agent=AgentConfig(enable_planning=False)
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            # Save to file
            config.to_file(temp_path)
            
            # Load from file
            loaded_config = Config.from_file(temp_path)
            
            assert loaded_config.llm.provider == "anthropic"
            assert loaded_config.llm.temperature == 0.8
            assert loaded_config.vector_store.provider == "pinecone"
            assert loaded_config.agent.enable_planning is False
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_config_from_nonexistent_file(self):
        """Test loading config from non-existent file."""
        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            Config.from_file("/nonexistent/path/config.yaml")
    
    def test_config_from_invalid_yaml(self):
        """Test loading config from invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            with pytest.raises(ConfigurationError, match="Invalid YAML in configuration file"):
                Config.from_file(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            llm=LLMConfig(provider="anthropic", temperature=0.8),
            vector_store=VectorStoreConfig(provider="pinecone")
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["llm"]["provider"] == "anthropic"
        assert config_dict["llm"]["temperature"] == 0.8
        assert config_dict["vector_store"]["provider"] == "pinecone"
    
    def test_config_validation(self):
        """Test config validation."""
        # Test weight validation
        with pytest.raises(ValueError, match="Dense and sparse weights must sum to 1.0"):
            Config(retrieval=RetrievalConfig(dense_weight=0.6, sparse_weight=0.5))


class TestConfigIntegration:
    """Integration tests for configuration."""
    
    def test_config_environment_override(self):
        """Test that environment variables override defaults."""
        with pytest.MonkeyPatch.context() as m:
            m.setenv("AGENTIC_RAG_LLM_TEMPERATURE", "0.9")
            m.setenv("AGENTIC_RAG_VECTOR_STORE_COLLECTION_NAME", "override_collection")
            
            config = Config.from_env()
            
            assert config.llm.temperature == 0.9
            assert config.vector_store.collection_name == "override_collection"
            # Other values should remain default
            assert config.llm.provider == "openai"
            assert config.vector_store.provider == "chroma"
    
    def test_config_partial_update(self):
        """Test partial configuration updates."""
        config = Config()
        
        # Update only specific fields
        updated = config.update(**{
            "llm.temperature": 0.9,
            "agent.enable_planning": False
        })
        
        # Updated fields should change
        assert updated.llm.temperature == 0.9
        assert updated.agent.enable_planning is False
        
        # Other fields should remain unchanged
        assert updated.llm.provider == "openai"
        assert updated.llm.model == "gpt-3.5-turbo"
        assert updated.vector_store.provider == "chroma"
    
    def test_config_serialization_roundtrip(self):
        """Test config serialization and deserialization roundtrip."""
        original_config = Config(
            llm=LLMConfig(
                provider="anthropic",
                model="claude-3-sonnet-20240229",
                temperature=0.8,
                max_tokens=2000
            ),
            vector_store=VectorStoreConfig(
                provider="pinecone",
                collection_name="test_collection"
            ),
            agent=AgentConfig(
                enable_planning=False,
                max_planning_steps=3,
                available_tools=["calculator", "web_search"]
            )
        )
        
        # Convert to dict and back
        config_dict = original_config.to_dict()
        restored_config = Config.from_dict(config_dict)
        
        # Should be identical
        assert restored_config.llm.provider == original_config.llm.provider
        assert restored_config.llm.model == original_config.llm.model
        assert restored_config.llm.temperature == original_config.llm.temperature
        assert restored_config.llm.max_tokens == original_config.llm.max_tokens
        assert restored_config.vector_store.provider == original_config.vector_store.provider
        assert restored_config.vector_store.collection_name == original_config.vector_store.collection_name
        assert restored_config.agent.enable_planning == original_config.agent.enable_planning
        assert restored_config.agent.max_planning_steps == original_config.agent.max_planning_steps
        assert restored_config.agent.available_tools == original_config.agent.available_tools
