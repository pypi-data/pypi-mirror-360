"""MCP (Model Context Protocol) integration for Agent X."""

from .server import MCPServer, serve_mcp
from .client import MCPClient, discover_mcp_tools

__all__ = ["MCPServer", "serve_mcp", "MCPClient", "discover_mcp_tools"]