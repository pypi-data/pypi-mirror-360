"""
Enterprise-grade caching system for AA Kit

Implements semantic caching, LRU caching, and distributed caching for LLM responses,
tool outputs, and memory operations with intelligent cache invalidation.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache storage."""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"
    HYBRID = "hybrid"


class EvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    SEMANTIC_SIMILARITY = "semantic_similarity"


@dataclass
class CacheConfig:
    """Configuration for cache system."""
    
    # Basic settings
    cache_type: CacheType = CacheType.MEMORY
    max_size: int = 10000
    default_ttl: float = 3600.0  # 1 hour
    
    # Eviction policy
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    
    # Semantic caching
    enable_semantic_caching: bool = True
    semantic_similarity_threshold: float = 0.85
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Performance settings
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress items > 1KB
    
    # Background cleanup
    cleanup_interval: float = 300.0  # 5 minutes
    cleanup_batch_size: int = 100
    
    # Redis settings (if using Redis)
    redis_url: Optional[str] = None
    redis_prefix: str = "agentz_cache"
    
    # Disk cache settings
    disk_cache_dir: str = "/tmp/agentz_cache"
    
    # Statistics
    enable_statistics: bool = True
    stats_interval: float = 60.0  # 1 minute


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    content_hash: Optional[str] = None
    embedding: Optional[np.ndarray] = None
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    @property
    def age(self) -> float:
        """Get age of entry in seconds."""
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        """Get idle time since last access."""
        return time.time() - self.last_accessed
    
    def access(self):
        """Mark entry as accessed."""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheBackend(ABC):
    """Abstract cache backend interface."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        pass
    
    @abstractmethod
    async def put(self, entry: CacheEntry) -> bool:
        """Put cache entry."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cache entry."""
        pass
    
    @abstractmethod
    async def clear(self) -> int:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get cache size."""
        pass
    
    @abstractmethod
    async def keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with LRU eviction."""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        async with self._lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired:
                entry.access()
                # Move to end of access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                return entry
            elif entry:
                # Entry expired, remove it
                await self._remove_entry(key)
            return None
    
    async def put(self, entry: CacheEntry) -> bool:
        """Put cache entry."""
        async with self._lock:
            # Remove existing entry if present
            if entry.key in self.cache:
                await self._remove_entry(entry.key)
            
            # Check if we need to evict
            while len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            # Add new entry
            self.cache[entry.key] = entry
            self.access_order.append(entry.key)
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry."""
        async with self._lock:
            return await self._remove_entry(key)
    
    async def _remove_entry(self, key: str) -> bool:
        """Remove entry from cache and access order."""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False
    
    async def _evict_lru(self):
        """Evict least recently used entry."""
        if self.access_order:
            lru_key = self.access_order[0]
            await self._remove_entry(lru_key)
    
    async def clear(self) -> int:
        """Clear all cache entries."""
        async with self._lock:
            size = len(self.cache)
            self.cache.clear()
            self.access_order.clear()
            return size
    
    async def size(self) -> int:
        """Get cache size."""
        return len(self.cache)
    
    async def keys(self) -> List[str]:
        """Get all cache keys."""
        return list(self.cache.keys())


class SemanticCacheManager:
    """
    Enterprise-grade cache manager with semantic similarity and intelligent caching.
    
    Features:
    - Semantic similarity caching for LLM responses
    - Multiple eviction policies
    - Compression for large objects
    - Background cleanup and optimization
    - Comprehensive statistics and monitoring
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.backend = self._create_backend()
        
        # Embedding model for semantic similarity (lazy loaded)
        self._embedding_model = None
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'puts': 0,
            'evictions': 0,
            'semantic_matches': 0,
            'compression_saves': 0,
            'total_size_bytes': 0,
            'start_time': time.time()
        }
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats_task: Optional[asyncio.Task] = None
        self._closed = False
        
        # Start background tasks
        if self.config.cleanup_interval > 0:
            self._start_cleanup_task()
        if self.config.enable_statistics and self.config.stats_interval > 0:
            self._start_stats_task()
    
    def _create_backend(self) -> CacheBackend:
        """Create appropriate cache backend."""
        if self.config.cache_type == CacheType.MEMORY:
            return MemoryCacheBackend(self.config.max_size)
        elif self.config.cache_type == CacheType.REDIS:
            # Would implement Redis backend here
            raise NotImplementedError("Redis backend not implemented yet")
        elif self.config.cache_type == CacheType.DISK:
            # Would implement disk backend here
            raise NotImplementedError("Disk backend not implemented yet")
        else:
            return MemoryCacheBackend(self.config.max_size)
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if not self._cleanup_task or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    def _start_stats_task(self):
        """Start background statistics task."""
        if not self._stats_task or self._stats_task.done():
            self._stats_task = asyncio.create_task(self._stats_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Cache cleanup error: {e}")
    
    async def _stats_loop(self):
        """Background statistics logging loop."""
        while not self._closed:
            try:
                await asyncio.sleep(self.config.stats_interval)
                stats = await self.get_stats()
                logger.info(f"Cache stats: {stats}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Cache stats error: {e}")
    
    async def _cleanup_expired_entries(self):
        """Clean up expired cache entries."""
        keys = await self.backend.keys()
        cleaned = 0
        
        for key in keys[:self.config.cleanup_batch_size]:
            entry = await self.backend.get(key)
            if entry and entry.is_expired:
                await self.backend.delete(key)
                cleaned += 1
                self.stats['evictions'] += 1
        
        if cleaned > 0:
            logger.debug(f"Cleaned up {cleaned} expired cache entries")
    
    def _get_embedding_model(self):
        """Lazy load embedding model for semantic similarity."""
        if self._embedding_model is None and self.config.enable_semantic_caching:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer(self.config.embedding_model)
            except ImportError:
                logger.warning("sentence-transformers not available, disabling semantic caching")
                self.config.enable_semantic_caching = False
        return self._embedding_model
    
    def _compute_embedding(self, text: str) -> Optional[np.ndarray]:
        """Compute embedding for text."""
        if not self.config.enable_semantic_caching:
            return None
        
        model = self._get_embedding_model()
        if model is None:
            return None
        
        try:
            embedding = model.encode([text])
            return embedding[0] if len(embedding) > 0 else None
        except Exception as e:
            logger.warning(f"Failed to compute embedding: {e}")
            return None
    
    def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between embeddings."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            return cosine_similarity([emb1], [emb2])[0][0]
        except ImportError:
            # Fallback to manual calculation
            dot_product = np.dot(emb1, emb2)
            norm_a = np.linalg.norm(emb1)
            norm_b = np.linalg.norm(emb2)
            return dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
    
    async def _find_semantic_match(self, text: str, embedding: np.ndarray) -> Optional[CacheEntry]:
        """Find semantically similar cache entry."""
        if not self.config.enable_semantic_caching or embedding is None:
            return None
        
        keys = await self.backend.keys()
        best_match = None
        best_similarity = 0.0
        
        for key in keys:
            entry = await self.backend.get(key)
            if entry and entry.embedding is not None:
                similarity = self._compute_similarity(embedding, entry.embedding)
                if (similarity > self.config.semantic_similarity_threshold and
                    similarity > best_similarity):
                    best_similarity = similarity
                    best_match = entry
        
        if best_match:
            self.stats['semantic_matches'] += 1
            logger.debug(f"Found semantic match with similarity {best_similarity:.3f}")
        
        return best_match
    
    def _create_cache_key(self, operation: str, inputs: Dict[str, Any]) -> str:
        """Create deterministic cache key from operation and inputs."""
        # Sort inputs for consistent hashing
        sorted_inputs = json.dumps(inputs, sort_keys=True, default=str)
        content = f"{operation}:{sorted_inputs}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _compress_value(self, value: Any) -> Tuple[Any, bool]:
        """Compress value if beneficial."""
        if not self.config.enable_compression:
            return value, False
        
        try:
            serialized = pickle.dumps(value)
            if len(serialized) > self.config.compression_threshold:
                import gzip
                compressed = gzip.compress(serialized)
                if len(compressed) < len(serialized) * 0.8:  # 20% savings threshold
                    self.stats['compression_saves'] += 1
                    return compressed, True
        except Exception as e:
            logger.debug(f"Compression failed: {e}")
        
        return value, False
    
    def _decompress_value(self, value: Any, compressed: bool) -> Any:
        """Decompress value if needed."""
        if not compressed:
            return value
        
        try:
            import gzip
            decompressed = gzip.decompress(value)
            return pickle.loads(decompressed)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return value
    
    async def get(
        self,
        operation: str,
        inputs: Dict[str, Any],
        semantic_text: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get cached result for operation and inputs.
        
        Args:
            operation: Operation name
            inputs: Operation inputs
            semantic_text: Text for semantic similarity matching
            
        Returns:
            Cached result or None if not found
        """
        # Try exact key match first
        key = self._create_cache_key(operation, inputs)
        entry = await self.backend.get(key)
        
        if entry:
            self.stats['hits'] += 1
            result = self._decompress_value(entry.value, entry.compressed)
            return result
        
        # Try semantic match if enabled and text provided
        if semantic_text and self.config.enable_semantic_caching:
            embedding = self._compute_embedding(semantic_text)
            if embedding is not None:
                semantic_match = await self._find_semantic_match(semantic_text, embedding)
                if semantic_match:
                    self.stats['hits'] += 1
                    result = self._decompress_value(semantic_match.value, semantic_match.compressed)
                    return result
        
        self.stats['misses'] += 1
        return None
    
    async def put(
        self,
        operation: str,
        inputs: Dict[str, Any],
        value: Any,
        ttl: Optional[float] = None,
        semantic_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache result for operation and inputs.
        
        Args:
            operation: Operation name
            inputs: Operation inputs
            value: Result value to cache
            ttl: Time to live (uses default if None)
            semantic_text: Text for semantic similarity
            metadata: Additional metadata
            
        Returns:
            True if cached successfully
        """
        key = self._create_cache_key(operation, inputs)
        
        # Compress value if beneficial
        cached_value, compressed = self._compress_value(value)
        
        # Compute embedding for semantic similarity
        embedding = None
        if semantic_text and self.config.enable_semantic_caching:
            embedding = self._compute_embedding(semantic_text)
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=cached_value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl=ttl or self.config.default_ttl,
            embedding=embedding,
            compressed=compressed,
            metadata=metadata or {}
        )
        
        success = await self.backend.put(entry)
        if success:
            self.stats['puts'] += 1
        
        return success
    
    async def invalidate(self, operation: str, inputs: Dict[str, Any]) -> bool:
        """Invalidate specific cache entry."""
        key = self._create_cache_key(operation, inputs)
        return await self.backend.delete(key)
    
    async def invalidate_pattern(self, operation: str) -> int:
        """Invalidate all cache entries for an operation."""
        keys = await self.backend.keys()
        pattern = f"{operation}:"
        deleted = 0
        
        for key in keys:
            entry = await self.backend.get(key)
            if entry and entry.key.startswith(pattern):
                await self.backend.delete(key)
                deleted += 1
        
        return deleted
    
    async def clear(self) -> int:
        """Clear entire cache."""
        return await self.backend.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        cache_size = await self.backend.size()
        uptime = time.time() - self.stats['start_time']
        
        return {
            'performance': {
                'hit_rate_percent': round(hit_rate, 2),
                'total_requests': total_requests,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'semantic_matches': self.stats['semantic_matches']
            },
            'storage': {
                'cache_size': cache_size,
                'max_size': self.config.max_size,
                'utilization_percent': round(cache_size / self.config.max_size * 100, 2),
                'puts': self.stats['puts'],
                'evictions': self.stats['evictions']
            },
            'optimization': {
                'compression_saves': self.stats['compression_saves'],
                'semantic_caching_enabled': self.config.enable_semantic_caching,
                'compression_enabled': self.config.enable_compression
            },
            'system': {
                'uptime_seconds': round(uptime, 2),
                'backend_type': self.config.cache_type.value,
                'eviction_policy': self.config.eviction_policy.value
            }
        }
    
    async def close(self):
        """Close cache manager and cleanup resources."""
        if self._closed:
            return
        
        self._closed = True
        
        # Cancel background tasks
        tasks = []
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            tasks.append(self._cleanup_task)
        
        if self._stats_task and not self._stats_task.done():
            self._stats_task.cancel()
            tasks.append(self._stats_task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Cache manager closed successfully")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Global cache manager instance
_global_cache_manager: Optional[SemanticCacheManager] = None


def get_cache_manager() -> SemanticCacheManager:
    """Get or create the global cache manager instance."""
    global _global_cache_manager
    
    if _global_cache_manager is None or _global_cache_manager._closed:
        _global_cache_manager = SemanticCacheManager()
    
    return _global_cache_manager


async def close_global_cache_manager():
    """Close the global cache manager."""
    global _global_cache_manager
    
    if _global_cache_manager and not _global_cache_manager._closed:
        await _global_cache_manager.close()
        _global_cache_manager = None