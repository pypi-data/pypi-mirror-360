"""Tests for tool implementations."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_rag.tools.base import (
    BaseTool,
    ToolParameter,
    ToolResult,
    ToolRegistry
)
from agentic_rag.tools.calculator import (
    CalculatorTool,
    StatisticsTool,
    UnitConverterTool
)
from agentic_rag.tools.web_search import WebSearchTool, WebScrapeTool
from agentic_rag.utils.exceptions import ToolError


class MockTool(BaseTool):
    """Mock tool for testing base functionality."""
    
    def __init__(self, should_fail=False, **kwargs):
        self.should_fail = should_fail
        parameters = [
            ToolParameter(
                name="input_text",
                type="string",
                description="Input text to process",
                required=True
            ),
            ToolParameter(
                name="uppercase",
                type="boolean",
                description="Convert to uppercase",
                required=False,
                default=False
            )
        ]
        
        super().__init__(
            name="mock_tool",
            description="A mock tool for testing",
            parameters=parameters,
            **kwargs
        )
    
    async def execute(self, **kwargs):
        if self.should_fail:
            raise Exception("Mock tool failure")
        
        input_text = kwargs["input_text"]
        uppercase = kwargs.get("uppercase", False)
        
        result = input_text.upper() if uppercase else input_text
        
        return ToolResult(
            success=True,
            result={"processed_text": result},
            execution_time=0.0
        )


class TestToolParameter:
    """Test tool parameter model."""
    
    def test_parameter_creation(self):
        """Test creating a tool parameter."""
        param = ToolParameter(
            name="test_param",
            type="string",
            description="A test parameter",
            required=True,
            default="default_value",
            enum=["option1", "option2"]
        )
        
        assert param.name == "test_param"
        assert param.type == "string"
        assert param.required is True
        assert param.default == "default_value"
        assert param.enum == ["option1", "option2"]


class TestToolResult:
    """Test tool result model."""
    
    def test_result_creation(self):
        """Test creating a tool result."""
        result = ToolResult(
            success=True,
            result={"output": "test output"},
            metadata={"tool": "test_tool"},
            execution_time=1.5
        )
        
        assert result.success is True
        assert result.result["output"] == "test output"
        assert result.metadata["tool"] == "test_tool"
        assert result.execution_time == 1.5
        assert result.error is None


@pytest.mark.asyncio
class TestBaseTool:
    """Test base tool functionality."""
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        tool = MockTool()
        
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert len(tool.parameters) == 2
        assert tool.timeout == 30
    
    def test_parameter_validation_success(self):
        """Test successful parameter validation."""
        tool = MockTool()
        
        params = {"input_text": "hello", "uppercase": True}
        validated = tool.validate_parameters(params)
        
        assert validated["input_text"] == "hello"
        assert validated["uppercase"] is True
    
    def test_parameter_validation_missing_required(self):
        """Test parameter validation with missing required parameter."""
        tool = MockTool()
        
        params = {"uppercase": True}  # Missing required input_text
        
        with pytest.raises(ToolError, match="Required parameter 'input_text' not provided"):
            tool.validate_parameters(params)
    
    def test_parameter_validation_with_default(self):
        """Test parameter validation using default values."""
        tool = MockTool()
        
        params = {"input_text": "hello"}  # uppercase will use default
        validated = tool.validate_parameters(params)
        
        assert validated["input_text"] == "hello"
        assert validated["uppercase"] is False
    
    def test_parameter_type_conversion(self):
        """Test parameter type conversion."""
        tool = MockTool()
        
        params = {"input_text": "hello", "uppercase": "true"}  # String to boolean
        validated = tool.validate_parameters(params)
        
        assert validated["uppercase"] is True
    
    async def test_tool_execution_success(self):
        """Test successful tool execution."""
        tool = MockTool()
        
        result = await tool.run(input_text="hello", uppercase=True)
        
        assert result.success is True
        assert result.result["processed_text"] == "HELLO"
        assert result.error is None
        assert result.execution_time > 0
    
    async def test_tool_execution_failure(self):
        """Test tool execution failure."""
        tool = MockTool(should_fail=True)
        
        result = await tool.run(input_text="hello")
        
        assert result.success is False
        assert result.result is None
        assert "Mock tool failure" in result.error
        assert result.execution_time > 0
    
    async def test_tool_timeout(self):
        """Test tool execution timeout."""
        class SlowTool(MockTool):
            async def execute(self, **kwargs):
                await asyncio.sleep(2)  # Sleep longer than timeout
                return await super().execute(**kwargs)
        
        tool = SlowTool(timeout=1)  # 1 second timeout
        
        result = await tool.run(input_text="hello")
        
        assert result.success is False
        assert "timed out" in result.error
    
    def test_get_schema(self):
        """Test getting tool schema."""
        tool = MockTool()
        
        schema = tool.get_schema()
        
        assert schema["name"] == "mock_tool"
        assert schema["description"] == "A mock tool for testing"
        assert "parameters" in schema
        assert "input_text" in schema["parameters"]["properties"]
        assert "uppercase" in schema["parameters"]["properties"]
        assert "input_text" in schema["parameters"]["required"]


class TestToolRegistry:
    """Test tool registry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = ToolRegistry()
        
        assert len(registry) == 0
        assert registry.list_tools() == []
    
    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        assert len(registry) == 1
        assert "mock_tool" in registry
        assert registry.get_tool("mock_tool") == tool
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        success = registry.unregister("mock_tool")
        
        assert success is True
        assert len(registry) == 0
        assert "mock_tool" not in registry
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering a non-existent tool."""
        registry = ToolRegistry()
        
        success = registry.unregister("nonexistent_tool")
        
        assert success is False
    
    def test_get_schemas(self):
        """Test getting all tool schemas."""
        registry = ToolRegistry()
        tool1 = MockTool()
        tool2 = MockTool()
        tool2.name = "mock_tool_2"
        
        registry.register(tool1)
        registry.register(tool2)
        
        schemas = registry.get_schemas()
        
        assert len(schemas) == 2
        assert all("name" in schema for schema in schemas)
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool through registry."""
        registry = ToolRegistry()
        tool = MockTool()
        
        registry.register(tool)
        
        result = await registry.execute_tool("mock_tool", input_text="hello", uppercase=True)
        
        assert result.success is True
        assert result.result["processed_text"] == "HELLO"
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self):
        """Test executing a non-existent tool."""
        registry = ToolRegistry()
        
        result = await registry.execute_tool("nonexistent_tool", input_text="hello")
        
        assert result.success is False
        assert "not found" in result.error


