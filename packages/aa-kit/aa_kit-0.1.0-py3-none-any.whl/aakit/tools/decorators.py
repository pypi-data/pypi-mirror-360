"""
Tool Decorators

Provides decorators for marking functions as tools and enhancing their metadata.
"""

import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

F = TypeVar('F', bound=Callable[..., Any])


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Callable[[F], F]:
    """
    Decorator to mark a function as a AA Kit tool.
    
    Args:
        name: Custom name for the tool (defaults to function name)
        description: Custom description (defaults to docstring)
        parameters: Custom parameter descriptions
        
    Returns:
        Decorated function with tool metadata
        
    Example:
        @tool(description="Search the web for information")
        def web_search(query: str, max_results: int = 5) -> str:
            '''Search the web and return results.'''
            return f"Results for: {query}"
    """
    def decorator(func: F) -> F:
        # Add tool metadata to function
        func._agentz_tool = True
        func._agentz_tool_name = name or func.__name__
        func._agentz_tool_description = description
        func._agentz_tool_parameters = parameters or {}
        
        return func
    
    return decorator


def mcp_tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    async_tool: bool = False
) -> Callable[[F], F]:
    """
    Enhanced decorator for MCP-compatible tools.
    
    Args:
        name: Custom tool name
        description: Custom description
        parameters: Parameter schema overrides
        async_tool: Whether this is an async tool
        
    Returns:
        Decorated function with enhanced MCP metadata
        
    Example:
        @mcp_tool(
            name="file_reader",
            description="Read content from a file",
            parameters={
                "file_path": {
                    "description": "Path to the file to read",
                    "required": True
                }
            }
        )
        def read_file(file_path: str) -> str:
            with open(file_path, 'r') as f:
                return f.read()
    """
    def decorator(func: F) -> F:
        # Add enhanced tool metadata
        func._agentz_tool = True
        func._agentz_mcp_tool = True
        func._agentz_tool_name = name or func.__name__
        func._agentz_tool_description = description
        func._agentz_tool_parameters = parameters or {}
        func._agentz_async_tool = async_tool
        
        # Add wrapper for async execution if needed
        if async_tool and not inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Copy metadata to wrapper
            async_wrapper._agentz_tool = True
            async_wrapper._agentz_mcp_tool = True
            async_wrapper._agentz_tool_name = name or func.__name__
            async_wrapper._agentz_tool_description = description
            async_wrapper._agentz_tool_parameters = parameters or {}
            async_wrapper._agentz_async_tool = async_tool
            async_wrapper._agentz_original_func = func
            
            return async_wrapper
        
        return func
    
    return decorator


def parameter(
    name: str,
    description: str,
    type: str = "string",
    required: bool = True,
    enum: Optional[List[str]] = None,
    default: Any = None
) -> Callable[[F], F]:
    """
    Decorator to add parameter metadata to a tool.
    Can be stacked multiple times for multiple parameters.
    
    Args:
        name: Parameter name
        description: Parameter description
        type: JSON Schema type
        required: Whether parameter is required
        enum: List of allowed values
        default: Default value
        
    Returns:
        Decorated function with parameter metadata
        
    Example:
        @tool()
        @parameter("query", "Search query", type="string", required=True)
        @parameter("limit", "Max results", type="integer", default=10)
        def search(query: str, limit: int = 10) -> str:
            return f"Searching for {query} (limit: {limit})"
    """
    def decorator(func: F) -> F:
        if not hasattr(func, '_agentz_tool_parameters'):
            func._agentz_tool_parameters = {}
        
        func._agentz_tool_parameters[name] = {
            "description": description,
            "type": type,
            "required": required,
            "enum": enum,
            "default": default
        }
        
        return func
    
    return decorator


def returns(description: str, type: str = "string") -> Callable[[F], F]:
    """
    Decorator to add return value metadata to a tool.
    
    Args:
        description: Description of what the tool returns
        type: JSON Schema type of return value
        
    Returns:
        Decorated function with return metadata
        
    Example:
        @tool()
        @returns("JSON formatted search results", type="object")
        def api_search(query: str) -> dict:
            return {"results": [], "query": query}
    """
    def decorator(func: F) -> F:
        func._agentz_tool_returns = {
            "description": description,
            "type": type
        }
        return func
    
    return decorator


def error_handler(
    errors: Dict[str, str]
) -> Callable[[F], F]:
    """
    Decorator to specify error handling for a tool.
    
    Args:
        errors: Mapping of exception types to user-friendly messages
        
    Returns:
        Decorated function with error handling
        
    Example:
        @tool()
        @error_handler({
            "FileNotFoundError": "The specified file was not found",
            "PermissionError": "Permission denied accessing the file"
        })
        def read_file(path: str) -> str:
            with open(path, 'r') as f:
                return f.read()
    """
    def decorator(func: F) -> F:
        func._agentz_tool_errors = errors
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                if error_type in errors:
                    raise type(e)(errors[error_type]) from e
                raise
        
        # Copy metadata to wrapper
        for attr in dir(func):
            if attr.startswith('_agentz_'):
                setattr(wrapper, attr, getattr(func, attr))
        
        return wrapper
    
    return decorator


# Utility functions for checking tool metadata

def is_tool(func: Callable) -> bool:
    """Check if a function is marked as a tool."""
    return getattr(func, '_agentz_tool', False)


def is_mcp_tool(func: Callable) -> bool:
    """Check if a function is marked as an MCP tool."""
    return getattr(func, '_agentz_mcp_tool', False)


def get_tool_name(func: Callable) -> Optional[str]:
    """Get the tool name from a function."""
    return getattr(func, '_agentz_tool_name', None)


def get_tool_description(func: Callable) -> Optional[str]:
    """Get the tool description from a function."""
    return getattr(func, '_agentz_tool_description', None)


def get_tool_parameters(func: Callable) -> Dict[str, Any]:
    """Get the tool parameters from a function."""
    return getattr(func, '_agentz_tool_parameters', {})


def get_tool_metadata(func: Callable) -> Dict[str, Any]:
    """Get all tool metadata from a function."""
    if not is_tool(func):
        return {}
    
    return {
        "name": get_tool_name(func),
        "description": get_tool_description(func),
        "parameters": get_tool_parameters(func),
        "is_mcp_tool": is_mcp_tool(func),
        "is_async": getattr(func, '_agentz_async_tool', False),
        "returns": getattr(func, '_agentz_tool_returns', {}),
        "errors": getattr(func, '_agentz_tool_errors', {})
    }