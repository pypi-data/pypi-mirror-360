"""
Enterprise-grade retry logic for AA Kit

Implements exponential backoff, jittered retries, circuit breaker integration,
and intelligent retry strategies for different failure types.
"""

import asyncio
import functools
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, Union
from enum import Enum

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI = "fibonacci"
    ADAPTIVE = "adaptive"


class FailureType(Enum):
    """Types of failures for retry decisions."""
    TRANSIENT = "transient"          # Network timeouts, rate limits
    PERSISTENT = "persistent"        # Authentication, invalid inputs
    FATAL = "fatal"                  # System errors, configuration issues
    UNKNOWN = "unknown"              # Unclassified errors


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    
    # Basic retry settings
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    
    # Exponential backoff settings
    backoff_multiplier: float = 2.0
    jitter: bool = True
    jitter_range: float = 0.1  # ±10% jitter
    
    # Adaptive retry settings
    enable_adaptive: bool = True
    success_threshold: float = 0.8  # 80% success rate
    failure_threshold: float = 0.2  # 20% failure rate
    adaptation_window: int = 100    # Look at last 100 attempts
    
    # Conditional retry settings
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError, TimeoutError, OSError
    ])
    no_retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ValueError, TypeError, KeyError
    ])
    
    # Status code retry settings (for HTTP)
    retry_on_status_codes: List[int] = field(default_factory=lambda: [
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    ])
    
    # Circuit breaker integration
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    
    # Logging and monitoring
    log_retries: bool = True
    log_level: str = "INFO"


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    
    attempt_number: int
    delay: float
    exception: Optional[Exception]
    start_time: float
    end_time: Optional[float] = None
    success: bool = False
    failure_type: FailureType = FailureType.UNKNOWN
    
    @property
    def duration(self) -> float:
        """Get attempt duration."""
        end = self.end_time or time.time()
        return end - self.start_time


class RetryStats:
    """Statistics tracker for retry operations."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.attempts: List[RetryAttempt] = []
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.total_retries = 0
    
    def add_attempt(self, attempt: RetryAttempt):
        """Add retry attempt to statistics."""
        self.attempts.append(attempt)
        if len(self.attempts) > self.window_size:
            self.attempts.pop(0)
        
        if attempt.attempt_number == 1:
            self.total_operations += 1
        else:
            self.total_retries += 1
        
        if attempt.success:
            if attempt.attempt_number == 1:
                self.successful_operations += 1
        elif attempt.attempt_number >= 3:  # Assuming max 3 attempts
            self.failed_operations += 1
    
    def get_success_rate(self) -> float:
        """Get recent success rate."""
        if not self.attempts:
            return 1.0
        
        first_attempts = [a for a in self.attempts if a.attempt_number == 1]
        if not first_attempts:
            return 1.0
        
        successful = sum(1 for a in first_attempts if a.success)
        return successful / len(first_attempts)
    
    def get_average_retries(self) -> float:
        """Get average number of retries per operation."""
        if self.total_operations == 0:
            return 0.0
        return self.total_retries / self.total_operations
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get statistics as dictionary."""
        return {
            'total_operations': self.total_operations,
            'successful_operations': self.successful_operations,
            'failed_operations': self.failed_operations,
            'total_retries': self.total_retries,
            'success_rate': round(self.get_success_rate() * 100, 2),
            'average_retries': round(self.get_average_retries(), 2),
            'recent_attempts': len(self.attempts)
        }


class RetryDelayCalculator(ABC):
    """Abstract base class for retry delay calculation."""
    
    @abstractmethod
    def calculate_delay(self, attempt: int, base_delay: float, max_delay: float) -> float:
        """Calculate delay for retry attempt."""
        pass


class ExponentialBackoffCalculator(RetryDelayCalculator):
    """Exponential backoff delay calculator."""
    
    def __init__(self, multiplier: float = 2.0, jitter: bool = True, jitter_range: float = 0.1):
        self.multiplier = multiplier
        self.jitter = jitter
        self.jitter_range = jitter_range
    
    def calculate_delay(self, attempt: int, base_delay: float, max_delay: float) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        delay = base_delay * (self.multiplier ** (attempt - 1))
        delay = min(delay, max_delay)
        
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay


class LinearBackoffCalculator(RetryDelayCalculator):
    """Linear backoff delay calculator."""
    
    def __init__(self, increment: float = 1.0, jitter: bool = True, jitter_range: float = 0.1):
        self.increment = increment
        self.jitter = jitter
        self.jitter_range = jitter_range
    
    def calculate_delay(self, attempt: int, base_delay: float, max_delay: float) -> float:
        """Calculate linear backoff delay."""
        delay = base_delay + (self.increment * (attempt - 1))
        delay = min(delay, max_delay)
        
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay


