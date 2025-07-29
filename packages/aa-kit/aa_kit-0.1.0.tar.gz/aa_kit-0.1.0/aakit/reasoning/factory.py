"""
Reasoning Factory

Factory for creating reasoning pattern instances.
"""

from typing import Optional, TYPE_CHECKING

from .patterns import ReasoningPattern, SimpleReasoning, ReActReasoning, ChainOfThoughtReasoning
from ..core.exceptions import ConfigurationError

if TYPE_CHECKING:
    from ..llm.manager import LLMManager
    from ..tools.registry import ToolRegistry
    from ..memory.backends import MemoryBackend


class ReasoningFactory:
    """Factory for creating reasoning pattern instances."""
    
    AVAILABLE_PATTERNS = {
        "simple": SimpleReasoning,
        "react": ReActReasoning,
        "chain_of_thought": ChainOfThoughtReasoning,
        "cot": ChainOfThoughtReasoning,  # Alias for chain_of_thought
    }
    
    @classmethod
    def create(
        cls,
        pattern: str,
        llm_manager: 'LLMManager',
        tool_registry: Optional['ToolRegistry'] = None,
        memory: Optional['MemoryBackend'] = None,
        **kwargs
    ) -> ReasoningPattern:
        """
        Create a reasoning pattern instance.
        
        Args:
            pattern: Type of reasoning pattern to create
            llm_manager: LLM manager for generating responses
            tool_registry: Registry of available tools
            memory: Memory backend for conversation history
            **kwargs: Additional arguments for the pattern
            
        Returns:
            Configured reasoning pattern instance
            
        Raises:
            ConfigurationError: If pattern type is not supported
        """
        pattern_name = pattern.lower().strip()
        
        if pattern_name not in cls.AVAILABLE_PATTERNS:
            raise ConfigurationError(
                f"Unsupported reasoning pattern: {pattern}. "
                f"Available patterns: {', '.join(cls.AVAILABLE_PATTERNS.keys())}"
            )
        
        pattern_class = cls.AVAILABLE_PATTERNS[pattern_name]
        
        # Create instance with appropriate arguments
        if pattern_name == "react":
            # ReAct reasoning may have additional configuration
            max_iterations = kwargs.get("max_iterations", 10)
            return pattern_class(
                llm_manager=llm_manager,
                tool_registry=tool_registry,
                memory=memory,
                max_iterations=max_iterations
            )
        else:
            # Other patterns use standard initialization
            return pattern_class(
                llm_manager=llm_manager,
                tool_registry=tool_registry,
                memory=memory
            )
    
    @classmethod
    def get_available_patterns(cls) -> dict:
        """
        Get information about available reasoning patterns.
        
        Returns:
            Dictionary mapping pattern names to descriptions
        """
        return {
            "simple": {
                "name": "Simple Reasoning",
                "description": "Direct LLM calls without tools. Best for basic conversation.",
                "supports_tools": False,
                "supports_streaming": True
            },
            "react": {
                "name": "ReAct (Reasoning + Acting)",
                "description": "Think → Act → Observe loop for tool-based problem solving.",
                "supports_tools": True,
                "supports_streaming": True
            },
            "chain_of_thought": {
                "name": "Chain of Thought",
                "description": "Step-by-step reasoning before providing answers.",
                "supports_tools": False,
                "supports_streaming": True
            },
            "cot": {
                "name": "Chain of Thought (alias)",
                "description": "Alias for chain_of_thought pattern.",
                "supports_tools": False,
                "supports_streaming": True
            }
        }
    
    @classmethod
    def get_recommended_pattern(
        cls,
        has_tools: bool = False,
        task_complexity: str = "simple"
    ) -> str:
        """
        Get recommended reasoning pattern based on context.
        
        Args:
            has_tools: Whether tools are available
            task_complexity: Complexity level ("simple", "medium", "complex")
            
        Returns:
            Recommended pattern name
        """
        if has_tools:
            # If tools are available, ReAct is usually best
            return "react"
        
        if task_complexity in ["medium", "complex"]:
            # For complex tasks without tools, use chain of thought
            return "chain_of_thought"
        
        # For simple tasks, basic reasoning is sufficient
        return "simple"
    
    @classmethod
    def validate_pattern(cls, pattern: str) -> bool:
        """
        Validate if a reasoning pattern is supported.
        
        Args:
            pattern: Pattern name to validate
            
        Returns:
            True if pattern is supported
        """
        return pattern.lower().strip() in cls.AVAILABLE_PATTERNS


# Convenience functions

def create_simple_reasoning(
    llm_manager: 'LLMManager',
    memory: Optional['MemoryBackend'] = None
) -> SimpleReasoning:
    """Create simple reasoning pattern."""
    return SimpleReasoning(llm_manager=llm_manager, memory=memory)


def create_react_reasoning(
    llm_manager: 'LLMManager',
    tool_registry: 'ToolRegistry',
    memory: Optional['MemoryBackend'] = None,
    max_iterations: int = 10
) -> ReActReasoning:
    """Create ReAct reasoning pattern."""
    return ReActReasoning(
        llm_manager=llm_manager,
        tool_registry=tool_registry,
        memory=memory,
        max_iterations=max_iterations
    )


def create_cot_reasoning(
    llm_manager: 'LLMManager',
    memory: Optional['MemoryBackend'] = None
) -> ChainOfThoughtReasoning:
    """Create Chain of Thought reasoning pattern."""
    return ChainOfThoughtReasoning(llm_manager=llm_manager, memory=memory)