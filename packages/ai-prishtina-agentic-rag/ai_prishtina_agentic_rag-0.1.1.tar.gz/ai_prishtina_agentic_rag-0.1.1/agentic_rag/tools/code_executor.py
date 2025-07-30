"""
Code execution tool for the Agentic RAG library.
Provides safe code execution capabilities with sandboxing.
"""

import ast
import sys
import io
import time
import traceback
from typing import Dict, Any, List, Optional
from contextlib import redirect_stdout, redirect_stderr

from .base import BaseTool, ToolResult, ToolParameter
from ..utils.exceptions import ToolError


class CodeExecutorTool(BaseTool):
    """Tool for executing Python code safely."""
    
    def __init__(self, timeout: int = 10, max_output_length: int = 10000, **kwargs):
        """
        Initialize the code executor tool.
        
        Args:
            timeout: Maximum execution time in seconds
            max_output_length: Maximum output length to capture
            **kwargs: Additional tool parameters
        """
        self.timeout = timeout
        self.max_output_length = max_output_length
        
        parameters = [
            ToolParameter(
                name="code",
                type="string",
                description="Python code to execute",
                required=True
            ),
            ToolParameter(
                name="language",
                type="string",
                description="Programming language (currently only 'python' supported)",
                required=False,
                default="python",
                enum=["python"]
            ),
            ToolParameter(
                name="timeout",
                type="integer",
                description="Execution timeout in seconds",
                required=False,
                default=timeout
            )
        ]
        
        super().__init__(
            name="code_executor",
            description="Execute Python code safely in a sandboxed environment",
            parameters=parameters,
            **kwargs
        )
    
    def _is_safe_code(self, code: str) -> tuple[bool, str]:
        """
        Check if code is safe to execute.
        
        Args:
            code: Python code to check
            
        Returns:
            Tuple of (is_safe, reason)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # List of dangerous operations
        dangerous_nodes = [
            ast.Import,
            ast.ImportFrom,
        ]

        # Add deprecated AST nodes for Python < 3.8 compatibility
        if hasattr(ast, 'Exec'):
            dangerous_nodes.append(ast.Exec)
        if hasattr(ast, 'Eval'):
            dangerous_nodes.append(ast.Eval)
        
        dangerous_names = {
            'open', 'file', 'input', 'raw_input', 'execfile', 'reload',
            '__import__', 'eval', 'exec', 'compile', 'globals', 'locals',
            'vars', 'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
            'exit', 'quit', 'help', 'license', 'credits', 'copyright'
        }
        
        for node in ast.walk(tree):
            # Check for dangerous node types
            if any(isinstance(node, dangerous_type) for dangerous_type in dangerous_nodes):
                return False, f"Dangerous operation detected: {type(node).__name__}"
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in dangerous_names:
                    return False, f"Dangerous function call: {node.func.id}"
            
            # Check for attribute access to dangerous modules
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id in ['os', 'sys', 'subprocess']:
                    return False, f"Access to dangerous module: {node.value.id}"
        
        return True, "Code appears safe"
    
    def _execute_python_code(self, code: str, timeout: int) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout
            
        Returns:
            Execution result dictionary
        """
        # Check if code is safe
        is_safe, reason = self._is_safe_code(code)
        if not is_safe:
            raise ToolError(f"Unsafe code detected: {reason}")
        
        # Prepare execution environment
        safe_globals = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
                'chr': chr, 'dict': dict, 'enumerate': enumerate, 'filter': filter,
                'float': float, 'format': format, 'frozenset': frozenset,
                'hex': hex, 'int': int, 'len': len, 'list': list, 'map': map,
                'max': max, 'min': min, 'oct': oct, 'ord': ord, 'pow': pow,
                'print': print, 'range': range, 'reversed': reversed, 'round': round,
                'set': set, 'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple,
                'type': type, 'zip': zip,
            },
            # Safe math operations
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'json': __import__('json'),
            're': __import__('re'),
        }
        
        safe_locals = {}
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        start_time = time.time()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Execute the code
                exec(code, safe_globals, safe_locals)
            
            execution_time = time.time() - start_time
            
            # Get output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            # Truncate output if too long
            if len(stdout_output) > self.max_output_length:
                stdout_output = stdout_output[:self.max_output_length] + "\n... (output truncated)"
            
            if len(stderr_output) > self.max_output_length:
                stderr_output = stderr_output[:self.max_output_length] + "\n... (output truncated)"
            
            return {
                "success": True,
                "stdout": stdout_output,
                "stderr": stderr_output,
                "execution_time": execution_time,
                "variables": {k: str(v) for k, v in safe_locals.items() if not k.startswith('_')},
                "error": None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_traceback = traceback.format_exc()
            
            return {
                "success": False,
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "execution_time": execution_time,
                "variables": {},
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": error_traceback
                }
            }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute code and return results."""
        code = kwargs["code"]
        language = kwargs.get("language", "python")
        timeout = kwargs.get("timeout", self.timeout)
        
        start_time = time.time()
        
        try:
            if language != "python":
                raise ToolError(f"Unsupported language: {language}")
            
            # Execute the code
            result = self._execute_python_code(code, timeout)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                success=result["success"],
                result={
                    "language": language,
                    "output": result["stdout"],
                    "errors": result["stderr"],
                    "variables": result["variables"],
                    "error_details": result["error"]
                },
                metadata={
                    "code_length": len(code),
                    "execution_time": result["execution_time"],
                    "safe_execution": True
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            raise ToolError(f"Code execution failed: {e}") from e


class PythonREPLTool(BaseTool):
    """Tool for interactive Python REPL sessions."""
    
    def __init__(self, **kwargs):
        """Initialize the Python REPL tool."""
        self.session_state = {}
        
        parameters = [
            ToolParameter(
                name="command",
                type="string",
                description="Python command to execute in REPL",
                required=True
            ),
            ToolParameter(
                name="reset_session",
                type="boolean",
                description="Whether to reset the REPL session",
                required=False,
                default=False
            )
        ]
        
        super().__init__(
            name="python_repl",
            description="Interactive Python REPL for multi-step code execution",
            parameters=parameters,
            **kwargs
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute command in persistent REPL session."""
        command = kwargs["command"]
        reset_session = kwargs.get("reset_session", False)
        
        if reset_session:
            self.session_state.clear()
        
        start_time = time.time()
        
        try:
            # Use the same safe execution as CodeExecutorTool
            executor = CodeExecutorTool()
            
            # Add session state to the code
            full_code = ""
            for var, value in self.session_state.items():
                full_code += f"{var} = {repr(value)}\n"
            full_code += command

            result = await executor.execute(code=full_code)

            # If the main execution failed, try to get more details
            if not result.success and not result.error:
                # Try to extract error from the result
                if result.result and result.result.get("errors"):
                    result.error = result.result["errors"]
            
            # Update session state with new variables (convert string values back to proper types)
            if result.success and result.result.get("variables"):
                new_vars = {}
                for var, str_value in result.result["variables"].items():
                    # Try to evaluate the string value to get the original type
                    try:
                        new_vars[var] = eval(str_value)
                    except:
                        new_vars[var] = str_value
                self.session_state.update(new_vars)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                success=result.success,
                result={
                    "output": result.result.get("output", ""),
                    "errors": result.result.get("errors", ""),
                    "session_variables": list(self.session_state.keys()),
                    "command": command
                },
                error=result.error,
                metadata={
                    "session_size": len(self.session_state),
                    "persistent_session": True
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            raise ToolError(f"REPL execution failed: {e}") from e
