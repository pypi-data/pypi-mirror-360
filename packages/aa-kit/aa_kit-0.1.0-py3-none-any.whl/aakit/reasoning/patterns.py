"""
Reasoning Pattern Implementations

Different approaches to AI agent reasoning and tool use.
"""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator, TYPE_CHECKING

if TYPE_CHECKING:
    from ..llm.manager import LLMManager
    from ..tools.registry import ToolRegistry
    from ..memory.backends import MemoryBackend

from ..llm.providers import LLMMessage
from ..core.exceptions import AAKitError, ToolError


class ReasoningPattern(ABC):
    """Abstract base class for reasoning patterns."""
    
    def __init__(
        self,
        llm_manager: 'LLMManager',
        tool_registry: Optional['ToolRegistry'] = None,
        memory: Optional['MemoryBackend'] = None
    ):
        """
        Initialize reasoning pattern.
        
        Args:
            llm_manager: LLM manager for generating responses
            tool_registry: Registry of available tools
            memory: Memory backend for conversation history
        """
        self.llm_manager = llm_manager
        self.tool_registry = tool_registry
        self.memory = memory
    
    @abstractmethod
    async def execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> str:
        """Execute reasoning with the given inputs."""
        pass
    
    @abstractmethod
    async def stream_execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Execute reasoning with streaming output."""
        pass
    
    async def _load_conversation_history(self, session_id: str) -> List[LLMMessage]:
        """Load conversation history from memory."""
        messages = [LLMMessage(role="system", content="")]  # Placeholder for system message
        
        if self.memory:
            try:
                history = await self.memory.retrieve(session_id, limit=50)
                for record in history:
                    messages.append(LLMMessage(
                        role=record.role,
                        content=record.content,
                        metadata=record.metadata
                    ))
            except Exception:
                # If memory fails, continue without history
                pass
        
        return messages
    
    async def _save_to_memory(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Save message to memory."""
        if self.memory:
            try:
                await self.memory.store(session_id, role, content, metadata)
            except Exception:
                # If memory fails, continue without saving
                pass


