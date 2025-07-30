"""
Agentic RAG - A comprehensive, professional-grade agentic Retrieval-Augmented Generation library.

This library provides a complete solution for building intelligent RAG systems with agentic capabilities,
including query planning, multi-step reasoning, tool integration, and advanced retrieval mechanisms.
"""

from .core.agent import AgenticRAG
from .core.memory import Memory, WorkingMemory, LongTermMemory
from .core.planner import QueryPlanner, Plan, PlanStep
from .core.orchestrator import RAGOrchestrator

from .document_processing.loaders import DocumentLoader
from .document_processing.chunkers import (
    BaseChunker,
    FixedSizeChunker,
    SemanticChunker,
    RecursiveChunker,
)
from .document_processing.preprocessors import TextPreprocessor
from .document_processing.metadata_extractors import MetadataExtractor

# Multi-modal processing (optional)
try:
    from .document_processing.multimodal_loaders import ImageLoader, AudioLoader, VideoLoader
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False

# Graph RAG (optional)
try:
    from .graph import KnowledgeGraph, GraphNode, GraphEdge, EntityExtractor
    GRAPH_RAG_AVAILABLE = True
except ImportError:
    GRAPH_RAG_AVAILABLE = False

from .retrieval import (
    BaseVectorStore,
    ChromaVectorStore,
    PineconeVectorStore,
    WeaviateVectorStore,
    FAISSVectorStore,
    BaseRetriever,
    VectorRetriever,
    HybridRetriever,
    GraphRetriever,
    BaseReranker,
    CrossEncoderReranker,
    ColBERTReranker,
)

from .llm import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    CohereProvider,
    LocalModelProvider,
    PromptTemplate,
    PromptManager,
    ResponseGenerator,
)

from .tools import (
    BaseTool,
    ToolResult,
    WebSearchTool,
    CalculatorTool,
    CodeExecutorTool,
)

from .evaluation.metrics import (
    RelevanceMetric,
    FaithfulnessMetric,
    AnswerQualityMetric,
    LatencyMetric,
    ComprehensiveEvaluator,
    EvaluationResult,
)

from .evaluation.benchmarks import RAGBenchmark, PerformanceBenchmark

from .utils.config import Config
from .utils.exceptions import (
    AgenticRAGError,
    DocumentProcessingError,
    RetrievalError,
    LLMError,
    ToolError,
)

__version__ = "0.1.0"
__author__ = "AI Prishtina"
__email__ = "contact@ai-prishtina.com"

__all__ = [
    # Core components
    "AgenticRAG",
    "Memory",
    "WorkingMemory",
    "LongTermMemory",
    "QueryPlanner",
    "Plan",
    "PlanStep",
    "RAGOrchestrator",
    
    # Document processing
    "DocumentLoader",
    "BaseChunker",
    "FixedSizeChunker",
    "SemanticChunker",
    "RecursiveChunker",
    "TextPreprocessor",
    "MetadataExtractor",
    
    # Retrieval
    "BaseVectorStore",
    "ChromaVectorStore",
    "PineconeVectorStore",
    "WeaviateVectorStore",
    "FAISSVectorStore",
    "BaseRetriever",
    "VectorRetriever",
    "HybridRetriever",
    "GraphRetriever",
    "BaseReranker",
    "CrossEncoderReranker",
    "ColBERTReranker",
    
    # LLM
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "CohereProvider",
    "LocalModelProvider",
    "PromptTemplate",
    "PromptManager",
    "ResponseGenerator",
    
    # Tools
    "BaseTool",
    "ToolResult",
    "WebSearchTool",
    "CalculatorTool",
    "CodeExecutorTool",
    
    # Evaluation
    "RelevanceMetric",
    "FaithfulnessMetric",
    "AnswerQualityMetric",
    "LatencyMetric",
    "ComprehensiveEvaluator",
    "EvaluationResult",
    "RAGBenchmark",
    "PerformanceBenchmark",
    
    # Utils
    "Config",
    "AgenticRAGError",
    "DocumentProcessingError",
    "RetrievalError",
    "LLMError",
    "ToolError",
]