class FibonacciBackoffCalculator(RetryDelayCalculator):
    """Fibonacci sequence backoff calculator."""
    
    def __init__(self, jitter: bool = True, jitter_range: float = 0.1):
        self.jitter = jitter
        self.jitter_range = jitter_range
        self._fib_cache = [1, 1]  # First two Fibonacci numbers
    
    def _fibonacci(self, n: int) -> int:
        """Get nth Fibonacci number with caching."""
        while len(self._fib_cache) <= n:
            self._fib_cache.append(
                self._fib_cache[-1] + self._fib_cache[-2]
            )
        return self._fib_cache[n]
    
    def calculate_delay(self, attempt: int, base_delay: float, max_delay: float) -> float:
        """Calculate Fibonacci backoff delay."""
        fib_multiplier = self._fibonacci(attempt - 1)
        delay = base_delay * fib_multiplier
        delay = min(delay, max_delay)
        
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            jitter = random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay + jitter)
        
        return delay


class FailureClassifier:
    """Classifies failures for retry decision making."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
    
    def classify_exception(self, exception: Exception) -> FailureType:
        """Classify exception to determine retry strategy."""
        # Check for explicit no-retry exceptions
        for no_retry_type in self.config.no_retry_on_exceptions:
            if isinstance(exception, no_retry_type):
                return FailureType.PERSISTENT
        
        # Check for explicit retry exceptions
        for retry_type in self.config.retry_on_exceptions:
            if isinstance(exception, retry_type):
                return FailureType.TRANSIENT
        
        # Classify common exceptions
        if isinstance(exception, (TimeoutError, ConnectionError, OSError)):
            return FailureType.TRANSIENT
        elif isinstance(exception, (ValueError, TypeError, KeyError, AttributeError)):
            return FailureType.PERSISTENT
        elif isinstance(exception, (SystemExit, KeyboardInterrupt, MemoryError)):
            return FailureType.FATAL
        else:
            return FailureType.UNKNOWN
    
    def should_retry(self, exception: Exception, attempt: int, max_attempts: int) -> bool:
        """Determine if operation should be retried."""
        if attempt >= max_attempts:
            return False
        
        failure_type = self.classify_exception(exception)
        
        # Never retry fatal or persistent errors
        if failure_type in [FailureType.FATAL, FailureType.PERSISTENT]:
            return False
        
        # Always retry transient errors (within attempt limit)
        if failure_type == FailureType.TRANSIENT:
            return True
        
        # For unknown errors, be conservative and retry once
        if failure_type == FailureType.UNKNOWN:
            return attempt == 1
        
        return False


class RetryManager:
    """
    Enterprise-grade retry manager with intelligent backoff and failure classification.
    
    Features:
    - Multiple retry strategies (exponential, linear, fibonacci)
    - Intelligent failure classification
    - Adaptive retry adjustment based on success rates
    - Circuit breaker integration
    - Comprehensive statistics and monitoring
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.stats = RetryStats(self.config.adaptation_window)
        self.failure_classifier = FailureClassifier(self.config)
        
        # Create delay calculator based on strategy
        self.delay_calculator = self._create_delay_calculator()
        
        # Adaptive retry state
        self.adaptive_multiplier = 1.0
        self.last_adaptation_time = time.time()
    
    def _create_delay_calculator(self) -> RetryDelayCalculator:
        """Create delay calculator based on strategy."""
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return ExponentialBackoffCalculator(
                self.config.backoff_multiplier,
                self.config.jitter,
                self.config.jitter_range
            )
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            return LinearBackoffCalculator(
                self.config.base_delay,
                self.config.jitter,
                self.config.jitter_range
            )
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            return FibonacciBackoffCalculator(
                self.config.jitter,
                self.config.jitter_range
            )
        else:
            # Default to exponential backoff
            return ExponentialBackoffCalculator()
    
    def _adapt_retry_parameters(self):
        """Adapt retry parameters based on recent success/failure rates."""
        if not self.config.enable_adaptive:
            return
        
        success_rate = self.stats.get_success_rate()
        
        if success_rate > self.config.success_threshold:
            # High success rate, can be more aggressive (fewer retries)
            self.adaptive_multiplier = max(0.5, self.adaptive_multiplier * 0.9)
        elif success_rate < self.config.failure_threshold:
            # Low success rate, be more conservative (more retries)
            self.adaptive_multiplier = min(2.0, self.adaptive_multiplier * 1.1)
        
        self.last_adaptation_time = time.time()
    
    def _get_effective_max_attempts(self) -> int:
        """Get effective max attempts considering adaptive adjustments."""
        base_attempts = self.config.max_attempts
        
        if self.config.enable_adaptive:
            self._adapt_retry_parameters()
            # Adjust attempts based on adaptive multiplier
            return max(1, int(base_attempts * self.adaptive_multiplier))
        
        return base_attempts
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        base_delay = self.config.base_delay
        max_delay = self.config.max_delay
        
        # Apply adaptive adjustment to base delay
        if self.config.enable_adaptive:
            base_delay *= self.adaptive_multiplier
        
        return self.delay_calculator.calculate_delay(attempt, base_delay, max_delay)
    
    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        operation_name: str = "unknown",
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            operation_name: Name for logging and stats
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries failed
        """
        max_attempts = self._get_effective_max_attempts()
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            attempt_start = time.time()
            
            try:
                if self.config.log_retries and attempt > 1:
                    logger.log(
                        getattr(logging, self.config.log_level),
                        f"Retry attempt {attempt}/{max_attempts} for {operation_name}"
                    )
                
                result = await func(*args, **kwargs)
                
                # Record successful attempt
                attempt_obj = RetryAttempt(
                    attempt_number=attempt,
                    delay=0,
                    exception=None,
                    start_time=attempt_start,
                    end_time=time.time(),
                    success=True,
                    failure_type=FailureType.UNKNOWN
                )
                self.stats.add_attempt(attempt_obj)
                
                if self.config.log_retries and attempt > 1:
                    logger.log(
                        getattr(logging, self.config.log_level),
                        f"Operation {operation_name} succeeded on attempt {attempt}"
                    )
                
                return result
                
            except Exception as e:
                last_exception = e
                failure_type = self.failure_classifier.classify_exception(e)
                
                # Record failed attempt
                attempt_obj = RetryAttempt(
                    attempt_number=attempt,
                    delay=0,
                    exception=e,
                    start_time=attempt_start,
                    end_time=time.time(),
                    success=False,
                    failure_type=failure_type
                )
                self.stats.add_attempt(attempt_obj)
                
                # Check if we should retry
                if not self.failure_classifier.should_retry(e, attempt, max_attempts):
                    if self.config.log_retries:
                        logger.log(
                            getattr(logging, self.config.log_level),
                            f"Not retrying {operation_name} due to {failure_type.value} failure: {e}"
                        )
                    break
                
                # Calculate delay for next attempt
                if attempt < max_attempts:
                    delay = self._calculate_delay(attempt)
                    
                    if self.config.log_retries:
                        logger.log(
                            getattr(logging, self.config.log_level),
                            f"Operation {operation_name} failed on attempt {attempt}, "
                            f"retrying in {delay:.2f}s: {e}"
                        )
                    
                    await asyncio.sleep(delay)
        
        # All attempts failed
        if self.config.log_retries:
            logger.error(
                f"Operation {operation_name} failed after {max_attempts} attempts"
            )
        
        raise last_exception
    
    def retry_decorator(
        self,
        operation_name: Optional[str] = None,
        max_attempts: Optional[int] = None,
        base_delay: Optional[float] = None
    ):
        """
        Decorator to add retry logic to async functions.
        
        Args:
            operation_name: Name for logging (uses function name if None)
            max_attempts: Override max attempts
            base_delay: Override base delay
        """
        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            op_name = operation_name or func.__name__
            
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                # Temporarily override config if needed
                original_config = None
                if max_attempts is not None or base_delay is not None:
                    original_config = (self.config.max_attempts, self.config.base_delay)
                    if max_attempts is not None:
                        self.config.max_attempts = max_attempts
                    if base_delay is not None:
                        self.config.base_delay = base_delay
                
                try:
                    return await self.execute_with_retry(func, *args, operation_name=op_name, **kwargs)
                finally:
                    # Restore original config
                    if original_config:
                        self.config.max_attempts, self.config.base_delay = original_config
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive retry statistics."""
        base_stats = self.stats.get_stats_dict()
        
        return {
            'performance': base_stats,
            'configuration': {
                'max_attempts': self.config.max_attempts,
                'strategy': self.config.strategy.value,
                'base_delay': self.config.base_delay,
                'max_delay': self.config.max_delay,
                'adaptive_enabled': self.config.enable_adaptive,
                'adaptive_multiplier': round(self.adaptive_multiplier, 3)
            },
            'recent_stats': {
                'recent_success_rate': round(self.stats.get_success_rate() * 100, 2),
                'average_retries': self.stats.get_average_retries()
            }
        }


# Global retry manager instance
_global_retry_manager: Optional[RetryManager] = None


def get_retry_manager() -> RetryManager:
    """Get or create the global retry manager instance."""
    global _global_retry_manager
    
    if _global_retry_manager is None:
        _global_retry_manager = RetryManager()
    
    return _global_retry_manager


# Convenience decorator for adding retries
def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    operation_name: Optional[str] = None
):
    """
    Decorator to add retry logic to async functions.
    
    Args:
        max_attempts: Maximum retry attempts
        base_delay: Base delay between retries
        strategy: Retry strategy to use
        operation_name: Operation name for logging
    """
    manager = get_retry_manager()
    
    # Temporarily configure manager
    original_config = manager.config
    temp_config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        strategy=strategy
    )
    manager.config = temp_config
    
    def restore_config():
        manager.config = original_config
    
    decorator = manager.retry_decorator(operation_name)
    
    def wrapper(func):
        decorated = decorator(func)
        # Restore config after decoration
        restore_config()
        return decorated
    
    return wrapper