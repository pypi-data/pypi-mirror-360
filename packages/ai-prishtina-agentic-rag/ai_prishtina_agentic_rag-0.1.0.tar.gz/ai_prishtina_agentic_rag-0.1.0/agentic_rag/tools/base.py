"""Base tool implementation for the Agentic RAG library."""

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..utils.exceptions import ToolError
from ..utils.logging import LoggerMixin


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    
    name: str = Field(description="Parameter name")
    type: str = Field(description="Parameter type")
    description: str = Field(description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[str]] = Field(default=None, description="Allowed values")


class ToolResult(BaseModel):
    """Result from tool execution."""
    
    success: bool = Field(description="Whether tool execution was successful")
    result: Any = Field(description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: float = Field(description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)


class BaseTool(ABC, LoggerMixin):
    """Abstract base class for tools."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[ToolParameter],
        timeout: int = 30,
        **kwargs
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.timeout = timeout
        self.kwargs = kwargs
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and process input parameters."""
        validated = {}
        
        for param in self.parameters:
            value = parameters.get(param.name)
            
            # Check required parameters
            if param.required and value is None:
                if param.default is not None:
                    value = param.default
                else:
                    raise ToolError(
                        f"Required parameter '{param.name}' not provided",
                        tool_name=self.name,
                        tool_input=parameters
                    )
            elif value is None and param.default is not None:
                value = param.default
            
            # Type validation (basic)
            if value is not None:
                if param.type == "string" and not isinstance(value, str):
                    value = str(value)
                elif param.type == "integer" and not isinstance(value, int):
                    try:
                        value = int(value)
                    except ValueError:
                        raise ToolError(
                            f"Parameter '{param.name}' must be an integer",
                            tool_name=self.name,
                            tool_input=parameters
                        )
                elif param.type == "float" and not isinstance(value, (int, float)):
                    try:
                        value = float(value)
                    except ValueError:
                        raise ToolError(
                            f"Parameter '{param.name}' must be a number",
                            tool_name=self.name,
                            tool_input=parameters
                        )
                elif param.type == "boolean" and not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "yes", "on")
                    else:
                        value = bool(value)
                
                # Enum validation
                if param.enum and value not in param.enum:
                    raise ToolError(
                        f"Parameter '{param.name}' must be one of {param.enum}",
                        tool_name=self.name,
                        tool_input=parameters
                    )
            
            validated[param.name] = value
        
        return validated
    
    async def run(self, **kwargs) -> ToolResult:
        """Run the tool with parameter validation and error handling."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate parameters
            validated_params = self.validate_parameters(kwargs)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(**validated_params),
                timeout=self.timeout
            )
            
            execution_time = asyncio.get_event_loop().time() - start_time
            result.execution_time = execution_time
            
            self.logger.info(f"Tool '{self.name}' executed successfully in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Tool '{self.name}' timed out after {self.timeout}s"
            self.logger.error(error_msg)
            
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
            
        except ToolError as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Tool '{self.name}' failed: {e}")
            
            return ToolResult(
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Unexpected error in tool '{self.name}': {e}"
            self.logger.error(error_msg)
            
            return ToolResult(
                success=False,
                result=None,
                error=error_msg,
                execution_time=execution_time
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for LLM function calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type,
                        "description": param.description,
                        **({"enum": param.enum} if param.enum else {}),
                        **({"default": param.default} if param.default is not None else {})
                    }
                    for param in self.parameters
                },
                "required": [param.name for param in self.parameters if param.required]
            }
        }
    
    def __str__(self) -> str:
        return f"Tool(name='{self.name}', description='{self.description}')"
    
    def __repr__(self) -> str:
        return self.__str__()


class ToolRegistry(LoggerMixin):
    """Registry for managing tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def unregister(self, tool_name: str) -> bool:
        """Unregister a tool."""
        if tool_name in self._tools:
            del self._tools[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
            return True
        return False
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not found",
                execution_time=0.0
            )
        
        return await tool.run(**kwargs)
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools
    
    def __iter__(self):
        return iter(self._tools.values())
