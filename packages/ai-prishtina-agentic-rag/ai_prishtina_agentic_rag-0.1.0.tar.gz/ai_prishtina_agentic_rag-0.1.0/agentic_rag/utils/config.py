"""Configuration management for the Agentic RAG library."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from .exceptions import ConfigurationError


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    
    provider: str = Field(default="openai", description="LLM provider name")
    model: str = Field(default="gpt-3.5-turbo", description="Model name")
    api_key: Optional[str] = Field(default=None, description="API key")
    base_url: Optional[str] = Field(default=None, description="Base URL for API")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature")
    max_tokens: int = Field(default=1000, gt=0, description="Maximum tokens")
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")


class VectorStoreConfig(BaseModel):
    """Configuration for vector stores."""
    
    provider: str = Field(default="chroma", description="Vector store provider")
    collection_name: str = Field(default="agentic_rag", description="Collection name")
    persist_directory: Optional[str] = Field(default=None, description="Persistence directory")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", description="Embedding model")
    dimension: int = Field(default=384, gt=0, description="Vector dimension")
    
    # Provider-specific configs
    chroma_config: Dict[str, Any] = Field(default_factory=dict)
    pinecone_config: Dict[str, Any] = Field(default_factory=dict)
    weaviate_config: Dict[str, Any] = Field(default_factory=dict)
    faiss_config: Dict[str, Any] = Field(default_factory=dict)


class DocumentProcessingConfig(BaseModel):
    """Configuration for document processing."""
    
    chunk_size: int = Field(default=1000, gt=0, description="Default chunk size")
    chunk_overlap: int = Field(default=200, ge=0, description="Chunk overlap")
    chunking_strategy: str = Field(default="recursive", description="Chunking strategy")
    
    # File type specific settings
    pdf_extract_images: bool = Field(default=False, description="Extract images from PDFs")
    html_parser: str = Field(default="html.parser", description="HTML parser")
    markdown_extensions: list = Field(default_factory=list, description="Markdown extensions")
    
    # Text preprocessing
    enable_preprocessing: bool = Field(default=True, description="Enable text preprocessing")
    remove_extra_whitespace: bool = Field(default=True, description="Remove extra whitespace")
    normalize_unicode: bool = Field(default=True, description="Normalize Unicode")
    remove_urls: bool = Field(default=False, description="Remove URLs")
    remove_emails: bool = Field(default=False, description="Remove email addresses")


class RetrievalConfig(BaseModel):
    """Configuration for retrieval operations."""
    
    top_k: int = Field(default=5, gt=0, description="Number of documents to retrieve")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    enable_reranking: bool = Field(default=True, description="Enable reranking")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", description="Reranker model")
    
    # Hybrid search settings
    enable_hybrid_search: bool = Field(default=False, description="Enable hybrid search")
    dense_weight: float = Field(default=0.7, ge=0.0, le=1.0, description="Dense retrieval weight")
    sparse_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Sparse retrieval weight")
    
    @field_validator('sparse_weight')
    @classmethod
    def validate_weights(cls, v, info):
        # Only validate when both weights are available
        if 'dense_weight' in info.data:
            dense_weight = info.data['dense_weight']
            if abs(dense_weight + v - 1.0) > 1e-6:
                raise ValueError("Dense and sparse weights must sum to 1.0")
        return v


class AgentConfig(BaseModel):
    """Configuration for agentic capabilities."""
    
    enable_planning: bool = Field(default=True, description="Enable query planning")
    max_planning_steps: int = Field(default=5, gt=0, description="Maximum planning steps")
    enable_memory: bool = Field(default=True, description="Enable memory")
    memory_size: int = Field(default=1000, gt=0, description="Memory size")
    
    # Tool configuration
    enable_tools: bool = Field(default=True, description="Enable tool usage")
    available_tools: list = Field(default_factory=lambda: ["web_search", "calculator"], description="Available tools")
    tool_timeout: int = Field(default=30, gt=0, description="Tool execution timeout")


class EvaluationConfig(BaseModel):
    """Configuration for evaluation and monitoring."""
    
    enable_evaluation: bool = Field(default=False, description="Enable evaluation")
    metrics: list = Field(default_factory=lambda: ["relevance", "faithfulness"], description="Evaluation metrics")
    benchmark_dataset: Optional[str] = Field(default=None, description="Benchmark dataset")
    
    # Monitoring
    enable_monitoring: bool = Field(default=False, description="Enable monitoring")
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")


class Config(BaseModel):
    """Main configuration class for Agentic RAG."""
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    document_processing: DocumentProcessingConfig = Field(default_factory=DocumentProcessingConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "Config":
        """Load configuration from a YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()
        
        config_data = {}
        
        # LLM configuration
        if os.getenv("LLM_PROVIDER"):
            config_data.setdefault("llm", {})["provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_MODEL"):
            config_data.setdefault("llm", {})["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_API_KEY"):
            config_data.setdefault("llm", {})["api_key"] = os.getenv("LLM_API_KEY")
        
        # Vector store configuration
        if os.getenv("VECTOR_STORE_PROVIDER"):
            config_data.setdefault("vector_store", {})["provider"] = os.getenv("VECTOR_STORE_PROVIDER")
        if os.getenv("VECTOR_STORE_COLLECTION"):
            config_data.setdefault("vector_store", {})["collection_name"] = os.getenv("VECTOR_STORE_COLLECTION")
        
        return cls(**config_data)
    
    def to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a YAML file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(self.model_dump(), f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {e}")
    
    def update(self, **kwargs) -> "Config":
        """Update configuration with new values."""
        config_dict = self.model_dump()
        
        for key, value in kwargs.items():
            if '.' in key:
                # Handle nested keys like 'llm.temperature'
                keys = key.split('.')
                current = config_dict
                for k in keys[:-1]:
                    current = current.setdefault(k, {})
                current[keys[-1]] = value
            else:
                config_dict[key] = value
        
        return Config(**config_dict)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create config from dictionary."""
        # Handle nested dictionaries for sub-configs
        processed_dict = {}

        for key, value in config_dict.items():
            if key == "llm" and isinstance(value, dict):
                processed_dict[key] = LLMConfig(**value)
            elif key == "vector_store" and isinstance(value, dict):
                processed_dict[key] = VectorStoreConfig(**value)
            elif key == "retrieval" and isinstance(value, dict):
                processed_dict[key] = RetrievalConfig(**value)
            elif key == "document_processing" and isinstance(value, dict):
                processed_dict[key] = DocumentProcessingConfig(**value)
            elif key == "agent" and isinstance(value, dict):
                processed_dict[key] = AgentConfig(**value)
            elif key == "evaluation" and isinstance(value, dict):
                processed_dict[key] = EvaluationConfig(**value)
            else:
                processed_dict[key] = value

        return cls(**processed_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()

    @classmethod
    def from_env(cls, prefix: str = "AGENTIC_RAG_") -> "Config":
        """Create config from environment variables."""
        config_dict = {}

        # Helper function to set nested values
        def set_nested_value(d: Dict[str, Any], keys: List[str], value: Any) -> None:
            current = d
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value

        # Parse environment variables
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()

                # Handle specific known patterns
                if config_key.startswith('vector_store_'):
                    field_name = config_key[13:]  # Remove 'vector_store_'
                    if 'vector_store' not in config_dict:
                        config_dict['vector_store'] = {}
                    config_dict['vector_store'][field_name] = value
                elif config_key.startswith('llm_'):
                    field_name = config_key[4:]  # Remove 'llm_'
                    if 'llm' not in config_dict:
                        config_dict['llm'] = {}
                    # Convert value to appropriate type
                    if value.lower() in ('true', 'false'):
                        converted_value = value.lower() == 'true'
                    elif value.isdigit():
                        converted_value = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        converted_value = float(value)
                    else:
                        converted_value = value
                    config_dict['llm'][field_name] = converted_value
                elif config_key.startswith('agent_'):
                    field_name = config_key[6:]  # Remove 'agent_'
                    if 'agent' not in config_dict:
                        config_dict['agent'] = {}
                    # Convert value to appropriate type
                    if value.lower() in ('true', 'false'):
                        converted_value = value.lower() == 'true'
                    elif value.isdigit():
                        converted_value = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        converted_value = float(value)
                    else:
                        converted_value = value
                    config_dict['agent'][field_name] = converted_value

        return cls.from_dict(config_dict)
