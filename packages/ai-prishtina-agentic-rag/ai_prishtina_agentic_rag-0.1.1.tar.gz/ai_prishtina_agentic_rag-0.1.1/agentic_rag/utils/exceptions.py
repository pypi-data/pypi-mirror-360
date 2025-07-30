"""Custom exceptions for the Agentic RAG library."""

from typing import Any, Dict, Optional


class AgenticRAGError(Exception):
    """Base exception class for all Agentic RAG errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DocumentProcessingError(AgenticRAGError):
    """Exception raised during document processing operations."""
    
    def __init__(
        self,
        message: str,
        document_path: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.document_path = document_path
        self.processing_stage = processing_stage


class RetrievalError(AgenticRAGError):
    """Exception raised during retrieval operations."""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        retrieval_method: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.query = query
        self.retrieval_method = retrieval_method


class LLMError(AgenticRAGError):
    """Exception raised during LLM operations."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.model = model
        self.prompt = prompt


class ToolError(AgenticRAGError):
    """Exception raised during tool execution."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        tool_input: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        self.tool_input = tool_input


class ConfigurationError(AgenticRAGError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_value = config_value


class ValidationError(AgenticRAGError):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.field_name = field_name
        self.field_value = field_value


class VectorStoreError(RetrievalError):
    """Exception raised for vector store operations."""
    
    def __init__(
        self,
        message: str,
        vector_store_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.vector_store_type = vector_store_type
        self.operation = operation


class MemoryError(AgenticRAGError):
    """Exception raised for memory-related operations."""
    
    def __init__(
        self,
        message: str,
        memory_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.memory_type = memory_type
        self.operation = operation


class PlanningError(AgenticRAGError):
    """Exception raised during query planning operations."""
    
    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        planning_stage: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.query = query
        self.planning_stage = planning_stage
