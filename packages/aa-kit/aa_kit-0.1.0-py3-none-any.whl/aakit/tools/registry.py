"""
Tool Registry

Central registry for managing tools, converting Python functions to MCP tools,
and handling external MCP server connections.
"""

import asyncio
import inspect
import json
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field

from .schema import ToolSchema, SchemaGenerator, enhance_schema_from_docstring
from .decorators import is_tool, get_tool_metadata
from ..core.exceptions import ToolError, ToolNotFoundError, ToolExecutionError
from ..mcp.client import MCPClient


@dataclass
class RegisteredTool:
    """Represents a registered tool in the registry."""
    name: str
    description: str
    schema: ToolSchema
    executor: Callable
    source_type: str  # "function", "mcp_server", "agent"
    source_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    """
    Central registry for all tools available to an agent.
    
    Features:
    - Convert Python functions to MCP tools
    - Connect to external MCP servers
    - Use other agents as tools
    - Type-safe tool execution
    - Automatic schema generation
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self.tools: Dict[str, RegisteredTool] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
    
    async def register_tool(
        self, 
        tool: Union[Callable, str, 'Agent'],
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Register a single tool.
        
        Args:
            tool: Function, MCP server URL, or Agent instance
            name: Custom name for the tool
            description: Custom description
        """
        if callable(tool):
            await self._register_function(tool, name, description)
        elif isinstance(tool, str):
            await self._register_mcp_server(tool)
        else:
            # Assume it's an Agent instance
            await self._register_agent(tool, name)
    
    async def register_tools(
        self,
        tools: List[Union[Callable, str, 'Agent']]
    ) -> None:
        """
        Register multiple tools.
        
        Args:
            tools: List of functions, MCP URLs, or Agent instances
        """
        for tool in tools:
            await self.register_tool(tool)
    
    async def _register_function(
        self,
        func: Callable,
        custom_name: Optional[str] = None,
        custom_description: Optional[str] = None
    ) -> None:
        """Register a Python function as a tool."""
        # Generate schema from function
        schema = SchemaGenerator.from_function(func)
        
        # Enhance with docstring information
        schema = enhance_schema_from_docstring(schema, func)
        
        # Apply custom overrides
        if custom_name:
            schema.name = custom_name
        if custom_description:
            schema.description = custom_description
        
        # Check for decorator metadata
        if is_tool(func):
            metadata = get_tool_metadata(func)
            if metadata.get('name'):
                schema.name = metadata['name']
            if metadata.get('description'):
                schema.description = metadata['description']
            
            # Apply parameter overrides from decorators
            decorator_params = metadata.get('parameters', {})
            for param in schema.parameters:
                if param.name in decorator_params:
                    param_meta = decorator_params[param.name]
                    if 'description' in param_meta:
                        param.description = param_meta['description']
                    if 'required' in param_meta:
                        param.required = param_meta['required']
                    if 'enum' in param_meta:
                        param.enum = param_meta['enum']
        
        # Create executor wrapper
        if inspect.iscoroutinefunction(func):
            executor = func
        else:
            # Wrap sync functions to be async
            async def async_executor(*args, **kwargs):
                return func(*args, **kwargs)
            executor = async_executor
        
        # Register the tool
        registered_tool = RegisteredTool(
            name=schema.name,
            description=schema.description,
            schema=schema,
            executor=executor,
            source_type="function",
            source_info={
                "function_name": func.__name__,
                "module": getattr(func, '__module__', 'unknown'),
                "is_async": inspect.iscoroutinefunction(func)
            }
        )
        
        self.tools[schema.name] = registered_tool
    
    async def _register_mcp_server(self, server_url: str) -> None:
        """Register tools from an external MCP server."""
        try:
            # Create MCP client
            client = MCPClient(server_url)
            await client.connect()
            
            # Get available tools
            tools = await client.list_tools()
            
            # Register each tool
            for tool_info in tools:
                tool_name = tool_info['name']
                
                # Create executor that calls MCP server
                async def mcp_executor(*args, **kwargs):
                    return await client.call_tool(tool_name, kwargs)
                
                # Create schema from MCP tool info
                schema = self._mcp_info_to_schema(tool_info)
                
                registered_tool = RegisteredTool(
                    name=tool_name,
                    description=tool_info.get('description', ''),
                    schema=schema,
                    executor=mcp_executor,
                    source_type="mcp_server",
                    source_info={
                        "server_url": server_url,
                        "tool_info": tool_info
                    }
                )
                
                self.tools[tool_name] = registered_tool
            
            # Store client for later use
            self.mcp_clients[server_url] = client
            
        except Exception as e:
            raise ToolError(
                f"Failed to register MCP server tools from {server_url}: {str(e)}",
                error_code="MCP_REGISTRATION_FAILED"
            )
    
    async def _register_agent(
        self,
        agent: 'Agent',
        custom_name: Optional[str] = None
    ) -> None:
        """Register another agent as a tool."""
        tool_name = custom_name or f"{agent.config.name}_agent"
        
        # Create executor that chats with the agent
        async def agent_executor(message: str, **kwargs) -> str:
            return await agent.chat(message, **kwargs)
        
        # Create simple schema for agent tool
        from .schema import ParameterSchema
        schema = ToolSchema(
            name=tool_name,
            description=f"Chat with {agent.config.name}: {agent.config.instruction}",
            parameters=[
                ParameterSchema(
                    name="message",
                    type="string",
                    description="Message to send to the agent",
                    required=True
                )
            ]
        )
        
        registered_tool = RegisteredTool(
            name=tool_name,
            description=schema.description,
            schema=schema,
            executor=agent_executor,
            source_type="agent",
            source_info={
                "agent_name": agent.config.name,
                "agent_model": agent.config.model,
                "agent_instruction": agent.config.instruction
            }
        )
        
        self.tools[tool_name] = registered_tool
    
    def _mcp_info_to_schema(self, tool_info: Dict[str, Any]) -> ToolSchema:
        """Convert MCP tool info to ToolSchema."""
        from .schema import ParameterSchema
        
        name = tool_info['name']
        description = tool_info.get('description', f'MCP tool: {name}')
        
        # Extract parameters from input schema
        parameters = []
        input_schema = tool_info.get('inputSchema', {})
        properties = input_schema.get('properties', {})
        required = input_schema.get('required', [])
        
        for param_name, param_info in properties.items():
            param_schema = ParameterSchema(
                name=param_name,
                type=param_info.get('type', 'string'),
                description=param_info.get('description', f'Parameter: {param_name}'),
                required=param_name in required,
                enum=param_info.get('enum')
            )
            parameters.append(param_schema)
        
        return ToolSchema(
            name=name,
            description=description,
            parameters=parameters
        )
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Execute a registered tool.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Result from tool execution
        """
        if tool_name not in self.tools:
            raise ToolNotFoundError(tool_name, list(self.tools.keys()))
        
        tool = self.tools[tool_name]
        
        try:
            # Validate arguments against schema
            self._validate_arguments(tool.schema, arguments)
            
            # Execute the tool
            if tool.source_type == "function":
                # Always await since we wrap sync functions to be async
                result = await tool.executor(**arguments)
            else:
                # For MCP servers and agents, pass arguments as kwargs
                result = await tool.executor(**arguments)
            
            return result
            
        except Exception as e:
            if isinstance(e, (ToolNotFoundError, ToolError)):
                raise
            
            raise ToolExecutionError(
                tool_name=tool_name,
                original_error=e,
                arguments=arguments
            )
    
    def _validate_arguments(
        self,
        schema: ToolSchema,
        arguments: Dict[str, Any]
    ) -> None:
        """Validate arguments against tool schema."""
        # Check required parameters
        for param in schema.parameters:
            if param.required and param.name not in arguments:
                raise ToolError(
                    f"Missing required parameter '{param.name}' for tool '{schema.name}'",
                    tool_name=schema.name,
                    error_code="MISSING_PARAMETER"
                )
        
        # Check enum constraints
        for param in schema.parameters:
            if param.name in arguments and param.enum:
                value = arguments[param.name]
                if value not in param.enum:
                    raise ToolError(
                        f"Parameter '{param.name}' must be one of {param.enum}, got '{value}'",
                        tool_name=schema.name,
                        error_code="INVALID_ENUM_VALUE"
                    )
    
    def unregister_tool(self, tool_name: str) -> None:
        """Remove a tool from the registry."""
        if tool_name in self.tools:
            del self.tools[tool_name]
    
    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self.tools.keys())
    
    def get_tool_schema(self, tool_name: str) -> Optional[ToolSchema]:
        """Get schema for a specific tool."""
        if tool_name in self.tools:
            return self.tools[tool_name].schema
        return None
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get MCP schemas for all registered tools."""
        return [
            tool.schema.to_mcp_schema()
            for tool in self.tools.values()
        ]
    
    def get_tools_info(self) -> Dict[str, Any]:
        """Get comprehensive information about all tools."""
        return {
            "total_tools": len(self.tools),
            "tools_by_source": self._get_tools_by_source(),
            "tools": {
                name: {
                    "name": tool.name,
                    "description": tool.description,
                    "source_type": tool.source_type,
                    "parameters": len(tool.schema.parameters),
                    "source_info": tool.source_info
                }
                for name, tool in self.tools.items()
            }
        }
    
    def _get_tools_by_source(self) -> Dict[str, int]:
        """Get count of tools by source type."""
        counts = {}
        for tool in self.tools.values():
            counts[tool.source_type] = counts.get(tool.source_type, 0) + 1
        return counts
    
    async def close(self) -> None:
        """Close all MCP client connections."""
        for client in self.mcp_clients.values():
            await client.disconnect()
        self.mcp_clients.clear()