class SimpleReasoning(ReasoningPattern):
    """
    Simple reasoning pattern - direct LLM calls without tools.
    
    Best for basic conversation and tasks that don't require external tools.
    """
    
    async def execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> str:
        """Execute simple reasoning."""
        # Load conversation history
        messages = await self._load_conversation_history(session_id)
        messages[0].content = instruction  # Set system message
        
        # Add user message
        messages.append(LLMMessage(role="user", content=message))
        
        # Save user message to memory
        await self._save_to_memory(session_id, "user", message)
        
        # Get LLM response
        response = await self.llm_manager.chat(messages, **kwargs)
        
        # Save assistant response to memory
        await self._save_to_memory(session_id, "assistant", response.content)
        
        return response.content
    
    async def stream_execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Execute simple reasoning with streaming."""
        # Load conversation history
        messages = await self._load_conversation_history(session_id)
        messages[0].content = instruction
        
        # Add user message
        messages.append(LLMMessage(role="user", content=message))
        
        # Save user message to memory
        await self._save_to_memory(session_id, "user", message)
        
        # Stream LLM response
        full_response = ""
        async for chunk in self.llm_manager.stream_chat(messages, **kwargs):
            full_response += chunk
            yield chunk
        
        # Save complete response to memory
        await self._save_to_memory(session_id, "assistant", full_response)


class ReActReasoning(ReasoningPattern):
    """
    ReAct (Reasoning + Acting) pattern implementation.
    
    Follows the Think → Act → Observe cycle for tool-based problem solving.
    """
    
    MAX_ITERATIONS = 10
    
    def __init__(
        self,
        llm_manager: 'LLMManager',
        tool_registry: Optional['ToolRegistry'] = None,
        memory: Optional['MemoryBackend'] = None,
        max_iterations: int = 10
    ):
        """Initialize ReAct reasoning with iteration limit."""
        super().__init__(llm_manager, tool_registry, memory)
        self.max_iterations = max_iterations
    
    async def execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> str:
        """Execute ReAct reasoning loop."""
        if not self.tool_registry:
            # Fall back to simple reasoning if no tools available
            simple = SimpleReasoning(self.llm_manager, self.tool_registry, self.memory)
            return await simple.execute(instruction, message, session_id, **kwargs)
        
        # Load conversation history
        messages = await self._load_conversation_history(session_id)
        
        # Create enhanced system message with ReAct instructions
        react_instruction = self._create_react_system_message(instruction)
        messages[0].content = react_instruction
        
        # Add user message
        messages.append(LLMMessage(role="user", content=message))
        await self._save_to_memory(session_id, "user", message)
        
        # Execute ReAct loop
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            # Get LLM response
            response = await self.llm_manager.chat(messages, **kwargs)
            assistant_message = response.content
            
            # Parse the response for actions
            action_match = self._parse_action(assistant_message)
            
            if action_match:
                # Execute the action
                tool_name = action_match["tool"]
                tool_args = action_match["arguments"]
                
                try:
                    # Execute tool
                    tool_result = await self.tool_registry.execute_tool(tool_name, tool_args)
                    
                    # Add assistant message with action
                    messages.append(LLMMessage(role="assistant", content=assistant_message))
                    
                    # Add observation
                    observation = f"Observation: {str(tool_result)}"
                    messages.append(LLMMessage(role="user", content=observation))
                    
                    # Save to memory
                    await self._save_to_memory(session_id, "assistant", assistant_message)
                    await self._save_to_memory(session_id, "user", observation)
                    
                except ToolError as e:
                    # Handle tool error
                    error_observation = f"Observation: Tool error - {str(e)}"
                    messages.append(LLMMessage(role="assistant", content=assistant_message))
                    messages.append(LLMMessage(role="user", content=error_observation))
                    
                    await self._save_to_memory(session_id, "assistant", assistant_message)
                    await self._save_to_memory(session_id, "user", error_observation)
            
            else:
                # No action found, this should be the final answer
                await self._save_to_memory(session_id, "assistant", assistant_message)
                return assistant_message
        
        # If we hit max iterations, return the last response
        await self._save_to_memory(session_id, "assistant", assistant_message)
        return assistant_message + "\n\n(Note: Reached maximum reasoning iterations)"
    
    async def stream_execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Execute ReAct reasoning with streaming (simplified)."""
        # For streaming, we'll use a simplified approach
        # Full ReAct streaming would require complex state management
        
        result = await self.execute(instruction, message, session_id, **kwargs)
        
        # Stream the result in chunks
        chunk_size = 50
        for i in range(0, len(result), chunk_size):
            chunk = result[i:i+chunk_size]
            yield chunk
            await asyncio.sleep(0.01)  # Small delay to simulate streaming
    
    def _create_react_system_message(self, base_instruction: str) -> str:
        """Create ReAct-enhanced system message."""
        available_tools = []
        if self.tool_registry:
            for tool_name in self.tool_registry.list_tools():
                schema = self.tool_registry.get_tool_schema(tool_name)
                if schema:
                    available_tools.append(f"- {tool_name}: {schema.description}")
        
        tools_text = "\n".join(available_tools) if available_tools else "No tools available."
        
        return f"""{base_instruction}

You have access to the following tools:
{tools_text}

When you need to use a tool, use this exact format:
Action: tool_name
Arguments: {{"arg1": "value1", "arg2": "value2"}}

After using a tool, you will receive an observation with the result. You can then:
1. Use another tool if needed
2. Provide your final answer

Think step by step and use tools when necessary to complete the task.

Remember:
- Use the exact format for actions
- Wait for observations before proceeding
- Provide clear, helpful responses"""
    
    def _parse_action(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse action from LLM response."""
        # Look for Action: pattern
        action_pattern = r"Action:\s*(\w+)"
        args_pattern = r"Arguments:\s*(\{.*?\})"
        
        action_match = re.search(action_pattern, text, re.IGNORECASE)
        if not action_match:
            return None
        
        tool_name = action_match.group(1)
        
        # Look for arguments
        args_match = re.search(args_pattern, text, re.IGNORECASE | re.DOTALL)
        if args_match:
            try:
                arguments = json.loads(args_match.group(1))
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract simple key-value pairs
                arguments = {}
        else:
            arguments = {}
        
        return {
            "tool": tool_name,
            "arguments": arguments
        }


class ChainOfThoughtReasoning(ReasoningPattern):
    """
    Chain of Thought reasoning pattern.
    
    Encourages step-by-step thinking before providing answers.
    """
    
    async def execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> str:
        """Execute Chain of Thought reasoning."""
        # Load conversation history
        messages = await self._load_conversation_history(session_id)
        
        # Create CoT-enhanced system message
        cot_instruction = f"""{instruction}

When responding, think through the problem step by step:
1. First, analyze what is being asked
2. Break down the problem into smaller parts
3. Work through each part systematically
4. Combine your thinking to reach a conclusion

Show your reasoning process before providing your final answer."""
        
        messages[0].content = cot_instruction
        
        # Add user message
        messages.append(LLMMessage(role="user", content=message))
        await self._save_to_memory(session_id, "user", message)
        
        # Get LLM response
        response = await self.llm_manager.chat(messages, **kwargs)
        
        # Save assistant response
        await self._save_to_memory(session_id, "assistant", response.content)
        
        return response.content
    
    async def stream_execute(
        self,
        instruction: str,
        message: str,
        session_id: str,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Execute Chain of Thought reasoning with streaming."""
        # Load conversation history
        messages = await self._load_conversation_history(session_id)
        
        # Create CoT-enhanced system message
        cot_instruction = f"""{instruction}

When responding, think through the problem step by step:
1. First, analyze what is being asked
2. Break down the problem into smaller parts  
3. Work through each part systematically
4. Combine your thinking to reach a conclusion

Show your reasoning process before providing your final answer."""
        
        messages[0].content = cot_instruction
        
        # Add user message
        messages.append(LLMMessage(role="user", content=message))
        await self._save_to_memory(session_id, "user", message)
        
        # Stream LLM response
        full_response = ""
        async for chunk in self.llm_manager.stream_chat(messages, **kwargs):
            full_response += chunk
            yield chunk
        
        # Save complete response
        await self._save_to_memory(session_id, "assistant", full_response)