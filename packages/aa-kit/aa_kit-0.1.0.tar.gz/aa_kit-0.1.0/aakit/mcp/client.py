"""
MCP Client Implementation

Client for connecting to external MCP servers and using their tools.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import aiohttp
import websockets

from ..core.exceptions import MCPError, MCPConnectionError


@dataclass
class MCPToolInfo:
    """Information about an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    metadata: Dict[str, Any]


class MCPClient:
    """
    Client for connecting to MCP servers.
    
    Supports both HTTP and WebSocket connections to MCP servers.
    """
    
    def __init__(self, server_url: str, timeout: int = 30):
        """
        Initialize MCP client.
        
        Args:
            server_url: URL of the MCP server
            timeout: Request timeout in seconds
        """
        self.server_url = server_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.connection_type: Optional[str] = None
    
    async def connect(self) -> None:
        """Establish connection to the MCP server."""
        if self.is_connected:
            return
        
        try:
            if self.server_url.startswith(("ws://", "wss://")):
                await self._connect_websocket()
            else:
                await self._connect_http()
            
            self.is_connected = True
            
        except Exception as e:
            raise MCPConnectionError(
                endpoint=self.server_url,
                original_error=e
            )
    
    async def _connect_websocket(self) -> None:
        """Connect via WebSocket."""
        try:
            self.websocket = await websockets.connect(
                self.server_url,
                timeout=self.timeout
            )
            self.connection_type = "websocket"
            
            # Send initialization message
            init_message = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "omniagent",
                        "version": "0.1.0"
                    }
                },
                "id": 1
            }
            
            await self.websocket.send(json.dumps(init_message))
            response = await self.websocket.recv()
            init_response = json.loads(response)
            
            if "error" in init_response:
                raise MCPError(
                    f"MCP initialization failed: {init_response['error']['message']}",
                    endpoint=self.server_url
                )
                
        except websockets.exceptions.WebSocketException as e:
            raise MCPConnectionError(
                endpoint=self.server_url,
                original_error=e
            )
    
    async def _connect_http(self) -> None:
        """Connect via HTTP."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        self.connection_type = "http"
        
        # Test connection with a simple request
        try:
            async with self.session.get(f"{self.server_url}/health") as response:
                if response.status >= 400:
                    raise MCPError(
                        f"MCP server health check failed: {response.status}",
                        endpoint=self.server_url
                    )
        except aiohttp.ClientError as e:
            raise MCPConnectionError(
                endpoint=self.server_url,
                original_error=e
            )
    
    async def list_tools(self) -> List[MCPToolInfo]:
        """
        Get list of available tools from the MCP server.
        
        Returns:
            List of tool information
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            if self.connection_type == "websocket":
                return await self._list_tools_websocket()
            else:
                return await self._list_tools_http()
                
        except Exception as e:
            raise MCPError(
                f"Failed to list tools: {str(e)}",
                endpoint=self.server_url
            )
    
    async def _list_tools_websocket(self) -> List[MCPToolInfo]:
        """List tools via WebSocket."""
        message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if "error" in result:
            raise MCPError(
                f"Tools list failed: {result['error']['message']}",
                endpoint=self.server_url
            )
        
        tools = []
        for tool_data in result.get("result", {}).get("tools", []):
            tool_info = MCPToolInfo(
                name=tool_data["name"],
                description=tool_data.get("description", ""),
                input_schema=tool_data.get("inputSchema", {}),
                metadata=tool_data
            )
            tools.append(tool_info)
        
        return tools
    
    async def _list_tools_http(self) -> List[MCPToolInfo]:
        """List tools via HTTP."""
        async with self.session.post(
            f"{self.server_url}/tools/list",
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
        ) as response:
            result = await response.json()
            
            if "error" in result:
                raise MCPError(
                    f"Tools list failed: {result['error']['message']}",
                    endpoint=self.server_url
                )
            
            tools = []
            for tool_data in result.get("result", {}).get("tools", []):
                tool_info = MCPToolInfo(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    metadata=tool_data
                )
                tools.append(tool_info)
            
            return tools
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            if self.connection_type == "websocket":
                return await self._call_tool_websocket(tool_name, arguments)
            else:
                return await self._call_tool_http(tool_name, arguments)
                
        except Exception as e:
            raise MCPError(
                f"Tool call failed for '{tool_name}': {str(e)}",
                endpoint=self.server_url
            )
    
    async def _call_tool_websocket(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call tool via WebSocket."""
        message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 3
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        result = json.loads(response)
        
        if "error" in result:
            raise MCPError(
                f"Tool call failed: {result['error']['message']}",
                endpoint=self.server_url
            )
        
        return result.get("result")
    
    async def _call_tool_http(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call tool via HTTP."""
        async with self.session.post(
            f"{self.server_url}/tools/call",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 3
            }
        ) as response:
            result = await response.json()
            
            if "error" in result:
                raise MCPError(
                    f"Tool call failed: {result['error']['message']}",
                    endpoint=self.server_url
                )
            
            return result.get("result")
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        self.is_connected = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.session:
            await self.session.close()
            self.session = None
        
        self.connection_type = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Utility functions

async def discover_mcp_tools(server_urls: List[str]) -> Dict[str, List[MCPToolInfo]]:
    """
    Discover tools from multiple MCP servers.
    
    Args:
        server_urls: List of MCP server URLs
        
    Returns:
        Dictionary mapping server URLs to their available tools
    """
    tools_by_server = {}
    
    for server_url in server_urls:
        try:
            async with MCPClient(server_url) as client:
                tools = await client.list_tools()
                tools_by_server[server_url] = tools
        except Exception:
            # Skip servers that fail to connect
            tools_by_server[server_url] = []
    
    return tools_by_server


async def test_mcp_connection(server_url: str) -> bool:
    """
    Test connection to an MCP server.
    
    Args:
        server_url: URL of the MCP server
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        async with MCPClient(server_url) as client:
            await client.list_tools()
        return True
    except Exception:
        return False