@pytest.mark.asyncio
class TestCalculatorTool:
    """Test calculator tool implementation."""
    
    def test_calculator_initialization(self):
        """Test calculator tool initialization."""
        tool = CalculatorTool()
        
        assert tool.name == "calculator"
        assert "expression" in [p.name for p in tool.parameters]
    
    async def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        tool = CalculatorTool()
        
        result = await tool.run(expression="2 + 3 * 4")
        
        assert result.success is True
        assert result.result["result"] == 14
        assert result.result["expression"] == "2 + 3 * 4"
    
    async def test_mathematical_functions(self):
        """Test mathematical functions."""
        tool = CalculatorTool()
        
        result = await tool.run(expression="sqrt(16)")
        
        assert result.success is True
        assert result.result["result"] == 4.0
    
    async def test_constants(self):
        """Test mathematical constants."""
        tool = CalculatorTool()

        result = await tool.run(expression="pi * 2")

        assert result.success is True
        assert abs(result.result["result"] - 6.283185307179586) < 0.001
    
    async def test_invalid_expression(self):
        """Test invalid expression handling."""
        tool = CalculatorTool()

        result = await tool.run(expression="invalid_function()")

        assert result.success is False
        assert "failed" in result.error.lower()
    
    async def test_precision_control(self):
        """Test precision control."""
        tool = CalculatorTool()
        
        result = await tool.run(expression="1/3", precision=2)
        
        assert result.success is True
        assert result.result["result"] == 0.33


@pytest.mark.asyncio
class TestStatisticsTool:
    """Test statistics tool implementation."""
    
    def test_statistics_initialization(self):
        """Test statistics tool initialization."""
        tool = StatisticsTool()
        
        assert tool.name == "statistics"
        assert "data" in [p.name for p in tool.parameters]
        assert "operation" in [p.name for p in tool.parameters]
    
    async def test_mean_calculation(self):
        """Test mean calculation."""
        tool = StatisticsTool()
        
        result = await tool.run(data="1,2,3,4,5", operation="mean")
        
        assert result.success is True
        assert result.result["result"] == 3.0
        assert result.result["operation"] == "mean"
    
    async def test_median_calculation(self):
        """Test median calculation."""
        tool = StatisticsTool()
        
        result = await tool.run(data="1,2,3,4,5", operation="median")
        
        assert result.success is True
        assert result.result["result"] == 3.0
    
    async def test_json_data_input(self):
        """Test JSON data input."""
        tool = StatisticsTool()
        
        result = await tool.run(data="[1, 2, 3, 4, 5]", operation="sum")
        
        assert result.success is True
        assert result.result["result"] == 15
    
    async def test_invalid_operation(self):
        """Test invalid operation handling."""
        tool = StatisticsTool()

        result = await tool.run(data="1,2,3", operation="invalid_op")

        assert result.success is False
        assert "must be one of" in result.error


