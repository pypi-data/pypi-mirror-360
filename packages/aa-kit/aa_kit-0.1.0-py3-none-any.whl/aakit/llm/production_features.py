"""
Production feature integration for LLM Manager

This module provides production-grade enhancements that can be applied
to the base LLM Manager when production features are enabled.
"""

import asyncio
import logging
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .providers import LLMMessage, LLMResponse
from ..core.config import get_production_config
from ..core.connection_manager import get_connection_manager
from ..core.timeout_manager import get_timeout_manager, TimeoutType
from ..core.rate_limiter import get_rate_limit_manager
from ..core.cache_manager import get_cache_manager
from ..core.retry_manager import get_retry_manager
from ..core.circuit_breaker import get_circuit_breaker_manager
from ..core.lifecycle_manager import get_resource_manager, ShutdownPhase
from ..core.parallel_executor import get_parallel_executor, ExecutionStrategy
from ..core.streaming_manager import get_stream_manager, StreamType
from ..core.observability import get_observability_manager

logger = logging.getLogger(__name__)


class ProductionFeatures:
    """
    Mixin class that adds production features to LLM Manager.
    
    This class provides all enterprise-grade features as optional
    enhancements that can be enabled/disabled via configuration.
    """
    
    def __init__(self):
        """Initialize production feature managers."""
        self._production_config = get_production_config()
        self._production_initialized = False
        
        # Lazy-loaded production subsystems
        self._connection_manager = None
        self._timeout_manager = None
        self._rate_limit_manager = None
        self._cache_manager = None
        self._retry_manager = None
        self._circuit_breaker_manager = None
        self._resource_manager = None
        self._parallel_executor = None
        self._stream_manager = None
        self._observability_manager = None
    
    async def _ensure_production_initialized(self):
        """Ensure production features are initialized."""
        if self._production_initialized:
            return
        
        config = self._production_config
        
        # Initialize enabled subsystems
        if config.enable_connection_pooling:
            self._connection_manager = get_connection_manager()
        
        if config.enable_timeout_handling:
            self._timeout_manager = get_timeout_manager()
        
        if config.enable_rate_limiting:
            self._rate_limit_manager = get_rate_limit_manager()
        
        if config.enable_response_caching:
            self._cache_manager = get_cache_manager()
        
        if config.enable_retry_logic:
            self._retry_manager = get_retry_manager()
        
        if config.enable_circuit_breaker:
            self._circuit_breaker_manager = get_circuit_breaker_manager()
        
        if config.enable_resource_cleanup:
            self._resource_manager = get_resource_manager()
            # Register this LLM manager
            await self._resource_manager.register_resource(
                self,
                resource_type="LLMManager",
                shutdown_phase=ShutdownPhase.NORMAL
            )
        
        if config.enable_parallel_execution:
            self._parallel_executor = get_parallel_executor()
        
        if config.enable_streaming:
            self._stream_manager = get_stream_manager()
        
        if config.enable_observability:
            self._observability_manager = get_observability_manager()
        
        self._production_initialized = True
        logger.info("Production features initialized for LLM Manager")
    
    async def _apply_rate_limiting(self, provider: str) -> bool:
        """Apply rate limiting if enabled."""
        if not self._production_config.enable_rate_limiting or not self._rate_limit_manager:
            return True
        
        return await self._rate_limit_manager.acquire(
            provider=provider,
            tokens=1.0,
            operation="llm_chat"
        )
    
    async def _check_cache(self, operation: str, inputs: Dict[str, Any], semantic_text: Optional[str] = None) -> Optional[Any]:
        """Check cache for response if enabled."""
        if not self._production_config.enable_response_caching or not self._cache_manager:
            return None
        
        return await self._cache_manager.get(
            operation=operation,
            inputs=inputs,
            semantic_text=semantic_text
        )
    
    async def _cache_response(self, operation: str, inputs: Dict[str, Any], value: Any, semantic_text: Optional[str] = None):
        """Cache response if enabled."""
        if not self._production_config.enable_response_caching or not self._cache_manager:
            return
        
        await self._cache_manager.put(
            operation=operation,
            inputs=inputs,
            value=value,
            ttl=self._production_config.cache_ttl,
            semantic_text=semantic_text
        )
    
    async def _execute_with_production_features(
        self,
        func: callable,
        *args,
        provider: str = "default",
        operation: str = "llm_request",
        **kwargs
    ) -> Any:
        """Execute function with all production protections."""
        # Apply timeout
        if self._production_config.enable_timeout_handling and self._timeout_manager:
            timeout = self._production_config.llm_request_timeout
            
            async def with_timeout():
                async with self._timeout_manager.timeout_context(operation, timeout, TimeoutType.REQUEST):
                    return await func(*args, **kwargs)
        else:
            async def with_timeout():
                return await func(*args, **kwargs)
        
        # Apply circuit breaker
        if self._production_config.enable_circuit_breaker and self._circuit_breaker_manager:
            circuit = await self._circuit_breaker_manager.get_circuit_breaker(f"{operation}_{provider}")
            
            # Apply retry within circuit breaker
            if self._production_config.enable_retry_logic and self._retry_manager:
                return await circuit.call(
                    self._retry_manager.execute_with_retry,
                    with_timeout,
                    operation_name=f"{operation}_{provider}"
                )
            else:
                return await circuit.call(with_timeout)
        
        # Just retry without circuit breaker
        elif self._production_config.enable_retry_logic and self._retry_manager:
            return await self._retry_manager.execute_with_retry(
                with_timeout,
                operation_name=f"{operation}_{provider}"
            )
        
        # No protection, direct call
        else:
            return await with_timeout()
    
    async def _record_metrics(
        self,
        provider: str,
        model: str,
        tokens: int,
        duration: float,
        success: bool,
        operation: str = "llm_chat"
    ):
        """Record metrics if observability is enabled."""
        if not self._production_config.enable_observability or not self._observability_manager:
            return
        
        await self._observability_manager.track_llm_call(
            provider=provider,
            model=model,
            tokens=tokens,
            duration=duration,
            success=success
        )
    
    async def batch_process(
        self,
        requests: List[Dict[str, Any]],
        strategy: ExecutionStrategy = ExecutionStrategy.BEST_EFFORT,
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple requests in parallel.
        
        Args:
            requests: List of request dictionaries
            strategy: Execution strategy
            max_concurrent: Maximum concurrent requests
            
        Returns:
            List of results
        """
        if not self._production_config.enable_parallel_execution:
            # Fallback to sequential processing
            results = []
            for request in requests:
                try:
                    result = await self.chat(**request)
                    results.append({'success': True, 'result': result})
                except Exception as e:
                    results.append({'success': False, 'error': str(e)})
            return results
        
        # Ensure production features initialized
        await self._ensure_production_initialized()
        
        if not self._parallel_executor:
            self._parallel_executor = get_parallel_executor()
        
        # Prepare tasks
        tasks = []
        for i, request in enumerate(requests):
            tasks.append((
                f"batch_{i}",
                self.chat,
                (),
                request
            ))
        
        # Execute in parallel
        execution_result = await self._parallel_executor.execute_functions(
            tasks,
            strategy=strategy,
            timeout=self._production_config.default_timeout * 2
        )
        
        # Format results
        return [
            {
                'task_id': r.task_id,
                'success': r.success,
                'result': r.result,
                'error': str(r.exception) if r.exception else None,
                'duration': r.duration
            }
            for r in execution_result.results
        ]
    
    async def create_stream(self, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a stream for real-time responses if streaming is enabled."""
        if not self._production_config.enable_streaming or not self._stream_manager:
            return None
        
        return await self._stream_manager.create_stream(metadata=metadata)
    
    async def emit_to_stream(self, stream_id: str, chunk_type: StreamType, data: Any) -> bool:
        """Emit data to stream if enabled."""
        if not self._production_config.enable_streaming or not self._stream_manager or not stream_id:
            return False
        
        return await self._stream_manager.emit(stream_id, chunk_type, data)
    
    async def close_stream(self, stream_id: str):
        """Close a stream if enabled."""
        if self._production_config.enable_streaming and self._stream_manager and stream_id:
            await self._stream_manager.close_stream(stream_id)
    
    def get_provider_for_model(self, model: str) -> str:
        """Get provider name from model name."""
        if model.startswith(('gpt-', 'o1-')):
            return 'openai'
        elif model.startswith('claude-'):
            return 'anthropic'
        else:
            return 'unknown'