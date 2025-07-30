"""Query planning for agentic RAG systems."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..utils.logging import LoggerMixin


class PlanStepType(Enum):
    """Types of plan steps."""
    RETRIEVE = "retrieve"
    SEARCH = "search"
    ANALYZE = "analyze"
    SYNTHESIZE = "synthesize"
    TOOL_USE = "tool_use"


class PlanStep(BaseModel):
    """Represents a single step in a query plan."""
    
    id: str = Field(description="Step identifier")
    type: PlanStepType = Field(description="Type of step")
    description: str = Field(description="Step description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Step parameters")
    dependencies: List[str] = Field(default_factory=list, description="Dependent step IDs")
    completed: bool = Field(default=False, description="Whether step is completed")
    result: Optional[Any] = Field(default=None, description="Step result")


class Plan(BaseModel):
    """Represents a complete query execution plan."""
    
    query: str = Field(description="Original query")
    steps: List[PlanStep] = Field(description="Plan steps")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Plan metadata")


class QueryPlanner(LoggerMixin):
    """Plans query execution for agentic RAG."""
    
    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
    
    def create_plan(self, query: str) -> Plan:
        """Create an execution plan for the query."""
        # Simple planning logic - can be enhanced with LLM-based planning
        steps = [
            PlanStep(
                id="step_1",
                type=PlanStepType.RETRIEVE,
                description="Retrieve relevant documents",
                parameters={"query": query, "top_k": 5}
            ),
            PlanStep(
                id="step_2", 
                type=PlanStepType.SYNTHESIZE,
                description="Generate response from retrieved documents",
                parameters={"query": query},
                dependencies=["step_1"]
            )
        ]
        
        return Plan(query=query, steps=steps)
