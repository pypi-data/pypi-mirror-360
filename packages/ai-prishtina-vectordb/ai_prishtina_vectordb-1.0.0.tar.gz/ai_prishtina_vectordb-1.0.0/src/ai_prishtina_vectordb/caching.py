"""
Advanced caching strategies for AI Prishtina VectorDB.

This module provides sophisticated caching mechanisms including LRU cache,
Redis-based distributed caching, and intelligent cache warming strategies.
"""

import asyncio
import hashlib
import json
import pickle
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Tuple
from collections import OrderedDict
import numpy as np

from .logger import AIPrishtinaLogger
from .metrics import MetricsCollector
from .exceptions import CacheError


@dataclass
class CacheConfig:
    """Configuration for caching strategies."""
    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600  # 1 hour default TTL
    cache_type: str = "memory"  # memory, redis, hybrid
    redis_url: Optional[str] = None
    compression_enabled: bool = True
    cache_warming_enabled: bool = True
    eviction_policy: str = "lru"  # lru, lfu, ttl
    persistence_enabled: bool = False
    persistence_path: Optional[str] = None


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() > (self.timestamp + self.ttl)
    
    def touch(self) -> None:
        """Update access information."""
        self.access_count += 1
        self.timestamp = time.time()


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(CacheStrategy):
    """In-memory LRU cache with advanced features."""
    
    def __init__(self, config: CacheConfig, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize memory cache."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="memory_cache")
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0,
            "memory_usage": 0
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache."""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                await self.delete(key)
                self.stats["misses"] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.touch()
            self.stats["hits"] += 1
            
            await self.logger.debug(f"Cache hit for key: {key}")
            return entry.value
        
        self.stats["misses"] += 1
        await self.logger.debug(f"Cache miss for key: {key}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in memory cache."""
        try:
            # Calculate size
            size_bytes = len(pickle.dumps(value))
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                size_bytes=size_bytes,
                ttl=ttl or self.config.ttl_seconds
            )
            
            # Check if we need to evict
            while len(self.cache) >= self.config.max_size:
                await self._evict_entry()
            
            # Add to cache
            self.cache[key] = entry
            self.stats["size"] = len(self.cache)
            self.stats["memory_usage"] += size_bytes
            
            await self.logger.debug(f"Cached value for key: {key}")
            return True
            
        except Exception as e:
            await self.logger.error(f"Failed to cache value for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache."""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.stats["size"] = len(self.cache)
            self.stats["memory_usage"] -= entry.size_bytes
            await self.logger.debug(f"Deleted cache entry for key: {key}")
            return True
        return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        self.cache.clear()
        self.stats["size"] = 0
        self.stats["memory_usage"] = 0
        await self.logger.info("Cleared all cache entries")
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    async def _evict_entry(self) -> None:
        """Evict entry based on eviction policy."""
        if not self.cache:
            return
        
        if self.config.eviction_policy == "lru":
            # Remove least recently used (first item)
            key, entry = self.cache.popitem(last=False)
        elif self.config.eviction_policy == "lfu":
            # Remove least frequently used
            key = min(self.cache.keys(), key=lambda k: self.cache[k].access_count)
            entry = self.cache.pop(key)
        elif self.config.eviction_policy == "ttl":
            # Remove expired entries first, then oldest
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            if expired_keys:
                key = expired_keys[0]
                entry = self.cache.pop(key)
            else:
                key, entry = self.cache.popitem(last=False)
        else:
            # Default to LRU
            key, entry = self.cache.popitem(last=False)
        
        self.stats["evictions"] += 1
        self.stats["memory_usage"] -= entry.size_bytes
        await self.logger.debug(f"Evicted cache entry for key: {key}")


class RedisCache(CacheStrategy):
    """Redis-based distributed cache."""
    
    def __init__(self, config: CacheConfig, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize Redis cache."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="redis_cache")
        self.redis_client = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }
    
    async def _get_redis_client(self):
        """Get Redis client (lazy initialization)."""
        if self.redis_client is None:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(
                    self.config.redis_url or "redis://localhost:6379"
                )
                await self.redis_client.ping()
                await self.logger.info("Connected to Redis cache")
            except Exception as e:
                await self.logger.error(f"Failed to connect to Redis: {str(e)}")
                raise CacheError(f"Redis connection failed: {str(e)}")
        
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            client = await self._get_redis_client()
            data = await client.get(f"ai_prishtina:{key}")
            
            if data is not None:
                value = pickle.loads(data)
                self.stats["hits"] += 1
                await self.logger.debug(f"Redis cache hit for key: {key}")
                return value
            
            self.stats["misses"] += 1
            await self.logger.debug(f"Redis cache miss for key: {key}")
            return None
            
        except Exception as e:
            self.stats["errors"] += 1
            await self.logger.error(f"Redis get error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in Redis cache."""
        try:
            client = await self._get_redis_client()
            data = pickle.dumps(value)
            
            ttl_seconds = int(ttl or self.config.ttl_seconds)
            await client.setex(f"ai_prishtina:{key}", ttl_seconds, data)
            
            await self.logger.debug(f"Cached value in Redis for key: {key}")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            await self.logger.error(f"Redis set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        try:
            client = await self._get_redis_client()
            result = await client.delete(f"ai_prishtina:{key}")
            
            await self.logger.debug(f"Deleted Redis cache entry for key: {key}")
            return result > 0
            
        except Exception as e:
            self.stats["errors"] += 1
            await self.logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            client = await self._get_redis_client()
            keys = await client.keys("ai_prishtina:*")
            
            if keys:
                await client.delete(*keys)
            
            await self.logger.info("Cleared all Redis cache entries")
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            await self.logger.error(f"Redis clear error: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


class HybridCache(CacheStrategy):
    """Hybrid cache combining memory and Redis."""
    
    def __init__(self, config: CacheConfig, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize hybrid cache."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="hybrid_cache")
        
        # Create L1 (memory) and L2 (Redis) caches
        memory_config = CacheConfig(
            max_size=min(config.max_size // 4, 100),  # Smaller L1 cache
            ttl_seconds=config.ttl_seconds,
            eviction_policy=config.eviction_policy
        )
        
        self.l1_cache = MemoryCache(memory_config, logger)
        self.l2_cache = RedisCache(config, logger)
        
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "promotions": 0  # L2 -> L1 promotions
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from hybrid cache (L1 first, then L2)."""
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            self.stats["l1_hits"] += 1
            return value
        
        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value is not None:
            self.stats["l2_hits"] += 1
            # Promote to L1 cache
            await self.l1_cache.set(key, value)
            self.stats["promotions"] += 1
            return value
        
        self.stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in both L1 and L2 caches."""
        l1_success = await self.l1_cache.set(key, value, ttl)
        l2_success = await self.l2_cache.set(key, value, ttl)
        
        return l1_success or l2_success
    
    async def delete(self, key: str) -> bool:
        """Delete value from both caches."""
        l1_success = await self.l1_cache.delete(key)
        l2_success = await self.l2_cache.delete(key)
        
        return l1_success or l2_success
    
    async def clear(self) -> bool:
        """Clear both caches."""
        l1_success = await self.l1_cache.clear()
        l2_success = await self.l2_cache.clear()
        
        return l1_success and l2_success
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get combined cache statistics."""
        l1_stats = await self.l1_cache.get_stats()
        l2_stats = await self.l2_cache.get_stats()
        
        total_hits = self.stats["l1_hits"] + self.stats["l2_hits"]
        total_requests = total_hits + self.stats["misses"]
        hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            **self.stats,
            "total_hit_rate": hit_rate,
            "total_requests": total_requests,
            "l1_stats": l1_stats,
            "l2_stats": l2_stats
        }


class CacheManager:
    """Main cache manager that coordinates different caching strategies."""
    
    def __init__(
        self,
        config: CacheConfig,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """Initialize cache manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="cache_manager")
        self.metrics = metrics or MetricsCollector()
        
        # Initialize cache strategy based on config
        if config.cache_type == "memory":
            self.cache = MemoryCache(config, logger)
        elif config.cache_type == "redis":
            self.cache = RedisCache(config, logger)
        elif config.cache_type == "hybrid":
            self.cache = HybridCache(config, logger)
        else:
            raise CacheError(f"Unknown cache type: {config.cache_type}")
        
        # Cache warming tasks
        self.warming_tasks: List[asyncio.Task] = []
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get_or_compute(
        self,
        key: str,
        compute_func,
        *args,
        ttl: Optional[float] = None,
        **kwargs
    ) -> Any:
        """Get value from cache or compute and cache it."""
        if not self.config.enabled:
            return await compute_func(*args, **kwargs)
        
        start_time = time.time()
        
        try:
            # Try to get from cache
            cached_value = await self.cache.get(key)
            if cached_value is not None:
                if hasattr(self.metrics, 'record_metric'):
                    await self.metrics.record_metric("cache_operation_time", time.time() - start_time)
                return cached_value
            
            # Compute value
            computed_value = await compute_func(*args, **kwargs)
            
            # Cache the computed value
            await self.cache.set(key, computed_value, ttl)
            
            if hasattr(self.metrics, 'record_metric'):
                await self.metrics.record_metric("cache_operation_time", time.time() - start_time)
            return computed_value
            
        except Exception as e:
            if hasattr(self.metrics, 'record_metric'):
                await self.metrics.record_metric("cache_operation_time", time.time() - start_time)
            await self.logger.error(f"Cache operation failed for key {key}: {str(e)}")
            # Fallback to computing without cache
            return await compute_func(*args, **kwargs)
    
    async def warm_cache(self, warming_data: List[Tuple[str, Any]]) -> None:
        """Warm cache with predefined data."""
        if not self.config.cache_warming_enabled:
            return
        
        await self.logger.info(f"Starting cache warming with {len(warming_data)} entries")
        
        for key, value in warming_data:
            try:
                await self.cache.set(key, value)
            except Exception as e:
                await self.logger.warning(f"Failed to warm cache for key {key}: {str(e)}")
        
        await self.logger.info("Cache warming completed")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        cache_stats = await self.cache.get_stats()
        
        return {
            "cache_type": self.config.cache_type,
            "enabled": self.config.enabled,
            "max_size": self.config.max_size,
            "ttl_seconds": self.config.ttl_seconds,
            **cache_stats
        }
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        # This is a simplified implementation
        # In practice, would need pattern matching support
        await self.logger.info(f"Invalidating cache entries matching pattern: {pattern}")
        return 0
    
    async def cleanup(self) -> None:
        """Cleanup cache resources."""
        # Cancel warming tasks
        for task in self.warming_tasks:
            if not task.done():
                task.cancel()
        
        # Clear cache if needed
        if hasattr(self.cache, 'redis_client') and self.cache.redis_client:
            await self.cache.redis_client.close()
        
        await self.logger.info("Cache cleanup completed")
