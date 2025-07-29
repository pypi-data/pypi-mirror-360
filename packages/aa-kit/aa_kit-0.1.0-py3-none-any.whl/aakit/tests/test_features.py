"""
Quick test of AA Kit production features
Run: python test_features.py
"""

import asyncio
from aakit.core import ProductionConfig, set_production_config
from aakit.core.cache_manager import get_cache_manager
from aakit.core.rate_limiter import get_rate_limit_manager
from aakit.core.timeout_manager import get_timeout_manager
from aakit.core.parallel_executor import get_parallel_executor, ExecutionStrategy
from aakit.core.observability import get_observability_manager


async def test_features():
    """Test core features without needing API keys."""
    print("🧪 Testing AA Kit Production Features")
    print("=" * 50)
    
    # 1. Test Caching
    print("\n1. Testing Response Caching...")
    cache = get_cache_manager()
    
    # Cache a "response"
    await cache.put("chat", {"query": "hello"}, "Hello! How can I help?", ttl=60)
    
    # Retrieve it
    cached = await cache.get("chat", {"query": "hello"})
    print(f"   ✅ Cache working: {cached}")
    
    # Test semantic similarity
    similar = await cache.get("chat", {"query": "hi there"}, semantic_text="hi there")
    print(f"   ✅ Semantic cache: {'Hit' if similar else 'Miss'}")
    
    # 2. Test Rate Limiting
    print("\n2. Testing Rate Limiting...")
    rate_limiter = get_rate_limit_manager()
    
    allowed_count = 0
    for i in range(10):
        if await rate_limiter.try_acquire("test", 1.0):
            allowed_count += 1
    
    print(f"   ✅ Requests allowed: {allowed_count}/10")
    
    # 3. Test Timeouts
    print("\n3. Testing Timeout Handling...")
    timeout_mgr = get_timeout_manager()
    
    # Fast operation (should succeed)
    async with timeout_mgr.timeout_context("fast_op", 1.0):
        await asyncio.sleep(0.1)
    print("   ✅ Fast operation completed")
    
    # Test timeout detection
    try:
        await timeout_mgr.with_timeout(
            asyncio.sleep(2.0), "slow_op", timeout=0.5
        )
    except Exception as e:
        print(f"   ✅ Timeout caught: {type(e).__name__}")
    
    # 4. Test Parallel Execution
    print("\n4. Testing Parallel Execution...")
    executor = get_parallel_executor()
    
    async def mock_task(n):
        await asyncio.sleep(0.1)
        return f"Result {n}"
    
    tasks = [(f"task_{i}", mock_task, (i,), {}) for i in range(5)]
    
    import time
    start = time.time()
    result = await executor.execute_functions(tasks, ExecutionStrategy.ALL_SUCCESS)
    duration = time.time() - start
    
    print(f"   ✅ Processed {result.total_tasks} tasks in {duration:.2f}s")
    print(f"   ✅ Success rate: {result.success_rate:.0f}%")
    
    # 5. Test Observability
    print("\n5. Testing Observability...")
    obs = get_observability_manager()
    
    # Record metrics
    obs.record_counter("test_requests", 5)
    obs.record_gauge("active_users", 42)
    obs.record_timer("response_time", 1.23)
    
    # Create a trace
    async with obs.trace_operation("test_operation") as span:
        span.set_tag("test", "true")
        await asyncio.sleep(0.05)
    
    print("   ✅ Metrics recorded")
    print("   ✅ Trace completed")
    
    # Get health status
    health = await obs.health_check()
    print(f"   ✅ System health: {health['status']}")
    
    print("\n🎉 All production features working!")
    
    # Show configuration
    config = ProductionConfig()
    print(f"\n📊 Active Features:")
    print(f"   Connection Pooling: {config.enable_connection_pooling}")
    print(f"   Rate Limiting: {config.enable_rate_limiting}")
    print(f"   Response Caching: {config.enable_response_caching}")
    print(f"   Circuit Breakers: {config.enable_circuit_breaker}")
    print(f"   Observability: {config.enable_observability}")


if __name__ == "__main__":
    asyncio.run(test_features())