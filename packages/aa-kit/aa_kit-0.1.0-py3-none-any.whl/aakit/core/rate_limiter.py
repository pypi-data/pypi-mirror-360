"""
Enterprise-grade rate limiting for AA Kit

Implements multiple rate limiting algorithms including token bucket, sliding window,
and adaptive rate limiting for LLM providers and external services.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Union, List
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    # Basic rate limits
    requests_per_second: float = 10.0
    requests_per_minute: float = 600.0
    requests_per_hour: float = 10000.0
    
    # Token limits for LLM providers
    tokens_per_minute: float = 50000.0
    tokens_per_hour: float = 1000000.0
    
    # Algorithm selection
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    
    # Token bucket specific
    bucket_size: Optional[float] = None  # Auto-calculated if None
    refill_rate: Optional[float] = None  # Auto-calculated if None
    
    # Sliding window specific
    window_size_seconds: float = 60.0
    
    # Adaptive rate limiting
    enable_adaptive: bool = True
    adaptive_increase_factor: float = 1.1
    adaptive_decrease_factor: float = 0.9
    error_threshold: float = 0.1  # 10% error rate triggers backoff
    
    # Burst handling
    allow_burst: bool = True
    burst_multiplier: float = 2.0
    
    # Queue management
    max_queue_size: int = 1000
    queue_timeout: float = 60.0
    
    # Provider-specific configs
    provider_configs: Dict[str, Dict[str, float]] = field(default_factory=dict)


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        limit_type: str = "requests",
        current_usage: float = 0,
        limit: float = 0
    ):
        self.retry_after = retry_after
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit = limit
        
        super().__init__(
            f"{message} (current: {current_usage}, limit: {limit}, "
            f"retry_after: {retry_after}s)"
        )


class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def acquire(self, tokens: float = 1.0) -> bool:
        """Acquire tokens from the rate limiter."""
        pass
    
    @abstractmethod
    async def try_acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens without blocking."""
        pass
    
    @abstractmethod
    def get_available_tokens(self) -> float:
        """Get number of available tokens."""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        pass


class TokenBucketLimiter(RateLimiter):
    """Token bucket rate limiter implementation."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.bucket_size = config.bucket_size or config.requests_per_second * 2
        self.refill_rate = config.refill_rate or config.requests_per_second
        
        self.tokens = self.bucket_size
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'accepted_requests': 0,
            'rejected_requests': 0,
            'total_tokens_consumed': 0,
            'last_refill_time': self.last_refill
        }
    
    def _refill_tokens(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
            self.last_refill = now
            self.stats['last_refill_time'] = now
    
    async def acquire(self, tokens: float = 1.0) -> bool:
        """Acquire tokens, blocking if necessary."""
        async with self._lock:
            self._refill_tokens()
            
            self.stats['total_requests'] += 1
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats['accepted_requests'] += 1
                self.stats['total_tokens_consumed'] += tokens
                return True
            
            # Calculate wait time
            deficit = tokens - self.tokens
            wait_time = deficit / self.refill_rate
            
            if wait_time > 60:  # Don't wait more than 1 minute
                self.stats['rejected_requests'] += 1
                return False
        
        # Wait outside the lock
        await asyncio.sleep(wait_time)
        
        # Try again after waiting
        async with self._lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats['accepted_requests'] += 1
                self.stats['total_tokens_consumed'] += tokens
                return True
            
            self.stats['rejected_requests'] += 1
            return False
    
    async def try_acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens without blocking."""
        async with self._lock:
            self._refill_tokens()
            
            self.stats['total_requests'] += 1
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.stats['accepted_requests'] += 1
                self.stats['total_tokens_consumed'] += tokens
                return True
            
            self.stats['rejected_requests'] += 1
            return False
    
    def get_available_tokens(self) -> float:
        """Get current available tokens."""
        self._refill_tokens()
        return self.tokens
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        total = self.stats['total_requests']
        acceptance_rate = (self.stats['accepted_requests'] / total * 100) if total > 0 else 0
        
        return {
            'type': 'token_bucket',
            'bucket_size': self.bucket_size,
            'refill_rate': self.refill_rate,
            'current_tokens': self.get_available_tokens(),
            'acceptance_rate_percent': round(acceptance_rate, 2),
            **self.stats
        }


