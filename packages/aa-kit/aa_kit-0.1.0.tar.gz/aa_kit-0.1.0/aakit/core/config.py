"""
Production configuration for AA Kit

Provides centralized configuration for all production features.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ProductionConfig:
    """Configuration for production features in AA Kit."""
    
    # Feature toggles
    enable_connection_pooling: bool = True
    enable_timeout_handling: bool = True
    enable_rate_limiting: bool = True
    enable_response_caching: bool = True
    enable_retry_logic: bool = True
    enable_circuit_breaker: bool = True
    enable_resource_cleanup: bool = True
    enable_parallel_execution: bool = True
    enable_streaming: bool = True
    enable_observability: bool = True
    
    # Connection pooling settings
    connection_pool_size: int = 100
    connections_per_host: int = 30
    connection_timeout: float = 10.0
    
    # Timeout settings
    default_timeout: float = 60.0
    llm_request_timeout: float = 60.0
    tool_execution_timeout: float = 30.0
    agent_chat_timeout: float = 120.0
    
    # Rate limiting settings
    requests_per_minute: float = 600.0
    tokens_per_minute: float = 50000.0
    enable_adaptive_rate_limiting: bool = True
    
    # Caching settings
    cache_ttl: float = 3600.0  # 1 hour
    enable_semantic_caching: bool = True
    semantic_similarity_threshold: float = 0.85
    
    # Retry settings
    max_retry_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    enable_adaptive_retry: bool = True
    
    # Circuit breaker settings
    circuit_failure_threshold: int = 5
    circuit_timeout_duration: float = 60.0
    circuit_success_threshold: int = 3
    
    # Parallel execution settings
    max_concurrent_requests: int = 10
    max_concurrent_agents: int = 5
    max_concurrent_tools: int = 20
    
    # Streaming settings
    stream_buffer_size: int = 1000
    stream_chunk_size: int = 50
    
    # Observability settings
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    metrics_interval: float = 60.0
    
    # Provider-specific overrides
    provider_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def development(cls) -> 'ProductionConfig':
        """Create a development configuration with relaxed limits."""
        return cls(
            enable_rate_limiting=False,
            enable_circuit_breaker=False,
            enable_response_caching=False,
            connection_pool_size=10,
            max_concurrent_requests=50,
            enable_adaptive_rate_limiting=False,
            enable_adaptive_retry=False
        )
    
    @classmethod
    def testing(cls) -> 'ProductionConfig':
        """Create a testing configuration with minimal features."""
        return cls(
            enable_connection_pooling=False,
            enable_rate_limiting=False,
            enable_response_caching=False,
            enable_circuit_breaker=False,
            enable_observability=False,
            max_retry_attempts=1,
            default_timeout=5.0
        )
    
    @classmethod
    def production(cls) -> 'ProductionConfig':
        """Create a production configuration with all features enabled."""
        return cls()  # All defaults are production-ready
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'features': {
                'connection_pooling': self.enable_connection_pooling,
                'timeout_handling': self.enable_timeout_handling,
                'rate_limiting': self.enable_rate_limiting,
                'response_caching': self.enable_response_caching,
                'retry_logic': self.enable_retry_logic,
                'circuit_breaker': self.enable_circuit_breaker,
                'resource_cleanup': self.enable_resource_cleanup,
                'parallel_execution': self.enable_parallel_execution,
                'streaming': self.enable_streaming,
                'observability': self.enable_observability
            },
            'limits': {
                'connection_pool_size': self.connection_pool_size,
                'max_concurrent_requests': self.max_concurrent_requests,
                'requests_per_minute': self.requests_per_minute,
                'tokens_per_minute': self.tokens_per_minute
            },
            'timeouts': {
                'default': self.default_timeout,
                'llm_request': self.llm_request_timeout,
                'tool_execution': self.tool_execution_timeout,
                'agent_chat': self.agent_chat_timeout
            }
        }


# Global configuration instance
_global_config: Optional[ProductionConfig] = None


def get_production_config() -> ProductionConfig:
    """Get or create the global production configuration."""
    global _global_config
    
    if _global_config is None:
        _global_config = ProductionConfig()
    
    return _global_config


def set_production_config(config: ProductionConfig):
    """Set the global production configuration."""
    global _global_config
    _global_config = config