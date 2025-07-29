"""
Agent X Core Agent Implementation

The heart of the Agent X framework - a production-grade agent class that embodies
our core principles of simplicity, MCP-first design, and universal interoperability.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field

from ..llm.manager import LLMManager
from ..memory.factory import MemoryFactory
from ..tools.registry import ToolRegistry
from ..reasoning.factory import ReasoningFactory
from ..mcp.server import MCPServer
from .exceptions import AAKitError, ConfigurationError, ModelNotAvailableError


@dataclass
class AgentConfig:
    """Configuration for an Agent instance."""
    
    name: str
    instruction: str
    model: str
    tools: List[Union[Callable, str]] = field(default_factory=list)
    memory: Optional[Union[str, Dict[str, Any]]] = None
    reasoning: str = "simple"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Agent:
    """
    Universal AI Agent for the MCP Era.
    
    Every Agent instance is simultaneously:
    - A standalone conversational agent
    - An MCP server exposing its capabilities
    - An MCP client that can use other agents/tools
    
    Example:
        >>> agent = Agent(
        ...     name="assistant",
        ...     instruction="You are a helpful assistant",
        ...     model="gpt-4"
        ... )
        >>> response = agent.chat("Hello!")
        >>> agent.serve_mcp(port=8080)  # Now available as MCP server
    """
    
    def __init__(
        self,
        name: str,
        instruction: str,
        model: str,
        tools: Optional[List[Union[Callable, str]]] = None,
        memory: Optional[Union[str, Dict[str, Any]]] = None,
        reasoning: str = "simple",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize an Agent.
        
        Args:
            name: Unique identifier for this agent
            instruction: System instruction defining the agent's behavior
            model: LLM model to use (e.g., "gpt-4", "claude-3-sonnet")
            tools: List of tools/functions this agent can use
            memory: Memory backend configuration
            reasoning: Reasoning pattern ("simple", "react", "chain_of_thought")
            temperature: LLM temperature (0.0-1.0)
            max_tokens: Maximum tokens for responses
            session_id: Session ID for memory isolation
            **kwargs: Additional metadata
        """
        # Validate required parameters
        if not name or not name.strip():
            raise ConfigurationError("Agent name cannot be empty")
        
        if not instruction or not instruction.strip():
            raise ConfigurationError("Agent instruction cannot be empty")
        
        if not model or not model.strip():
            raise ConfigurationError("Agent model cannot be empty")
        
        # Initialize configuration
        self.config = AgentConfig(
            name=name.strip(),
            instruction=instruction.strip(),
            model=model.strip(),
            tools=tools or [],
            memory=memory,
            reasoning=reasoning,
            temperature=temperature,
            max_tokens=max_tokens,
            session_id=session_id or str(uuid.uuid4()),
            metadata=kwargs
        )
        
        # Initialize core components
        self._llm_manager: Optional[LLMManager] = None
        self._memory = None
        self._tool_registry: Optional[ToolRegistry] = None
        self._reasoning_engine = None
        self._mcp_server: Optional[MCPServer] = None
        self._initialized = False
    
    async def _ensure_initialized(self) -> None:
        """Lazy initialization of agent components."""
        if self._initialized:
            return
        
        try:
            # Initialize LLM Manager
            self._llm_manager = LLMManager(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Initialize Memory
            if self.config.memory:
                self._memory = await MemoryFactory.create(
                    config=self.config.memory,
                    session_id=self.config.session_id
                )
            
            # Initialize Tool Registry
            self._tool_registry = ToolRegistry()
            await self._tool_registry.register_tools(self.config.tools)
            
            # Initialize Reasoning Engine
            self._reasoning_engine = ReasoningFactory.create(
                pattern=self.config.reasoning,
                llm_manager=self._llm_manager,
                tool_registry=self._tool_registry,
                memory=self._memory
            )
            
            self._initialized = True
            
        except ModelNotAvailableError:
            # If model is not available due to missing API keys, still initialize other components
            # This allows testing without API keys
            self._llm_manager = None
            
            # Initialize Memory
            if self.config.memory:
                self._memory = await MemoryFactory.create(
                    config=self.config.memory,
                    session_id=self.config.session_id
                )
            
            # Initialize Tool Registry
            self._tool_registry = ToolRegistry()
            await self._tool_registry.register_tools(self.config.tools)
            
            # Reasoning engine will be None without LLM
            self._reasoning_engine = None
            
            self._initialized = True
            
        except Exception as e:
            raise AAKitError(f"Failed to initialize agent '{self.config.name}': {str(e)}")
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """
        Chat with the agent.
        
        Args:
            message: User message
            session_id: Optional session ID override
            **kwargs: Additional parameters for the reasoning engine
            
        Returns:
            Agent's response as a string
        """
        await self._ensure_initialized()
        
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        if not self._reasoning_engine:
            raise AAKitError(
                f"Cannot chat: Agent '{self.config.name}' requires valid API credentials. "
                f"Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable."
            )
        
        try:
            # Use provided session_id or fall back to agent's default
            effective_session_id = session_id or self.config.session_id
            
            # Execute reasoning with the user message
            response = await self._reasoning_engine.execute(
                instruction=self.config.instruction,
                message=message.strip(),
                session_id=effective_session_id,
                **kwargs
            )
            
            return response
            
        except Exception as e:
            raise AAKitError(f"Chat failed for agent '{self.config.name}': {str(e)}")
    
    async def stream_chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Stream chat responses from the agent.
        
        Args:
            message: User message
            session_id: Optional session ID override
            **kwargs: Additional parameters for the reasoning engine
            
        Yields:
            Partial responses as they become available
        """
        await self._ensure_initialized()
        
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        try:
            effective_session_id = session_id or self.config.session_id
            
            async for chunk in self._reasoning_engine.stream_execute(
                instruction=self.config.instruction,
                message=message.strip(),
                session_id=effective_session_id,
                **kwargs
            ):
                yield chunk
                
        except Exception as e:
            raise AAKitError(f"Stream chat failed for agent '{self.config.name}': {str(e)}")
    
    def serve_mcp(
        self,
        port: int = 8080,
        host: str = "localhost",
        background: bool = False
    ) -> Optional[MCPServer]:
        """
        Serve this agent as an MCP server.
        
        Args:
            port: Port to serve on
            host: Host to bind to
            background: Whether to run in background
            
        Returns:
            MCPServer instance if background=True, None otherwise
        """
        if not self._initialized:
            # Run initialization synchronously for MCP server
            asyncio.run(self._ensure_initialized())
        
        self._mcp_server = MCPServer(
            agent=self,
            name=self.config.name,
            description=self.config.instruction
        )
        
        if background:
            # Start server in background
            asyncio.create_task(self._mcp_server.serve(host=host, port=port))
            return self._mcp_server
        else:
            # Run server in foreground
            asyncio.run(self._mcp_server.serve(host=host, port=port))
            return None
    
    async def add_tool(self, tool: Union[Callable, str]) -> None:
        """
        Add a tool to this agent.
        
        Args:
            tool: Function or MCP server endpoint to add
        """
        await self._ensure_initialized()
        await self._tool_registry.register_tool(tool)
    
    async def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from this agent.
        
        Args:
            tool_name: Name of the tool to remove
        """
        await self._ensure_initialized()
        self._tool_registry.unregister_tool(tool_name)
    
    def get_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        if not self._tool_registry:
            return []
        return self._tool_registry.list_tools()
    
    async def clear_memory(self, session_id: Optional[str] = None) -> None:
        """
        Clear agent memory for a session.
        
        Args:
            session_id: Session ID to clear, or current session if None
        """
        if self._memory:
            effective_session_id = session_id or self.config.session_id
            await self._memory.clear(effective_session_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent configuration to dictionary.
        
        Returns:
            Dictionary representation of the agent
        """
        return {
            "name": self.config.name,
            "instruction": self.config.instruction,
            "model": self.config.model,
            "tools": [
                tool if isinstance(tool, str) else tool.__name__ 
                for tool in self.config.tools
            ],
            "memory": self.config.memory,
            "reasoning": self.config.reasoning,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "session_id": self.config.session_id,
            "metadata": self.config.metadata,
            "initialized": self._initialized
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return (
            f"Agent(name='{self.config.name}', model='{self.config.model}', "
            f"tools={len(self.config.tools)}, reasoning='{self.config.reasoning}')"
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_initialized()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # Cleanup resources if needed
        if self._memory:
            await self._memory.close()
        
        if self._mcp_server:
            await self._mcp_server.stop()


# Convenience function for quick agent creation
def create_agent(
    name: str,
    instruction: str,
    model: str = "gpt-4",
    **kwargs: Any
) -> Agent:
    """
    Create an agent with minimal configuration.
    
    Args:
        name: Agent name
        instruction: System instruction
        model: LLM model (defaults to gpt-4)
        **kwargs: Additional agent parameters
        
    Returns:
        Configured Agent instance
    """
    return Agent(
        name=name,
        instruction=instruction,
        model=model,
        **kwargs
    )