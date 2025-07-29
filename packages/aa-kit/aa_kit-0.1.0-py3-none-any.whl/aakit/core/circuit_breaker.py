"""
Enterprise-grade circuit breaker implementation for AA Kit

Implements the circuit breaker pattern with multiple states, failure tracking,
and automatic recovery for protecting against cascading failures.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class FailureType(Enum):
    """Types of failures for circuit breaker."""
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    SERVER_ERROR = "server_error"
    RATE_LIMIT = "rate_limit"
    UNKNOWN = "unknown"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    
    # Failure tracking
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_duration: float = 60.0
    
    # Request volume requirements
    minimum_requests: int = 10
    rolling_window_size: int = 100
    
    # Recovery settings
    half_open_max_calls: int = 5
    recovery_timeout: float = 30.0
    
    # Failure classification
    count_timeouts_as_failures: bool = True
    count_rate_limits_as_failures: bool = False
    
    # Advanced settings
    slow_call_threshold: float = 5.0  # Calls slower than this are failures
    slow_call_rate_threshold: float = 0.5  # 50% slow calls trigger open
    enable_automatic_transition: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    metrics_window_size: int = 1000


@dataclass
class CallResult:
    """Result of a circuit breaker call."""
    
    success: bool
    duration: float
    exception: Optional[Exception] = None
    failure_type: Optional[FailureType] = None
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_slow_call(self) -> bool:
        """Check if call was slow."""
        return self.duration > 5.0  # Default threshold


class CircuitBreakerMetrics:
    """Metrics collection for circuit breaker."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.calls: deque[CallResult] = deque(maxlen=window_size)
        
        # Summary statistics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.state_transitions = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
    
    def record_call(self, result: CallResult):
        """Record a call result."""
        self.calls.append(result)
        self.total_calls += 1
        
        if result.success:
            self.successful_calls += 1
            self.last_success_time = result.timestamp
        else:
            self.failed_calls += 1
            self.last_failure_time = result.timestamp
    
    def record_state_transition(self):
        """Record a state transition."""
        self.state_transitions += 1
    
    def get_recent_calls(self, count: int) -> List[CallResult]:
        """Get most recent calls."""
        return list(self.calls)[-count:] if count <= len(self.calls) else list(self.calls)
    
    def get_failure_rate(self, window_size: Optional[int] = None) -> float:
        """Get failure rate for recent calls."""
        recent_calls = self.get_recent_calls(window_size or len(self.calls))
        if not recent_calls:
            return 0.0
        
        failures = sum(1 for call in recent_calls if not call.success)
        return failures / len(recent_calls)
    
    def get_slow_call_rate(self, window_size: Optional[int] = None) -> float:
        """Get slow call rate for recent calls."""
        recent_calls = self.get_recent_calls(window_size or len(self.calls))
        if not recent_calls:
            return 0.0
        
        slow_calls = sum(1 for call in recent_calls if call.is_slow_call)
        return slow_calls / len(recent_calls)
    
    def get_average_duration(self, window_size: Optional[int] = None) -> float:
        """Get average call duration."""
        recent_calls = self.get_recent_calls(window_size or len(self.calls))
        if not recent_calls:
            return 0.0
        
        total_duration = sum(call.duration for call in recent_calls)
        return total_duration / len(recent_calls)
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary."""
        recent_calls = list(self.calls)
        
        return {
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0,
            'failure_rate': round(self.get_failure_rate() * 100, 2),
            'slow_call_rate': round(self.get_slow_call_rate() * 100, 2),
            'average_duration': round(self.get_average_duration(), 3),
            'state_transitions': self.state_transitions,
            'recent_calls_count': len(recent_calls),
            'last_failure_time': self.last_failure_time,
            'last_success_time': self.last_success_time
        }


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open."""
    
    def __init__(
        self,
        message: str,
        state: CircuitState,
        last_failure_time: Optional[float] = None,
        failure_count: int = 0
    ):
        self.state = state
        self.last_failure_time = last_failure_time
        self.failure_count = failure_count
        super().__init__(f"{message} (state: {state.value}, failures: {failure_count})")


class FailureClassifier:
    """Classifies exceptions into failure types."""
    
    def classify_exception(self, exception: Exception) -> FailureType:
        """Classify exception into failure type."""
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(exception, (ConnectionError, OSError)):
            return FailureType.CONNECTION_ERROR
        elif hasattr(exception, 'status_code'):
            # HTTP-like exception
            status_code = getattr(exception, 'status_code')
            if status_code == 429:
                return FailureType.RATE_LIMIT
            elif 500 <= status_code < 600:
                return FailureType.SERVER_ERROR
        
        return FailureType.UNKNOWN


