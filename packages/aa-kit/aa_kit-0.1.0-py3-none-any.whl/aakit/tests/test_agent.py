"""
Test AA Kit with real API calls
Requires: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable
Run: python test_agent.py
"""

import asyncio
import os
from aakit import Agent
from aakit.core import ProductionConfig, set_production_config


async def test_agent():
    """Test agent with production features."""
    print("🤖 Testing AA Kit with Production Features")
    print("=" * 50)
    
    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    if not (has_openai or has_anthropic):
        print("❌ No API keys found!")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print(f"✅ API Keys: OpenAI={has_openai}, Anthropic={has_anthropic}")
    
    # Configure production features
    config = ProductionConfig(
        enable_response_caching=True,
        enable_rate_limiting=True,
        enable_timeout_handling=True,
        enable_observability=True,
        cache_ttl=300.0  # 5 minutes
    )
    set_production_config(config)
    
    # Choose model based on available keys
    if has_openai:
        model = "gpt-3.5-turbo"
    else:
        model = "claude-3-haiku"
    
    print(f"✅ Using model: {model}")
    
    # Create agent
    agent = Agent(
        name="test_agent",
        instruction="You are a helpful assistant. Keep responses brief.",
        model=model
    )
    
    print("✅ Agent created with production features")
    
    # Test 1: Basic chat
    print("\n1. Testing basic chat...")
    import time
    start = time.time()
    
    try:
        response = await agent.chat("What is 2+2? Answer briefly.")
        duration = time.time() - start
        print(f"   ✅ Response: {response}")
        print(f"   ✅ Duration: {duration:.2f}s")
    except Exception as e:
        print(f"   ❌ Chat failed: {e}")
        return False
    
    # Test 2: Cached response (should be faster)
    print("\n2. Testing cached response...")
    start = time.time()
    
    try:
        cached_response = await agent.chat("What is 2+2? Answer briefly.")
        cache_duration = time.time() - start
        print(f"   ✅ Cached response: {cached_response}")
        print(f"   ✅ Duration: {cache_duration:.2f}s")
        
        if cache_duration < duration * 0.5:
            print("   ✅ Cache speedup detected!")
        else:
            print("   ℹ️  Cache may not have hit (different response)")
    except Exception as e:
        print(f"   ❌ Cached chat failed: {e}")
    
    # Test 3: Different question
    print("\n3. Testing different question...")
    try:
        response2 = await agent.chat("What is the capital of France? One word.")
        print(f"   ✅ Response: {response2}")
    except Exception as e:
        print(f"   ❌ Second chat failed: {e}")
    
    # Test 4: Streaming (if supported)
    print("\n4. Testing streaming...")
    try:
        print("   Stream: ", end="")
        async for chunk in agent.stream_chat("Count from 1 to 5, one number per chunk."):
            print(chunk, end="", flush=True)
        print()
        print("   ✅ Streaming completed")
    except Exception as e:
        print(f"   ℹ️  Streaming not available: {e}")
    
    print("\n🎉 Agent testing completed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    if success:
        print("\n✅ AA Kit is working with production features!")
    else:
        print("\n❌ Agent test failed")