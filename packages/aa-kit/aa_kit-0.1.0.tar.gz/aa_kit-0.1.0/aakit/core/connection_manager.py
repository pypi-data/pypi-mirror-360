"""
Enterprise-grade connection pooling for AA Kit

Provides HTTP connection pooling, session management, and resource optimization
for all external API calls (LLM providers, MCP servers, etc.)
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional, Any, AsyncIterator
from dataclasses import dataclass, field

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector


logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """Configuration for connection pools."""
    
    # Connection limits
    total_connections: int = 100
    connections_per_host: int = 30
    
    # Timeouts (in seconds)
    total_timeout: float = 60.0
    connect_timeout: float = 10.0
    read_timeout: float = 50.0
    
    # Keep-alive settings
    keepalive_timeout: float = 30.0
    keepalive_expiry: float = 3600.0  # 1 hour
    
    # Retry and backoff
    enable_retries: bool = True
    max_retries: int = 3
    backoff_factor: float = 0.5
    
    # SSL/TLS settings
    verify_ssl: bool = True
    ssl_timeout: float = 10.0
    
    # Performance tuning
    enable_compression: bool = True
    enable_cookies: bool = False
    raise_for_status: bool = False
    
    # Connection pool cleanup
    cleanup_interval: float = 60.0  # Cleanup every minute
    max_idle_time: float = 300.0    # 5 minutes idle timeout


class ConnectionManager:
    """
    Enterprise-grade HTTP connection manager with pooling, timeouts, and resource management.
    
    Features:
    - Per-host connection pooling with limits
    - Automatic connection cleanup and recycling
    - Comprehensive timeout management
    - SSL/TLS optimization
    - Connection health monitoring
    - Resource usage tracking
    """
    
    def __init__(self, config: Optional[ConnectionPoolConfig] = None):
        self.config = config or ConnectionPoolConfig()
        self._sessions: Dict[str, ClientSession] = {}
        self._session_stats: Dict[str, Dict[str, Any]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._closed = False
        
        # Initialize cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task for connection cleanup."""
        if not self._cleanup_task or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background loop for cleaning up idle connections."""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_idle_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Connection cleanup error: {e}")
    
    async def _cleanup_idle_sessions(self):
        """Clean up idle or expired sessions."""
        current_time = time.time()
        sessions_to_close = []
        
        for session_key, stats in self._session_stats.items():
            last_used = stats.get('last_used', 0)
            if current_time - last_used > self.config.max_idle_time:
                sessions_to_close.append(session_key)
        
        for session_key in sessions_to_close:
            await self._close_session(session_key)
            logger.debug(f"Closed idle session: {session_key}")
    
    def _create_connector(self) -> TCPConnector:
        """Create optimized TCP connector for the session."""
        return TCPConnector(
            limit=self.config.total_connections,
            limit_per_host=self.config.connections_per_host,
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=self.config.keepalive_timeout,
            enable_cleanup_closed=True,
            verify_ssl=self.config.verify_ssl,
        )
    
    def _create_timeout(self) -> ClientTimeout:
        """Create timeout configuration for requests."""
        return ClientTimeout(
            total=self.config.total_timeout,
            connect=self.config.connect_timeout,
            sock_read=self.config.read_timeout,
        )
    
    def _get_session_key(self, base_url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """Generate unique session key based on base URL and auth headers."""
        # Include auth headers in session key for isolation
        auth_hash = ""
        if headers:
            auth_keys = {'authorization', 'x-api-key', 'anthropic-version'}
            auth_headers = {k: v for k, v in headers.items() if k.lower() in auth_keys}
            if auth_headers:
                auth_hash = str(hash(frozenset(auth_headers.items())))
        
        return f"{base_url}:{auth_hash}" if auth_hash else base_url
    
    async def get_session(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        **session_kwargs
    ) -> ClientSession:
        """
        Get or create a pooled session for the given base URL.
        
        Args:
            base_url: Base URL for the session
            headers: Default headers for the session
            **session_kwargs: Additional session parameters
            
        Returns:
            Configured ClientSession instance
        """
        if self._closed:
            raise RuntimeError("ConnectionManager is closed")
        
        session_key = self._get_session_key(base_url, headers)
        
        # Check if we have an existing session
        if session_key in self._sessions:
            session = self._sessions[session_key]
            if not session.closed:
                # Update last used time
                self._session_stats[session_key]['last_used'] = time.time()
                self._session_stats[session_key]['requests_count'] += 1
                return session
            else:
                # Session was closed, remove it
                await self._close_session(session_key)
        
        # Create new session
        session = await self._create_session(base_url, headers, **session_kwargs)
        self._sessions[session_key] = session
        self._session_stats[session_key] = {
            'created_at': time.time(),
            'last_used': time.time(),
            'requests_count': 1,
            'base_url': base_url
        }
        
        logger.debug(f"Created new session for {base_url}")
        return session
    
    async def _create_session(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        **session_kwargs
    ) -> ClientSession:
        """Create a new configured session."""
        # Merge default headers with provided headers
        default_headers = {
            'User-Agent': 'AA Kit/1.0 (Connection Pool)',
        }
        if headers:
            default_headers.update(headers)
        
        # Session configuration
        session_config = {
            'base_url': base_url,
            'headers': default_headers,
            'timeout': self._create_timeout(),
            'connector': self._create_connector(),
            'raise_for_status': self.config.raise_for_status,
            'cookie_jar': aiohttp.CookieJar() if self.config.enable_cookies else None,
        }
        
        # Merge with additional kwargs
        session_config.update(session_kwargs)
        
        return aiohttp.ClientSession(**session_config)
    
    async def _close_session(self, session_key: str):
        """Close and remove a specific session."""
        if session_key in self._sessions:
            session = self._sessions[session_key]
            if not session.closed:
                await session.close()
            del self._sessions[session_key]
            del self._session_stats[session_key]
    
    @asynccontextmanager
    async def request(
        self,
        method: str,
        url: str,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        """
        Make an HTTP request using pooled connections.
        
        Args:
            method: HTTP method
            url: Request URL (relative to base_url)
            base_url: Base URL for the service
            headers: Request headers
            **kwargs: Additional request parameters
            
        Yields:
            aiohttp.ClientResponse object
        """
        session = await self.get_session(base_url, headers)
        
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                yield response
        except Exception as e:
            # Log request failure but don't close session (might be temporary)
            logger.debug(f"Request failed for {method} {url}: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        total_sessions = len(self._sessions)
        active_sessions = sum(1 for s in self._sessions.values() if not s.closed)
        
        stats = {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'config': {
                'total_connections': self.config.total_connections,
                'connections_per_host': self.config.connections_per_host,
                'total_timeout': self.config.total_timeout,
            },
            'sessions': {}
        }
        
        # Add per-session stats
        for key, session_stats in self._session_stats.items():
            stats['sessions'][key] = {
                'base_url': session_stats['base_url'],
                'requests_count': session_stats['requests_count'],
                'age_seconds': time.time() - session_stats['created_at'],
                'idle_seconds': time.time() - session_stats['last_used'],
                'is_closed': self._sessions[key].closed if key in self._sessions else True
            }
        
        return stats
    
    async def close(self):
        """Close all sessions and cleanup resources."""
        if self._closed:
            return
        
        self._closed = True
        
        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all sessions
        close_tasks = []
        for session_key in list(self._sessions.keys()):
            task = asyncio.create_task(self._close_session(session_key))
            close_tasks.append(task)
        
        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)
        
        logger.info("ConnectionManager closed successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global connection manager instance
_global_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the global connection manager instance."""
    global _global_connection_manager
    
    if _global_connection_manager is None or _global_connection_manager._closed:
        _global_connection_manager = ConnectionManager()
    
    return _global_connection_manager


async def close_global_connection_manager():
    """Close the global connection manager."""
    global _global_connection_manager
    
    if _global_connection_manager and not _global_connection_manager._closed:
        await _global_connection_manager.close()
        _global_connection_manager = None