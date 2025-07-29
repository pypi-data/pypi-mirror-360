"""
Comprehensive timeout management for AA Kit

Provides configurable timeouts, deadline management, and timeout context propagation
for all async operations in the framework.
"""

import asyncio
import functools
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar, Union
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TimeoutType(Enum):
    """Types of timeout operations."""
    REQUEST = "request"
    OPERATION = "operation"
    TOTAL = "total"
    IDLE = "idle"


@dataclass
class TimeoutConfig:
    """Comprehensive timeout configuration."""
    
    # Request-level timeouts
    llm_request_timeout: float = 60.0
    tool_execution_timeout: float = 30.0
    memory_operation_timeout: float = 5.0
    mcp_request_timeout: float = 45.0
    
    # Operation-level timeouts  
    agent_chat_timeout: float = 120.0
    reasoning_timeout: float = 180.0
    multi_agent_timeout: float = 300.0
    
    # Connection timeouts
    connect_timeout: float = 10.0
    read_timeout: float = 50.0
    write_timeout: float = 30.0
    
    # Idle timeouts
    idle_timeout: float = 300.0
    session_timeout: float = 3600.0
    
    # Grace periods
    shutdown_grace_period: float = 30.0
    cleanup_grace_period: float = 10.0
    
    # Retry timeouts
    retry_base_timeout: float = 1.0
    retry_max_timeout: float = 60.0
    retry_multiplier: float = 2.0
    
    # Debugging
    enable_timeout_logging: bool = True
    log_slow_operations: bool = True
    slow_operation_threshold: float = 5.0


class TimeoutError(Exception):
    """Enhanced timeout error with context."""
    
    def __init__(
        self,
        message: str,
        timeout_duration: float,
        operation: str,
        timeout_type: TimeoutType = TimeoutType.OPERATION,
        context: Optional[Dict[str, Any]] = None
    ):
        self.timeout_duration = timeout_duration
        self.operation = operation
        self.timeout_type = timeout_type
        self.context = context or {}
        
        super().__init__(
            f"{message} (operation: {operation}, timeout: {timeout_duration}s, "
            f"type: {timeout_type.value})"
        )


class TimeoutContext:
    """Context manager for tracking nested timeout operations."""
    
    def __init__(self, operation: str, timeout: float, timeout_type: TimeoutType):
        self.operation = operation
        self.timeout = timeout
        self.timeout_type = timeout_type
        self.start_time = 0.0
        self.end_time = 0.0
        self.parent: Optional['TimeoutContext'] = None
        self.children: list['TimeoutContext'] = []
    
    @property
    def duration(self) -> float:
        """Get operation duration."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time if self.start_time else 0.0
    
    @property
    def remaining_time(self) -> float:
        """Get remaining time before timeout."""
        elapsed = self.duration
        return max(0.0, self.timeout - elapsed)
    
    @property
    def is_expired(self) -> bool:
        """Check if timeout has expired."""
        return self.duration >= self.timeout
    
    def add_child(self, child: 'TimeoutContext'):
        """Add child timeout context."""
        child.parent = self
        self.children.append(child)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/debugging."""
        return {
            'operation': self.operation,
            'timeout': self.timeout,
            'type': self.timeout_type.value,
            'duration': self.duration,
            'remaining': self.remaining_time,
            'expired': self.is_expired,
            'children_count': len(self.children)
        }


