"""
AA Kit Exception Hierarchy

Clean, comprehensive exception handling for production-grade error management.
"""

from typing import Any, Dict, Optional


class AAKitError(Exception):
    """Base exception for all AA Kit errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class LLMError(AAKitError):
    """Errors related to LLM operations."""
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, error_code, details)
        self.model = model


class RateLimitError(LLMError):
    """Rate limit exceeded for LLM API."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        model: Optional[str] = None,
        retry_after: Optional[int] = None
    ) -> None:
        super().__init__(message, model, "RATE_LIMIT_EXCEEDED")
        self.retry_after = retry_after


class ModelNotAvailableError(LLMError):
    """Requested model is not available."""
    
    def __init__(
        self,
        model: str,
        available_models: Optional[list] = None
    ) -> None:
        message = f"Model '{model}' is not available"
        if available_models:
            message += f". Available models: {', '.join(available_models)}"
        super().__init__(message, model, "MODEL_NOT_AVAILABLE")
        self.available_models = available_models or []


class ToolError(AAKitError):
    """Errors related to tool operations."""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, error_code, details)
        self.tool_name = tool_name


class ToolNotFoundError(ToolError):
    """Requested tool was not found."""
    
    def __init__(
        self,
        tool_name: str,
        available_tools: Optional[list] = None
    ) -> None:
        message = f"Tool '{tool_name}' not found"
        if available_tools:
            message += f". Available tools: {', '.join(available_tools)}"
        super().__init__(message, tool_name, "TOOL_NOT_FOUND")
        self.available_tools = available_tools or []


class ToolExecutionError(ToolError):
    """Error during tool execution."""
    
    def __init__(
        self,
        tool_name: str,
        original_error: Exception,
        arguments: Optional[Dict[str, Any]] = None
    ) -> None:
        message = f"Tool '{tool_name}' execution failed: {str(original_error)}"
        super().__init__(message, tool_name, "TOOL_EXECUTION_FAILED")
        self.original_error = original_error
        self.arguments = arguments or {}


class MemoryError(AAKitError):
    """Errors related to memory operations."""
    
    def __init__(
        self,
        message: str,
        backend: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, error_code, details)
        self.backend = backend


class MemoryConnectionError(MemoryError):
    """Failed to connect to memory backend."""
    
    def __init__(
        self,
        backend: str,
        connection_string: str,
        original_error: Optional[Exception] = None
    ) -> None:
        message = f"Failed to connect to memory backend '{backend}': {connection_string}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, backend, "MEMORY_CONNECTION_FAILED")
        self.connection_string = connection_string
        self.original_error = original_error


class MCPError(AAKitError):
    """Errors related to MCP operations."""
    
    def __init__(
        self,
        message: str,
        endpoint: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, error_code, details)
        self.endpoint = endpoint


class MCPConnectionError(MCPError):
    """Failed to connect to MCP server."""
    
    def __init__(
        self,
        endpoint: str,
        original_error: Optional[Exception] = None
    ) -> None:
        message = f"Failed to connect to MCP server: {endpoint}"
        if original_error:
            message += f" - {str(original_error)}"
        super().__init__(message, endpoint, "MCP_CONNECTION_FAILED")
        self.original_error = original_error


class ConfigurationError(AAKitError):
    """Invalid configuration provided."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        valid_values: Optional[list] = None
    ) -> None:
        if config_key and valid_values:
            message += f". Valid values for '{config_key}': {', '.join(map(str, valid_values))}"
        super().__init__(message, "INVALID_CONFIGURATION")
        self.config_key = config_key
        self.valid_values = valid_values or []


class ReasoningError(AAKitError):
    """Errors related to reasoning operations."""
    
    def __init__(
        self,
        message: str,
        reasoning_type: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, error_code, details)
        self.reasoning_type = reasoning_type