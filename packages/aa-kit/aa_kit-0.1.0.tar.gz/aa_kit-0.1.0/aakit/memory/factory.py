"""
Memory Factory

Factory for creating memory backend instances from configuration.
"""

from typing import Any, Dict, Optional, Union
from urllib.parse import urlparse

from .backends import MemoryBackend, InMemoryBackend, RedisBackend, SQLiteBackend
from ..core.exceptions import ConfigurationError


class MemoryFactory:
    """Factory for creating memory backend instances."""
    
    @classmethod
    async def create(
        cls,
        config: Union[str, Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> MemoryBackend:
        """
        Create a memory backend from configuration.
        
        Args:
            config: Memory configuration (URL string or dict)
            session_id: Optional session ID for context
            
        Returns:
            Configured memory backend instance
            
        Examples:
            # In-memory (for development)
            backend = await MemoryFactory.create("memory://")
            
            # Redis
            backend = await MemoryFactory.create("redis://localhost:6379")
            
            # SQLite
            backend = await MemoryFactory.create("sqlite:///path/to/db.sqlite")
            
            # Configuration dict
            backend = await MemoryFactory.create({
                "type": "redis",
                "host": "localhost", 
                "port": 6379,
                "ttl": 3600
            })
        """
        if isinstance(config, str):
            return await cls._create_from_url(config)
        elif isinstance(config, dict):
            return await cls._create_from_dict(config)
        else:
            raise ConfigurationError(
                f"Invalid memory configuration type: {type(config)}. "
                "Expected string URL or dictionary."
            )
    
    @classmethod
    async def _create_from_url(cls, url: str) -> MemoryBackend:
        """Create backend from URL string."""
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        
        if scheme == "memory":
            return InMemoryBackend()
        
        elif scheme == "redis":
            return RedisBackend(redis_url=url)
        
        elif scheme == "sqlite":
            # Extract path from URL
            if parsed.path:
                db_path = parsed.path[1:]  # Remove leading slash
            else:
                db_path = "agentz_memory.db"
            
            return SQLiteBackend(db_path=db_path)
        
        else:
            raise ConfigurationError(
                f"Unsupported memory backend scheme: {scheme}. "
                "Supported schemes: memory, redis, sqlite"
            )
    
    @classmethod
    async def _create_from_dict(cls, config: Dict[str, Any]) -> MemoryBackend:
        """Create backend from configuration dictionary."""
        backend_type = config.get("type", "memory").lower()
        
        if backend_type == "memory":
            return InMemoryBackend()
        
        elif backend_type == "redis":
            # Build Redis URL from components
            host = config.get("host", "localhost")
            port = config.get("port", 6379)
            db = config.get("db", 0)
            password = config.get("password")
            
            redis_url = f"redis://"
            if password:
                redis_url += f":{password}@"
            redis_url += f"{host}:{port}/{db}"
            
            return RedisBackend(
                redis_url=redis_url,
                key_prefix=config.get("key_prefix", "agentz:memory:"),
                ttl=config.get("ttl")
            )
        
        elif backend_type == "sqlite":
            return SQLiteBackend(
                db_path=config.get("db_path", "agentz_memory.db")
            )
        
        else:
            raise ConfigurationError(
                f"Unsupported memory backend type: {backend_type}. "
                "Supported types: memory, redis, sqlite"
            )
    
    @classmethod
    def get_supported_backends(cls) -> Dict[str, str]:
        """Get list of supported memory backends."""
        backends = {
            "memory": "In-memory storage (development only)",
            "sqlite": "SQLite database (local persistence)"
        }
        
        # Check if Redis is available
        try:
            import redis
            backends["redis"] = "Redis (production-ready)"
        except ImportError:
            pass
        
        return backends
    
    @classmethod
    def validate_config(cls, config: Union[str, Dict[str, Any]]) -> bool:
        """
        Validate memory configuration without creating the backend.
        
        Args:
            config: Memory configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            if isinstance(config, str):
                parsed = urlparse(config)
                scheme = parsed.scheme.lower()
                
                if scheme not in ["memory", "redis", "sqlite"]:
                    raise ConfigurationError(f"Unsupported scheme: {scheme}")
                
                # Additional validation for specific schemes
                if scheme == "redis" and not parsed.netloc:
                    raise ConfigurationError("Redis URL must include host")
                
            elif isinstance(config, dict):
                backend_type = config.get("type", "memory").lower()
                
                if backend_type not in ["memory", "redis", "sqlite"]:
                    raise ConfigurationError(f"Unsupported backend type: {backend_type}")
                
                # Type-specific validation
                if backend_type == "redis":
                    if "host" in config and not isinstance(config["host"], str):
                        raise ConfigurationError("Redis host must be a string")
                    
                    if "port" in config and not isinstance(config["port"], int):
                        raise ConfigurationError("Redis port must be an integer")
                
                elif backend_type == "sqlite":
                    if "db_path" in config and not isinstance(config["db_path"], str):
                        raise ConfigurationError("SQLite db_path must be a string")
            
            else:
                raise ConfigurationError(
                    f"Invalid configuration type: {type(config)}"
                )
            
            return True
            
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(f"Configuration validation failed: {str(e)}")


# Convenience functions

async def create_memory(
    config: Union[str, Dict[str, Any]],
    session_id: Optional[str] = None
) -> MemoryBackend:
    """Convenience function to create memory backend."""
    return await MemoryFactory.create(config, session_id)


async def create_in_memory() -> InMemoryBackend:
    """Create in-memory backend."""
    return InMemoryBackend()


async def create_redis(
    url: str = "redis://localhost:6379",
    ttl: Optional[int] = None
) -> RedisBackend:
    """Create Redis backend."""
    return RedisBackend(redis_url=url, ttl=ttl)


async def create_sqlite(db_path: str = "agentz_memory.db") -> SQLiteBackend:
    """Create SQLite backend."""
    return SQLiteBackend(db_path=db_path)