class TimeoutManager:
    """
    Enterprise-grade timeout management with context tracking and hierarchical timeouts.
    
    Features:
    - Configurable timeout policies
    - Nested timeout context tracking
    - Automatic timeout propagation
    - Performance monitoring
    - Graceful timeout handling
    """
    
    def __init__(self, config: Optional[TimeoutConfig] = None):
        self.config = config or TimeoutConfig()
        self._active_contexts: Dict[str, TimeoutContext] = {}
        self._context_stack: list[TimeoutContext] = []
        self._stats = {
            'total_operations': 0,
            'timed_out_operations': 0,
            'slow_operations': 0,
            'avg_duration': 0.0
        }
    
    def get_timeout(self, operation: str, timeout_type: TimeoutType) -> float:
        """Get timeout value for a specific operation and type."""
        timeout_map = {
            # LLM operations
            ('llm_chat', TimeoutType.REQUEST): self.config.llm_request_timeout,
            ('llm_stream', TimeoutType.REQUEST): self.config.llm_request_timeout,
            
            # Tool operations
            ('tool_execute', TimeoutType.OPERATION): self.config.tool_execution_timeout,
            
            # Memory operations
            ('memory_get', TimeoutType.OPERATION): self.config.memory_operation_timeout,
            ('memory_set', TimeoutType.OPERATION): self.config.memory_operation_timeout,
            ('memory_clear', TimeoutType.OPERATION): self.config.memory_operation_timeout,
            
            # Agent operations
            ('agent_chat', TimeoutType.TOTAL): self.config.agent_chat_timeout,
            ('agent_reasoning', TimeoutType.OPERATION): self.config.reasoning_timeout,
            
            # MCP operations
            ('mcp_request', TimeoutType.REQUEST): self.config.mcp_request_timeout,
            
            # Multi-agent operations
            ('multi_agent', TimeoutType.TOTAL): self.config.multi_agent_timeout,
        }
        
        # Try exact match first
        timeout = timeout_map.get((operation, timeout_type))
        if timeout is not None:
            return timeout
        
        # Fall back to type-based defaults
        type_defaults = {
            TimeoutType.REQUEST: 60.0,
            TimeoutType.OPERATION: 30.0,
            TimeoutType.TOTAL: 120.0,
            TimeoutType.IDLE: self.config.idle_timeout
        }
        
        return type_defaults.get(timeout_type, 30.0)
    
    @asynccontextmanager
    async def timeout_context(
        self,
        operation: str,
        timeout: Optional[float] = None,
        timeout_type: TimeoutType = TimeoutType.OPERATION,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Create a timeout context for an operation.
        
        Args:
            operation: Name of the operation
            timeout: Timeout duration (auto-detected if None)
            timeout_type: Type of timeout
            context: Additional context for debugging
        """
        if timeout is None:
            timeout = self.get_timeout(operation, timeout_type)
        
        # Adjust timeout based on parent context
        if self._context_stack:
            parent = self._context_stack[-1]
            remaining = parent.remaining_time
            if remaining < timeout:
                timeout = max(1.0, remaining - 1.0)  # Leave 1s buffer
        
        timeout_context = TimeoutContext(operation, timeout, timeout_type)
        timeout_context.start_time = time.time()
        
        # Add to parent if exists
        if self._context_stack:
            self._context_stack[-1].add_child(timeout_context)
        
        self._context_stack.append(timeout_context)
        context_id = f"{operation}_{id(timeout_context)}"
        self._active_contexts[context_id] = timeout_context
        
        try:
            if self.config.enable_timeout_logging:
                logger.debug(f"Starting operation '{operation}' with {timeout}s timeout")
            
            yield timeout_context
            
        finally:
            timeout_context.end_time = time.time()
            duration = timeout_context.duration
            
            # Update statistics
            self._update_stats(timeout_context)
            
            # Log completion
            if self.config.enable_timeout_logging:
                status = "TIMEOUT" if timeout_context.is_expired else "COMPLETED"
                logger.debug(f"Operation '{operation}' {status} in {duration:.2f}s")
            
            # Log slow operations
            if (self.config.log_slow_operations and 
                duration > self.config.slow_operation_threshold):
                logger.warning(
                    f"Slow operation detected: '{operation}' took {duration:.2f}s "
                    f"(threshold: {self.config.slow_operation_threshold}s)"
                )
            
            # Cleanup
            self._context_stack.pop()
            del self._active_contexts[context_id]
    
    def _update_stats(self, context: TimeoutContext):
        """Update performance statistics."""
        self._stats['total_operations'] += 1
        
        if context.is_expired:
            self._stats['timed_out_operations'] += 1
        
        if context.duration > self.config.slow_operation_threshold:
            self._stats['slow_operations'] += 1
        
        # Update average duration
        total = self._stats['total_operations']
        current_avg = self._stats['avg_duration']
        new_avg = (current_avg * (total - 1) + context.duration) / total
        self._stats['avg_duration'] = new_avg
    
    async def with_timeout(
        self,
        coro: Awaitable[T],
        operation: str,
        timeout: Optional[float] = None,
        timeout_type: TimeoutType = TimeoutType.OPERATION,
        context: Optional[Dict[str, Any]] = None
    ) -> T:
        """
        Execute a coroutine with timeout management.
        
        Args:
            coro: Coroutine to execute
            operation: Operation name for logging
            timeout: Timeout duration
            timeout_type: Type of timeout
            context: Additional context
            
        Returns:
            Result of the coroutine
            
        Raises:
            TimeoutError: If operation times out
        """
        async with self.timeout_context(operation, timeout, timeout_type, context) as ctx:
            try:
                return await asyncio.wait_for(coro, timeout=ctx.timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(
                    f"Operation '{operation}' timed out",
                    ctx.timeout,
                    operation,
                    timeout_type,
                    context
                )
    
    def timeout_decorator(
        self,
        operation: Optional[str] = None,
        timeout: Optional[float] = None,
        timeout_type: TimeoutType = TimeoutType.OPERATION
    ):
        """
        Decorator to add timeout management to async functions.
        
        Args:
            operation: Operation name (uses function name if None)
            timeout: Timeout duration
            timeout_type: Type of timeout
        """
        def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
            op_name = operation or func.__name__
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                return await self.with_timeout(
                    func(*args, **kwargs),
                    op_name,
                    timeout,
                    timeout_type
                )
            
            return wrapper
        return decorator
    
    def get_current_context(self) -> Optional[TimeoutContext]:
        """Get the current timeout context."""
        return self._context_stack[-1] if self._context_stack else None
    
    def get_remaining_time(self) -> Optional[float]:
        """Get remaining time in current context."""
        context = self.get_current_context()
        return context.remaining_time if context else None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timeout management statistics."""
        total_ops = self._stats['total_operations']
        timeout_rate = (self._stats['timed_out_operations'] / total_ops * 100) if total_ops > 0 else 0
        slow_rate = (self._stats['slow_operations'] / total_ops * 100) if total_ops > 0 else 0
        
        return {
            'total_operations': total_ops,
            'timeout_rate_percent': round(timeout_rate, 2),
            'slow_operation_rate_percent': round(slow_rate, 2),
            'average_duration_seconds': round(self._stats['avg_duration'], 3),
            'active_contexts': len(self._active_contexts),
            'context_stack_depth': len(self._context_stack),
            'config': {
                'llm_request_timeout': self.config.llm_request_timeout,
                'agent_chat_timeout': self.config.agent_chat_timeout,
                'slow_operation_threshold': self.config.slow_operation_threshold
            }
        }
    
    async def cancel_all_operations(self, grace_period: Optional[float] = None):
        """Cancel all active operations with grace period."""
        if not self._active_contexts:
            return
        
        grace = grace_period or self.config.shutdown_grace_period
        logger.info(f"Cancelling {len(self._active_contexts)} active operations with {grace}s grace period")
        
        # Wait for grace period
        if grace > 0:
            await asyncio.sleep(grace)
        
        # Force cleanup remaining contexts
        remaining = len(self._active_contexts)
        if remaining > 0:
            logger.warning(f"Force-cancelling {remaining} operations that exceeded grace period")
            self._active_contexts.clear()
            self._context_stack.clear()


# Global timeout manager instance
_global_timeout_manager: Optional[TimeoutManager] = None


def get_timeout_manager() -> TimeoutManager:
    """Get or create the global timeout manager instance."""
    global _global_timeout_manager
    
    if _global_timeout_manager is None:
        _global_timeout_manager = TimeoutManager()
    
    return _global_timeout_manager


# Convenience functions for common timeout patterns
async def with_timeout(
    coro: Awaitable[T],
    timeout: float,
    operation: str = "async_operation"
) -> T:
    """Simple timeout wrapper for coroutines."""
    manager = get_timeout_manager()
    return await manager.with_timeout(coro, operation, timeout)


def timeout(
    duration: Optional[float] = None,
    operation: Optional[str] = None,
    timeout_type: TimeoutType = TimeoutType.OPERATION
):
    """Decorator for adding timeouts to async functions."""
    manager = get_timeout_manager()
    return manager.timeout_decorator(operation, duration, timeout_type)