class SlidingWindowLimiter(RateLimiter):
    """Sliding window rate limiter implementation."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.window_size = config.window_size_seconds
        self.limit = config.requests_per_minute
        
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'accepted_requests': 0,
            'rejected_requests': 0,
            'window_size_seconds': self.window_size,
            'current_window_count': 0
        }
    
    def _cleanup_old_requests(self):
        """Remove requests outside the sliding window."""
        now = time.time()
        cutoff = now - self.window_size
        
        while self.requests and self.requests[0] <= cutoff:
            self.requests.popleft()
        
        self.stats['current_window_count'] = len(self.requests)
    
    async def acquire(self, tokens: float = 1.0) -> bool:
        """Acquire tokens (tokens represent request weight)."""
        async with self._lock:
            self._cleanup_old_requests()
            
            self.stats['total_requests'] += 1
            current_count = len(self.requests)
            
            if current_count + tokens <= self.limit:
                now = time.time()
                # Add multiple entries for weighted requests
                for _ in range(int(tokens)):
                    self.requests.append(now)
                
                self.stats['accepted_requests'] += 1
                self.stats['current_window_count'] = len(self.requests)
                return True
            
            self.stats['rejected_requests'] += 1
            return False
    
    async def try_acquire(self, tokens: float = 1.0) -> bool:
        """Same as acquire for sliding window (non-blocking by nature)."""
        return await self.acquire(tokens)
    
    def get_available_tokens(self) -> float:
        """Get available capacity in current window."""
        self._cleanup_old_requests()
        return max(0, self.limit - len(self.requests))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        total = self.stats['total_requests']
        acceptance_rate = (self.stats['accepted_requests'] / total * 100) if total > 0 else 0
        
        return {
            'type': 'sliding_window',
            'window_size_seconds': self.window_size,
            'limit': self.limit,
            'available_capacity': self.get_available_tokens(),
            'acceptance_rate_percent': round(acceptance_rate, 2),
            **self.stats
        }


class AdaptiveRateLimiter(RateLimiter):
    """Adaptive rate limiter that adjusts based on error rates."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.base_limiter = TokenBucketLimiter(config)
        
        # Adaptive parameters
        self.current_multiplier = 1.0
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = time.time()
        self.adjustment_interval = 30.0  # Adjust every 30 seconds
        
        # Statistics
        self.stats = {
            'adaptations': 0,
            'current_multiplier': self.current_multiplier,
            'error_rate': 0.0,
            'last_adjustment': self.last_adjustment
        }
    
    def _should_adjust(self) -> bool:
        """Check if rate should be adjusted."""
        now = time.time()
        return now - self.last_adjustment >= self.adjustment_interval
    
    def _adjust_rate(self):
        """Adjust rate based on error metrics."""
        total_requests = self.error_count + self.success_count
        
        if total_requests < 10:  # Need minimum samples
            return
        
        error_rate = self.error_count / total_requests
        self.stats['error_rate'] = error_rate
        
        if error_rate > self.config.error_threshold:
            # Too many errors, decrease rate
            self.current_multiplier *= self.config.adaptive_decrease_factor
            self.current_multiplier = max(0.1, self.current_multiplier)
        elif error_rate < self.config.error_threshold / 2:
            # Low error rate, can increase
            self.current_multiplier *= self.config.adaptive_increase_factor
            self.current_multiplier = min(2.0, self.current_multiplier)
        
        # Update base limiter's refill rate
        self.base_limiter.refill_rate = (
            self.config.requests_per_second * self.current_multiplier
        )
        
        # Reset counters
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = time.time()
        self.stats['adaptations'] += 1
        self.stats['current_multiplier'] = self.current_multiplier
        self.stats['last_adjustment'] = self.last_adjustment
        
        logger.debug(
            f"Adaptive rate limiter adjusted: multiplier={self.current_multiplier:.2f}, "
            f"error_rate={error_rate:.2%}"
        )
    
    async def acquire(self, tokens: float = 1.0) -> bool:
        """Acquire tokens with adaptive adjustment."""
        if self._should_adjust():
            self._adjust_rate()
        
        return await self.base_limiter.acquire(tokens)
    
    async def try_acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens with adaptive adjustment."""
        if self._should_adjust():
            self._adjust_rate()
        
        return await self.base_limiter.try_acquire(tokens)
    
    def record_success(self):
        """Record a successful operation."""
        self.success_count += 1
    
    def record_error(self):
        """Record a failed operation."""
        self.error_count += 1
    
    def get_available_tokens(self) -> float:
        """Get available tokens from base limiter."""
        return self.base_limiter.get_available_tokens()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get combined statistics."""
        base_stats = self.base_limiter.get_stats()
        base_stats.update(self.stats)
        base_stats['type'] = 'adaptive'
        return base_stats


