"""Configuration module for AA Kit with optional pydantic support"""

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    # Fallback to dataclasses if pydantic is not available
    from dataclasses import dataclass, field
    from typing import Optional, Dict, Any


if HAS_PYDANTIC:
    class AgentConfig(BaseModel):
        """Agent configuration with pydantic validation"""
        temperature: float = Field(default=0.7, ge=0, le=2)
        max_tokens: Optional[int] = Field(default=None, gt=0)
        timeout: int = Field(default=30, gt=0)
        retry_max: int = Field(default=3, ge=0)
        retry_delay: float = Field(default=1.0, gt=0)
        cache_ttl: int = Field(default=3600, ge=0)
        rate_limit: Optional[Dict[str, Any]] = None
        
        class Config:
            extra = "allow"
else:
    @dataclass
    class AgentConfig:
        """Agent configuration with dataclasses fallback"""
        temperature: float = 0.7
        max_tokens: Optional[int] = None
        timeout: int = 30
        retry_max: int = 3
        retry_delay: float = 1.0
        cache_ttl: int = 3600
        rate_limit: Optional[Dict[str, Any]] = None
        
        def __post_init__(self):
            # Basic validation
            if not 0 <= self.temperature <= 2:
                raise ValueError("temperature must be between 0 and 2")
            if self.timeout <= 0:
                raise ValueError("timeout must be positive")
            if self.retry_max < 0:
                raise ValueError("retry_max must be non-negative")
            if self.retry_delay <= 0:
                raise ValueError("retry_delay must be positive")
            if self.cache_ttl < 0:
                raise ValueError("cache_ttl must be non-negative")


def get_config_class():
    """Get the appropriate config class based on available dependencies"""
    return AgentConfig