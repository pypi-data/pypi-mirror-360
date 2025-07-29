"""
MCP Server Implementation

Makes every Agent X agent available as an MCP server, enabling universal interoperability.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from ..core.exceptions import MCPError, ToolError

if TYPE_CHECKING:
    from ..core.agent import Agent


@dataclass
class MCPRequest:
    """Represents an MCP JSON-RPC request."""
    jsonrpc: str
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


@dataclass 
class MCPResponse:
    """Represents an MCP JSON-RPC response."""
    jsonrpc: str
    id: Optional[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPServer:
    """
    MCP server that exposes an Agent X agent as an MCP endpoint.
    
    This makes every agent universally accessible to any MCP-compatible client,
    including other Agent X agents, Claude Desktop, and third-party tools.
    """
    
    def __init__(
        self,
        agent: 'Agent',
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "0.1.0"
    ):
        """
        Initialize MCP server for an agent.
        
        Args:
            agent: Agent instance to expose
            name: Server name (defaults to agent name)
            description: Server description (defaults to agent instruction)
            version: Server version
        """
        self.agent = agent
        self.name = name or agent.config.name
        self.description = description or agent.config.instruction
        self.version = version
        
        # Create FastAPI app
        self.app = FastAPI(
            title=f"Agent X MCP Server - {self.name}",
            description=self.description,
            version=self.version
        )
        
        # Track active connections
        self.connections: List[WebSocket] = []
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes for MCP protocol."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server information."""
            return {
                "name": self.name,
                "description": self.description,
                "version": self.version,
                "protocol": "mcp",
                "agent": {
                    "name": self.agent.config.name,
                    "model": self.agent.config.model,
                    "reasoning": self.agent.config.reasoning
                }
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy", "agent": self.agent.config.name}
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request_data: dict):
            """Handle MCP JSON-RPC requests via HTTP."""
            try:
                request = MCPRequest(**request_data)
                response = await self._handle_request(request)
                return response.__dict__
            except Exception as e:
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request_data.get("id"),
                    error={
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                ).__dict__
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """Handle MCP requests via WebSocket."""
            await websocket.accept()
            self.connections.append(websocket)
            
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    request_data = json.loads(data)
                    
                    # Handle request
                    request = MCPRequest(**request_data)
                    response = await self._handle_request(request)
                    
                    # Send response
                    await websocket.send_text(json.dumps(response.__dict__))
                    
            except Exception as e:
                # Send error response
                error_response = MCPResponse(
                    jsonrpc="2.0",
                    id=request_data.get("id") if 'request_data' in locals() else None,
                    error={
                        "code": -32603,
                        "message": f"WebSocket error: {str(e)}"
                    }
                )
                try:
                    await websocket.send_text(json.dumps(error_response.__dict__))
                except:
                    pass
            finally:
                self.connections.remove(websocket)
    
    async def _handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        Handle an MCP request and return appropriate response.
        
        Args:
            request: MCP request to handle
            
        Returns:
            MCP response
        """
        try:
            if request.method == "initialize":
                return await self._handle_initialize(request)
            elif request.method == "tools/list":
                return await self._handle_tools_list(request)
            elif request.method == "tools/call":
                return await self._handle_tools_call(request)
            elif request.method == "chat":
                return await self._handle_chat(request)
            else:
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error={
                        "code": -32601,
                        "message": f"Method not found: {request.method}"
                    }
                )
                
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialization request."""
        client_info = request.params.get("clientInfo", {})
        
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "chat": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                    "description": self.description
                },
                "agentInfo": {
                    "name": self.agent.config.name,
                    "model": self.agent.config.model,
                    "reasoning": self.agent.config.reasoning,
                    "tools": len(self.agent.get_tools())
                }
            }
        )
    
    async def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools list request."""
        # Ensure agent is initialized
        await self.agent._ensure_initialized()
        
        # Get tool schemas from the agent's tool registry
        if self.agent._tool_registry:
            tools = self.agent._tool_registry.get_tool_schemas()
        else:
            tools = []
        
        # Add the agent's chat capability as a tool
        chat_tool = {
            "name": "chat",
            "description": f"Chat with {self.agent.config.name}",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to send to the agent"
                    },
                    "session_id": {
                        "type": "string",
                        "description": "Optional session ID for conversation context"
                    }
                },
                "required": ["message"],
                "additionalProperties": False
            }
        }
        tools.append(chat_tool)
        
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={"tools": tools}
        )
    
    async def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tool call request."""
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if not tool_name:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32602,
                    "message": "Missing required parameter: name"
                }
            )
        
        try:
            # Ensure agent is initialized
            await self.agent._ensure_initialized()
            
            if tool_name == "chat":
                # Handle chat requests
                message = arguments.get("message")
                session_id = arguments.get("session_id")
                
                if not message:
                    return MCPResponse(
                        jsonrpc="2.0",
                        id=request.id,
                        error={
                            "code": -32602,
                            "message": "Missing required parameter: message"
                        }
                    )
                
                response = await self.agent.chat(message, session_id=session_id)
                
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": response
                            }
                        ]
                    }
                )
            
            else:
                # Handle other tool calls
                if not self.agent._tool_registry:
                    return MCPResponse(
                        jsonrpc="2.0",
                        id=request.id,
                        error={
                            "code": -32601,
                            "message": f"Tool not found: {tool_name}"
                        }
                    )
                
                result = await self.agent._tool_registry.execute_tool(tool_name, arguments)
                
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                )
                
        except ToolError as e:
            return MCPResponse(
                jsonrpc="2.0", 
                id=request.id,
                error={
                    "code": -32602,
                    "message": str(e)
                }
            )
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            )
    
    async def _handle_chat(self, request: MCPRequest) -> MCPResponse:
        """Handle direct chat request (non-tool)."""
        message = request.params.get("message")
        session_id = request.params.get("session_id")
        
        if not message:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32602,
                    "message": "Missing required parameter: message"
                }
            )
        
        try:
            response = await self.agent.chat(message, session_id=session_id)
            
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                result={
                    "response": response,
                    "session_id": session_id or self.agent.config.session_id
                }
            )
            
        except Exception as e:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Chat failed: {str(e)}"
                }
            )
    
    async def serve(
        self,
        host: str = "localhost",
        port: int = 8080,
        log_level: str = "info"
    ) -> None:
        """
        Start the MCP server.
        
        Args:
            host: Host to bind to
            port: Port to serve on
            log_level: Logging level
        """
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level=log_level
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self) -> None:
        """Stop the MCP server and close connections."""
        # Close all WebSocket connections
        for websocket in self.connections.copy():
            try:
                await websocket.close()
            except:
                pass
        
        self.connections.clear()


# Convenience functions

async def serve_mcp(
    agent: 'Agent',
    host: str = "localhost", 
    port: int = 8080,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """
    Convenience function to serve an agent as MCP server.
    
    Args:
        agent: Agent to serve
        host: Host to bind to
        port: Port to serve on
        name: Server name
        description: Server description
    """
    server = MCPServer(agent, name=name, description=description)
    await server.serve(host=host, port=port)


def create_mcp_server(
    agent: 'Agent',
    name: Optional[str] = None,
    description: Optional[str] = None
) -> MCPServer:
    """
    Create an MCP server instance for an agent.
    
    Args:
        agent: Agent to serve
        name: Server name
        description: Server description
        
    Returns:
        MCPServer instance
    """
    return MCPServer(agent, name=name, description=description)