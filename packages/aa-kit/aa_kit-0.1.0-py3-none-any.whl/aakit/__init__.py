"""
AA Kit - The Universal AI Agent Framework for the MCP Era

A revolutionary framework for building AI agents that naturally compose into ecosystems.
Every agent is simultaneously a standalone agent, an MCP server, and an MCP client.

Example:
    >>> from aakit import Agent
    >>> agent = Agent(
    ...     name="assistant",
    ...     instruction="You are a helpful assistant",
    ...     model="gpt-4"
    ... )
    >>> response = agent.chat("Hello!")
    >>> agent.serve_mcp(port=8080)  # Now available as MCP server
"""

__version__ = "0.1.0"
__author__ = "Harsh Joshi"
__email__ = "harsh.joshi.pth@gmail.com"

# Core imports - the main API surface
from .core.agent import Agent
from .core.exceptions import AAKitError, LLMError, ToolError, MemoryError

# Utility imports for advanced usage
from .memory.factory import MemoryFactory
from .tools.registry import ToolRegistry
from .mcp.server import serve_mcp
from .mcp.client import discover_mcp_tools

# Version info
__all__ = [
    # Core classes
    "Agent",
    
    # Exceptions
    "AAKitError",
    "LLMError", 
    "ToolError",
    "MemoryError",
    
    # Utilities
    "MemoryFactory",
    "ToolRegistry",
    "serve_mcp",
    "discover_mcp_tools",
    
    # Version
    "__version__",
]

# Package metadata
PACKAGE_NAME = "aa-kit"
REPOSITORY_URL = "https://github.com/josharsh/aa-kit"
DOCUMENTATION_URL = "https://docs.aa-kit.dev"
HOMEPAGE_URL = "https://aa-kit.dev"