class CircuitBreaker:
    """
    Enterprise-grade circuit breaker implementation.
    
    Implements the circuit breaker pattern to prevent cascading failures
    and provide fail-fast behavior when services are unavailable.
    
    Features:
    - Three states: CLOSED, OPEN, HALF_OPEN
    - Configurable failure thresholds and timeouts
    - Slow call detection and rate limiting
    - Comprehensive metrics and monitoring
    - Automatic recovery testing
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        
        # State management
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None
        self.last_state_transition = time.time()
        self.half_open_calls = 0
        self.consecutive_successes = 0
        self.consecutive_failures = 0
        
        # Metrics and monitoring
        self.metrics = CircuitBreakerMetrics(self.config.metrics_window_size)
        self.failure_classifier = FailureClassifier()
        
        # Thread safety
        self._lock = asyncio.Lock()
    
    async def _transition_to_state(self, new_state: CircuitState, reason: str = ""):
        """Transition to a new state."""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.last_state_transition = time.time()
            self.metrics.record_state_transition()
            
            # Reset counters on state change
            if new_state == CircuitState.HALF_OPEN:
                self.half_open_calls = 0
            elif new_state == CircuitState.CLOSED:
                self.consecutive_failures = 0
                self.consecutive_successes = 0
            
            logger.info(
                f"Circuit breaker '{self.name}' transitioned from {old_state.value} "
                f"to {new_state.value}. Reason: {reason}"
            )
    
    def _should_trip_circuit(self) -> bool:
        """Check if circuit should trip to OPEN state."""
        # Check if we have minimum required requests
        recent_calls = self.metrics.get_recent_calls(self.config.rolling_window_size)
        if len(recent_calls) < self.config.minimum_requests:
            return False
        
        # Check failure rate
        failure_rate = self.metrics.get_failure_rate(self.config.rolling_window_size)
        failure_threshold_rate = self.config.failure_threshold / self.config.rolling_window_size
        
        if failure_rate >= failure_threshold_rate:
            return True
        
        # Check slow call rate if enabled
        slow_call_rate = self.metrics.get_slow_call_rate(self.config.rolling_window_size)
        if slow_call_rate >= self.config.slow_call_rate_threshold:
            return True
        
        # Check consecutive failures
        if self.consecutive_failures >= self.config.failure_threshold:
            return True
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset from OPEN to HALF_OPEN."""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.last_failure_time is None:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.timeout_duration
    
    def _should_close_circuit(self) -> bool:
        """Check if circuit should close from HALF_OPEN to CLOSED."""
        return (self.state == CircuitState.HALF_OPEN and 
                self.consecutive_successes >= self.config.success_threshold)
    
    async def _handle_call_success(self, duration: float):
        """Handle successful call."""
        result = CallResult(success=True, duration=duration)
        self.metrics.record_call(result)
        
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        
        # Check for state transitions
        if self._should_close_circuit():
            await self._transition_to_state(
                CircuitState.CLOSED,
                f"Success threshold reached ({self.consecutive_successes})"
            )
    
    async def _handle_call_failure(self, exception: Exception, duration: float):
        """Handle failed call."""
        failure_type = self.failure_classifier.classify_exception(exception)
        
        # Determine if this failure should count
        should_count = True
        if (failure_type == FailureType.RATE_LIMIT and 
            not self.config.count_rate_limits_as_failures):
            should_count = False
        
        result = CallResult(
            success=False,
            duration=duration,
            exception=exception,
            failure_type=failure_type
        )
        self.metrics.record_call(result)
        
        if should_count:
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure_time = time.time()
            
            # Check if circuit should trip
            if self.state == CircuitState.CLOSED and self._should_trip_circuit():
                await self._transition_to_state(
                    CircuitState.OPEN,
                    f"Failure threshold exceeded ({self.consecutive_failures})"
                )
            elif self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open should return to open
                await self._transition_to_state(
                    CircuitState.OPEN,
                    "Failure during half-open state"
                )
    
    async def _can_execute(self) -> bool:
        """Check if call can be executed in current state."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if we should attempt reset
            if self._should_attempt_reset():
                await self._transition_to_state(
                    CircuitState.HALF_OPEN,
                    "Timeout duration elapsed, attempting reset"
                )
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self.half_open_calls < self.config.half_open_max_calls
        
        return False
    
    async def call(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerException: If circuit is open
            Original exception: If function fails
        """
        async with self._lock:
            if not await self._can_execute():
                raise CircuitBreakerException(
                    f"Circuit breaker '{self.name}' is OPEN",
                    self.state,
                    self.last_failure_time,
                    self.consecutive_failures
                )
            
            # Increment half-open call counter
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_calls += 1
        
        # Execute the function
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            async with self._lock:
                await self._handle_call_success(duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            async with self._lock:
                await self._handle_call_failure(e, duration)
            
            raise
    
    def call_decorator(self):
        """Decorator to wrap functions with circuit breaker."""
        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            async def wrapper(*args, **kwargs) -> Any:
                return await self.call(func, *args, **kwargs)
            return wrapper
        return decorator
    
    async def health_check(self, func: Callable[[], Awaitable[bool]]) -> bool:
        """
        Perform health check and potentially reset circuit.
        
        Args:
            func: Health check function that returns bool
            
        Returns:
            True if healthy, False otherwise
        """
        try:
            is_healthy = await func()
            if is_healthy and self.state == CircuitState.OPEN:
                async with self._lock:
                    await self._transition_to_state(
                        CircuitState.HALF_OPEN,
                        "Health check passed"
                    )
            return is_healthy
        except Exception as e:
            logger.warning(f"Health check failed for circuit '{self.name}': {e}")
            return False
    
    def force_state(self, state: CircuitState, reason: str = "Manual override"):
        """Force circuit to specific state (for testing/admin)."""
        asyncio.create_task(self._transition_to_state(state, reason))
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker statistics."""
        metrics_stats = self.metrics.get_stats_dict()
        
        return {
            'name': self.name,
            'state': self.state.value,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'half_open_calls': self.half_open_calls,
            'last_failure_time': self.last_failure_time,
            'last_state_transition': self.last_state_transition,
            'time_in_current_state': time.time() - self.last_state_transition,
            'metrics': metrics_stats,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'success_threshold': self.config.success_threshold,
                'timeout_duration': self.config.timeout_duration,
                'minimum_requests': self.config.minimum_requests,
                'half_open_max_calls': self.config.half_open_max_calls
            }
        }


class CircuitBreakerManager:
    """Manager for multiple circuit breakers."""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker by name."""
        async with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name, config)
            return self.circuit_breakers[name]
    
    async def call_through_circuit(
        self,
        circuit_name: str,
        func: Callable[..., Awaitable[Any]],
        *args,
        config: Optional[CircuitBreakerConfig] = None,
        **kwargs
    ) -> Any:
        """Execute function through named circuit breaker."""
        circuit = await self.get_circuit_breaker(circuit_name, config)
        return await circuit.call(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all circuit breakers."""
        return {
            name: circuit.get_stats()
            for name, circuit in self.circuit_breakers.items()
        }
    
    async def health_check_all(
        self,
        health_checks: Dict[str, Callable[[], Awaitable[bool]]]
    ) -> Dict[str, bool]:
        """Perform health checks for multiple circuits."""
        results = {}
        
        for circuit_name, health_check_func in health_checks.items():
            if circuit_name in self.circuit_breakers:
                circuit = self.circuit_breakers[circuit_name]
                results[circuit_name] = await circuit.health_check(health_check_func)
        
        return results


# Global circuit breaker manager
_global_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get or create the global circuit breaker manager."""
    global _global_circuit_breaker_manager
    
    if _global_circuit_breaker_manager is None:
        _global_circuit_breaker_manager = CircuitBreakerManager()
    
    return _global_circuit_breaker_manager


# Convenience decorator for circuit breaker
def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    timeout_duration: float = 60.0,
    success_threshold: int = 3
):
    """
    Decorator to protect functions with circuit breaker.
    
    Args:
        name: Circuit breaker name
        failure_threshold: Number of failures to trip circuit
        timeout_duration: Timeout before attempting reset
        success_threshold: Successes needed to close circuit
    """
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        async def wrapper(*args, **kwargs) -> Any:
            config = CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                timeout_duration=timeout_duration,
                success_threshold=success_threshold
            )
            
            manager = get_circuit_breaker_manager()
            return await manager.call_through_circuit(
                name, func, *args, config=config, **kwargs
            )
        
        return wrapper
    return decorator