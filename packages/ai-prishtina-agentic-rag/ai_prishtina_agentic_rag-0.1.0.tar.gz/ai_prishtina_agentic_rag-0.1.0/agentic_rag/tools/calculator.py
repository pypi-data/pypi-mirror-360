"""Calculator tool implementation."""

import ast
import math
import operator
from typing import Any, Dict, Union

from .base import BaseTool, ToolParameter, ToolResult
from ..utils.exceptions import ToolError


class CalculatorTool(BaseTool):
    """Tool for mathematical calculations."""
    
    def __init__(self, **kwargs):
        parameters = [
            ToolParameter(
                name="expression",
                type="string",
                description="Mathematical expression to evaluate",
                required=True
            ),
            ToolParameter(
                name="precision",
                type="integer",
                description="Number of decimal places for the result",
                required=False,
                default=6
            )
        ]
        
        super().__init__(
            name="calculator",
            description="Evaluate mathematical expressions safely",
            parameters=parameters,
            **kwargs
        )
        
        # Safe operators and functions
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.FloorDiv: operator.floordiv,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        self.functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'atan2': math.atan2,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'exp': math.exp,
            'ceil': math.ceil,
            'floor': math.floor,
            'factorial': math.factorial,
            'degrees': math.degrees,
            'radians': math.radians,
        }
        
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
            'nan': math.nan,
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute mathematical calculation."""
        expression = kwargs["expression"]
        precision = kwargs.get("precision", 6)
        
        try:
            # Parse the expression
            tree = ast.parse(expression, mode='eval')
            
            # Evaluate the expression safely
            result = self._eval_node(tree.body)
            
            # Format result with specified precision
            if isinstance(result, float):
                if precision == 0:
                    formatted_result = int(result)
                else:
                    formatted_result = round(result, precision)
            else:
                formatted_result = result
            
            return ToolResult(
                success=True,
                result={
                    "expression": expression,
                    "result": formatted_result,
                    "type": type(result).__name__
                },
                metadata={
                    "precision": precision,
                    "raw_result": result
                },
                execution_time=0.0
            )
            
        except Exception as e:
            raise ToolError(f"Calculation failed: {e}")
    
    def _eval_node(self, node) -> Union[int, float, complex]:
        """Safely evaluate an AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # For Python < 3.8 compatibility
            return node.n
        elif isinstance(node, ast.Name):
            if node.id in self.constants:
                return self.constants[node.id]
            else:
                raise ToolError(f"Unknown variable: {node.id}")
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ToolError(f"Unsupported operator: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op = self.operators.get(type(node.op))
            if op is None:
                raise ToolError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op(operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else None
            if func_name not in self.functions:
                raise ToolError(f"Unknown function: {func_name}")
            
            args = [self._eval_node(arg) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value) for kw in node.keywords}
            
            try:
                return self.functions[func_name](*args, **kwargs)
            except Exception as e:
                raise ToolError(f"Function '{func_name}' error: {e}")
        elif isinstance(node, ast.List):
            return [self._eval_node(item) for item in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(item) for item in node.elts)
        else:
            raise ToolError(f"Unsupported expression type: {type(node).__name__}")


class StatisticsTool(BaseTool):
    """Tool for statistical calculations."""
    
    def __init__(self, **kwargs):
        parameters = [
            ToolParameter(
                name="data",
                type="string",
                description="Comma-separated list of numbers or JSON array",
                required=True
            ),
            ToolParameter(
                name="operation",
                type="string",
                description="Statistical operation to perform",
                required=True,
                enum=["mean", "median", "mode", "std", "var", "min", "max", "sum", "count", "range"]
            )
        ]
        
        super().__init__(
            name="statistics",
            description="Perform statistical calculations on datasets",
            parameters=parameters,
            **kwargs
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute statistical calculation."""
        data_str = kwargs["data"]
        operation = kwargs["operation"]
        
        try:
            # Parse data
            try:
                import json
                data = json.loads(data_str)
            except json.JSONDecodeError:
                # Try parsing as comma-separated values
                data = [float(x.strip()) for x in data_str.split(',')]
            
            if not data:
                raise ToolError("No data provided")
            
            # Perform statistical operation
            if operation == "mean":
                result = sum(data) / len(data)
            elif operation == "median":
                sorted_data = sorted(data)
                n = len(sorted_data)
                if n % 2 == 0:
                    result = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
                else:
                    result = sorted_data[n//2]
            elif operation == "mode":
                from collections import Counter
                counts = Counter(data)
                max_count = max(counts.values())
                modes = [k for k, v in counts.items() if v == max_count]
                result = modes[0] if len(modes) == 1 else modes
            elif operation == "std":
                mean = sum(data) / len(data)
                variance = sum((x - mean) ** 2 for x in data) / len(data)
                result = variance ** 0.5
            elif operation == "var":
                mean = sum(data) / len(data)
                result = sum((x - mean) ** 2 for x in data) / len(data)
            elif operation == "min":
                result = min(data)
            elif operation == "max":
                result = max(data)
            elif operation == "sum":
                result = sum(data)
            elif operation == "count":
                result = len(data)
            elif operation == "range":
                result = max(data) - min(data)
            else:
                raise ToolError(f"Unknown operation: {operation}")
            
            return ToolResult(
                success=True,
                result={
                    "operation": operation,
                    "result": result,
                    "data_points": len(data)
                },
                metadata={
                    "data_sample": data[:10] if len(data) > 10 else data
                },
                execution_time=0.0
            )
            
        except Exception as e:
            raise ToolError(f"Statistics calculation failed: {e}")


class UnitConverterTool(BaseTool):
    """Tool for unit conversions."""
    
    def __init__(self, **kwargs):
        parameters = [
            ToolParameter(
                name="value",
                type="float",
                description="Value to convert",
                required=True
            ),
            ToolParameter(
                name="from_unit",
                type="string",
                description="Source unit",
                required=True
            ),
            ToolParameter(
                name="to_unit",
                type="string",
                description="Target unit",
                required=True
            ),
            ToolParameter(
                name="category",
                type="string",
                description="Unit category",
                required=False,
                enum=["length", "weight", "temperature", "volume", "area", "time"]
            )
        ]
        
        super().__init__(
            name="unit_converter",
            description="Convert between different units of measurement",
            parameters=parameters,
            **kwargs
        )
        
        # Conversion factors to base units
        self.conversions = {
            "length": {
                "base": "meter",
                "factors": {
                    "mm": 0.001,
                    "cm": 0.01,
                    "m": 1.0,
                    "km": 1000.0,
                    "inch": 0.0254,
                    "ft": 0.3048,
                    "yard": 0.9144,
                    "mile": 1609.344
                }
            },
            "weight": {
                "base": "kilogram",
                "factors": {
                    "mg": 0.000001,
                    "g": 0.001,
                    "kg": 1.0,
                    "oz": 0.0283495,
                    "lb": 0.453592,
                    "ton": 1000.0
                }
            },
            "temperature": {
                "base": "celsius",
                "special": True  # Special handling required
            },
            "volume": {
                "base": "liter",
                "factors": {
                    "ml": 0.001,
                    "l": 1.0,
                    "gal": 3.78541,
                    "qt": 0.946353,
                    "pt": 0.473176,
                    "cup": 0.236588,
                    "fl_oz": 0.0295735
                }
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute unit conversion."""
        value = kwargs["value"]
        from_unit = kwargs["from_unit"].lower()
        to_unit = kwargs["to_unit"].lower()
        category = kwargs.get("category")
        
        try:
            # Auto-detect category if not provided
            if not category:
                category = self._detect_category(from_unit, to_unit)
            
            if category not in self.conversions:
                raise ToolError(f"Unsupported category: {category}")
            
            # Handle temperature conversions specially
            if category == "temperature":
                result = self._convert_temperature(value, from_unit, to_unit)
            else:
                result = self._convert_standard(value, from_unit, to_unit, category)
            
            return ToolResult(
                success=True,
                result={
                    "original_value": value,
                    "original_unit": from_unit,
                    "converted_value": result,
                    "converted_unit": to_unit,
                    "category": category
                },
                metadata={
                    "conversion_factor": result / value if value != 0 else None
                },
                execution_time=0.0
            )
            
        except Exception as e:
            raise ToolError(f"Unit conversion failed: {e}")
    
    def _detect_category(self, from_unit: str, to_unit: str) -> str:
        """Auto-detect unit category."""
        for category, data in self.conversions.items():
            if category == "temperature":
                temp_units = ["celsius", "fahrenheit", "kelvin", "c", "f", "k"]
                if from_unit in temp_units and to_unit in temp_units:
                    return category
            else:
                factors = data.get("factors", {})
                if from_unit in factors and to_unit in factors:
                    return category
        
        raise ToolError(f"Could not determine category for units: {from_unit}, {to_unit}")
    
    def _convert_standard(self, value: float, from_unit: str, to_unit: str, category: str) -> float:
        """Convert using standard factor-based conversion."""
        factors = self.conversions[category]["factors"]
        
        if from_unit not in factors:
            raise ToolError(f"Unknown unit in {category}: {from_unit}")
        if to_unit not in factors:
            raise ToolError(f"Unknown unit in {category}: {to_unit}")
        
        # Convert to base unit, then to target unit
        base_value = value * factors[from_unit]
        result = base_value / factors[to_unit]
        
        return result
    
    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature units."""
        # Normalize unit names
        unit_map = {"c": "celsius", "f": "fahrenheit", "k": "kelvin"}
        from_unit = unit_map.get(from_unit, from_unit)
        to_unit = unit_map.get(to_unit, to_unit)
        
        # Convert to Celsius first
        if from_unit == "celsius":
            celsius = value
        elif from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        else:
            raise ToolError(f"Unknown temperature unit: {from_unit}")
        
        # Convert from Celsius to target
        if to_unit == "celsius":
            result = celsius
        elif to_unit == "fahrenheit":
            result = celsius * 9/5 + 32
        elif to_unit == "kelvin":
            result = celsius + 273.15
        else:
            raise ToolError(f"Unknown temperature unit: {to_unit}")
        
        return result