class RateLimitManager:
    """
    Enterprise rate limit manager with multiple limiters and provider-specific rules.
    
    Features:
    - Multiple rate limiting algorithms
    - Provider-specific rate limits
    - Token-based and request-based limiting
    - Adaptive rate adjustment
    - Queue management for burst handling
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.limiters: Dict[str, RateLimiter] = {}
        self.queues: Dict[str, asyncio.Queue] = {}
        
        # Create default limiters
        self._create_default_limiters()
        
        # Global statistics
        self.global_stats = {
            'total_requests': 0,
            'rate_limited_requests': 0,
            'queue_overflows': 0
        }
    
    def _create_default_limiters(self):
        """Create default rate limiters for common operations."""
        # General API rate limiter
        self.limiters['default'] = self._create_limiter(self.config)
        
        # Provider-specific limiters
        providers = ['openai', 'anthropic', 'mcp']
        for provider in providers:
            provider_config = self._get_provider_config(provider)
            self.limiters[provider] = self._create_limiter(provider_config)
    
    def _create_limiter(self, config: RateLimitConfig) -> RateLimiter:
        """Create a rate limiter based on algorithm configuration."""
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return TokenBucketLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return SlidingWindowLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.ADAPTIVE:
            return AdaptiveRateLimiter(config)
        else:
            # Default to token bucket
            return TokenBucketLimiter(config)
    
    def _get_provider_config(self, provider: str) -> RateLimitConfig:
        """Get provider-specific configuration."""
        base_config = self.config
        provider_overrides = base_config.provider_configs.get(provider, {})
        
        # Provider-specific defaults
        defaults = {
            'openai': {
                'requests_per_minute': 500,
                'tokens_per_minute': 150000,
                'algorithm': RateLimitAlgorithm.ADAPTIVE
            },
            'anthropic': {
                'requests_per_minute': 1000,
                'tokens_per_minute': 200000,
                'algorithm': RateLimitAlgorithm.TOKEN_BUCKET
            },
            'mcp': {
                'requests_per_second': 20,
                'algorithm': RateLimitAlgorithm.TOKEN_BUCKET
            }
        }
        
        # Merge configurations
        provider_defaults = defaults.get(provider, {})
        merged_config = {
            **base_config.__dict__,
            **provider_defaults,
            **provider_overrides
        }
        
        return RateLimitConfig(**merged_config)
    
    async def acquire(
        self,
        provider: str = 'default',
        tokens: float = 1.0,
        operation: str = 'request'
    ) -> bool:
        """
        Acquire rate limit tokens for an operation.
        
        Args:
            provider: Provider/limiter name
            tokens: Number of tokens to acquire
            operation: Operation type for logging
            
        Returns:
            True if tokens acquired, False if rate limited
        """
        self.global_stats['total_requests'] += 1
        
        limiter = self.limiters.get(provider, self.limiters['default'])
        
        success = await limiter.acquire(tokens)
        
        if not success:
            self.global_stats['rate_limited_requests'] += 1
            logger.warning(
                f"Rate limit exceeded for {provider} provider "
                f"(operation: {operation}, tokens: {tokens})"
            )
        
        return success
    
    async def try_acquire(
        self,
        provider: str = 'default',
        tokens: float = 1.0
    ) -> bool:
        """Try to acquire tokens without blocking."""
        limiter = self.limiters.get(provider, self.limiters['default'])
        return await limiter.try_acquire(tokens)
    
    async def acquire_with_queue(
        self,
        provider: str = 'default',
        tokens: float = 1.0,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Acquire tokens with queueing for burst handling.
        
        Args:
            provider: Provider name
            tokens: Tokens to acquire
            timeout: Queue timeout
            
        Returns:
            True if acquired, False if timed out
        """
        queue_key = f"{provider}_queue"
        
        if queue_key not in self.queues:
            self.queues[queue_key] = asyncio.Queue(self.config.max_queue_size)
        
        queue = self.queues[queue_key]
        
        try:
            # Add to queue
            request_event = asyncio.Event()
            queue_timeout = timeout or self.config.queue_timeout
            
            await asyncio.wait_for(
                queue.put((tokens, request_event)),
                timeout=queue_timeout
            )
            
            # Process queue in background
            asyncio.create_task(self._process_queue(provider, queue))
            
            # Wait for processing
            await asyncio.wait_for(request_event.wait(), timeout=queue_timeout)
            return True
            
        except asyncio.TimeoutError:
            self.global_stats['queue_overflows'] += 1
            return False
        except asyncio.QueueFull:
            self.global_stats['queue_overflows'] += 1
            return False
    
    async def _process_queue(self, provider: str, queue: asyncio.Queue):
        """Process queued requests for a provider."""
        limiter = self.limiters.get(provider, self.limiters['default'])
        
        while not queue.empty():
            try:
                tokens, event = await asyncio.wait_for(queue.get(), timeout=1.0)
                success = await limiter.acquire(tokens)
                
                if success:
                    event.set()
                else:
                    # Put back in queue if failed
                    await queue.put((tokens, event))
                    break
                    
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                break
    
    def record_success(self, provider: str = 'default'):
        """Record successful operation for adaptive limiters."""
        limiter = self.limiters.get(provider, self.limiters['default'])
        if isinstance(limiter, AdaptiveRateLimiter):
            limiter.record_success()
    
    def record_error(self, provider: str = 'default'):
        """Record failed operation for adaptive limiters."""
        limiter = self.limiters.get(provider, self.limiters['default'])
        if isinstance(limiter, AdaptiveRateLimiter):
            limiter.record_error()
    
    def get_available_capacity(self, provider: str = 'default') -> float:
        """Get available capacity for a provider."""
        limiter = self.limiters.get(provider, self.limiters['default'])
        return limiter.get_available_tokens()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting statistics."""
        limiter_stats = {}
        for name, limiter in self.limiters.items():
            limiter_stats[name] = limiter.get_stats()
        
        total_requests = self.global_stats['total_requests']
        rate_limit_percentage = (
            self.global_stats['rate_limited_requests'] / total_requests * 100
            if total_requests > 0 else 0
        )
        
        return {
            'global': {
                **self.global_stats,
                'rate_limit_percentage': round(rate_limit_percentage, 2),
                'active_queues': len(self.queues)
            },
            'limiters': limiter_stats
        }


# Global rate limit manager
_global_rate_limit_manager: Optional[RateLimitManager] = None


def get_rate_limit_manager() -> RateLimitManager:
    """Get or create the global rate limit manager."""
    global _global_rate_limit_manager
    
    if _global_rate_limit_manager is None:
        _global_rate_limit_manager = RateLimitManager()
    
    return _global_rate_limit_manager