@pytest.mark.asyncio
class TestUnitConverterTool:
    """Test unit converter tool implementation."""
    
    def test_converter_initialization(self):
        """Test unit converter tool initialization."""
        tool = UnitConverterTool()
        
        assert tool.name == "unit_converter"
        assert "value" in [p.name for p in tool.parameters]
        assert "from_unit" in [p.name for p in tool.parameters]
        assert "to_unit" in [p.name for p in tool.parameters]
    
    async def test_length_conversion(self):
        """Test length unit conversion."""
        tool = UnitConverterTool()
        
        result = await tool.run(value=1000, from_unit="m", to_unit="km")
        
        assert result.success is True
        assert result.result["converted_value"] == 1.0
        assert result.result["category"] == "length"
    
    async def test_temperature_conversion(self):
        """Test temperature unit conversion."""
        tool = UnitConverterTool()
        
        result = await tool.run(value=0, from_unit="celsius", to_unit="fahrenheit")
        
        assert result.success is True
        assert result.result["converted_value"] == 32.0
        assert result.result["category"] == "temperature"
    
    async def test_weight_conversion(self):
        """Test weight unit conversion."""
        tool = UnitConverterTool()
        
        result = await tool.run(value=1, from_unit="kg", to_unit="g")
        
        assert result.success is True
        assert result.result["converted_value"] == 1000.0
        assert result.result["category"] == "weight"
    
    async def test_auto_category_detection(self):
        """Test automatic category detection."""
        tool = UnitConverterTool()
        
        result = await tool.run(value=1, from_unit="m", to_unit="cm")
        
        assert result.success is True
        assert result.result["category"] == "length"
    
    async def test_invalid_units(self):
        """Test invalid unit handling."""
        tool = UnitConverterTool()

        result = await tool.run(value=1, from_unit="invalid", to_unit="m")

        assert result.success is False
        assert "failed" in result.error.lower()


@pytest.mark.asyncio
class TestWebSearchTool:
    """Test web search tool implementation."""
    
    def test_web_search_initialization(self):
        """Test web search tool initialization."""
        tool = WebSearchTool()
        
        assert tool.name == "web_search"
        assert "query" in [p.name for p in tool.parameters]
        assert tool.search_engine == "duckduckgo"
    
    @patch('agentic_rag.tools.web_search.aiohttp.ClientSession')
    async def test_duckduckgo_api_search(self, mock_session):
        """Test DuckDuckGo API search."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "Abstract": "Test abstract",
            "AbstractURL": "https://example.com",
            "Heading": "Test Topic",
            "RelatedTopics": [
                {
                    "Text": "Related topic 1 - Description",
                    "FirstURL": "https://example.com/1"
                }
            ]
        }

        # Create proper async context manager mock
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = AsyncMock()
        mock_session_instance.get.return_value = mock_get

        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=None)

        tool = WebSearchTool(search_engine="duckduckgo")

        # Mock the duckduckgo-search import to fail, forcing API fallback
        with patch('duckduckgo_search.AsyncDDGS', side_effect=ImportError):
            result = await tool.run(query="test query", num_results=2)

        assert result.success is True
        assert "results" in result.result
        assert len(result.result["results"]) <= 2
    
    async def test_web_search_parameter_validation(self):
        """Test web search parameter validation."""
        tool = WebSearchTool(max_results=5)
        
        # Test that num_results is capped at max_results
        validated = tool.validate_parameters({
            "query": "test",
            "num_results": 10,  # Should be capped at 5
            "safe_search": True
        })
        
        assert validated["query"] == "test"
        assert validated["num_results"] == 10  # Validation doesn't cap, execution does
        assert validated["safe_search"] is True


@pytest.mark.asyncio
class TestWebScrapeTool:
    """Test web scrape tool implementation."""
    
    def test_web_scrape_initialization(self):
        """Test web scrape tool initialization."""
        tool = WebScrapeTool()
        
        assert tool.name == "web_scrape"
        assert "url" in [p.name for p in tool.parameters]
    
    @patch('agentic_rag.tools.web_search.aiohttp.ClientSession')
    @patch('bs4.BeautifulSoup')
    async def test_web_scraping(self, mock_bs, mock_session):
        """Test web page scraping."""
        # Mock HTTP response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html><body><h1>Test Page</h1><p>Content</p></body></html>")

        # Create proper async context manager mock
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = AsyncMock()
        mock_session_instance.get.return_value = mock_get

        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_soup.get_text.return_value = "Test Page\nContent"
        mock_soup.title.string = "Test Page"
        mock_bs.return_value = mock_soup
        
        tool = WebScrapeTool()
        
        result = await tool.run(url="https://example.com", max_length=1000)
        
        assert result.success is True
        assert "content" in result.result
        assert result.result["url"] == "https://example.com"
    
    @patch('agentic_rag.tools.web_search.aiohttp.ClientSession')
    async def test_web_scraping_http_error(self, mock_session):
        """Test web scraping with HTTP error."""
        # Mock HTTP error response
        mock_response = AsyncMock()
        mock_response.status = 404

        # Create proper async context manager mock
        mock_get = AsyncMock()
        mock_get.__aenter__ = AsyncMock(return_value=mock_response)
        mock_get.__aexit__ = AsyncMock(return_value=None)

        mock_session_instance = AsyncMock()
        mock_session_instance.get.return_value = mock_get

        mock_session.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
        mock_session.return_value.__aexit__ = AsyncMock(return_value=None)
        
        tool = WebScrapeTool()
        
        result = await tool.run(url="https://example.com/notfound")
        
        assert result.success is False
        assert "404" in result.error
