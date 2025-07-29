"""
AA Kit Core Module

Production-grade components for building reliable AI agents.
"""

from .agent import Agent, AgentConfig, create_agent
from .exceptions import (
    AAKitError,
    ConfigurationError,
    ModelNotAvailableError,
    LLMError,
    ToolError,
    MemoryError,
    ReasoningError,
    MCPError
)
from .config import ProductionConfig, get_production_config, set_production_config

# Production subsystems - imported lazily when needed
__all__ = [
    # Core agent
    'Agent',
    'AgentConfig',
    'create_agent',
    
    # Exceptions
    'AAKitError',
    'ConfigurationError',
    'ModelNotAvailableError',
    'LLMError',
    'ToolError',
    'MemoryError',
    'ReasoningError',
    'MCPError',
    
    # Configuration
    'ProductionConfig',
    'get_production_config',
    'set_production_config'
]