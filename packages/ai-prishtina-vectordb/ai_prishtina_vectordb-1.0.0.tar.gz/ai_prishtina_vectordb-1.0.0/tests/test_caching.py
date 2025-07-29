"""
Tests for advanced caching strategies.
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, AsyncMock, patch

from ai_prishtina_vectordb.caching import (
    CacheConfig,
    CacheEntry,
    MemoryCache,
    RedisCache,
    HybridCache,
    CacheManager
)
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
from ai_prishtina_vectordb.metrics import MetricsCollector


class TestCacheEntry:
    """Test cases for CacheEntry."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            timestamp=time.time(),
            ttl=3600
        )
        
        assert entry.key == "test_key"
        assert entry.value == "test_value"
        assert entry.access_count == 0
        assert entry.ttl == 3600
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration."""
        # Create expired entry
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            timestamp=time.time() - 7200,  # 2 hours ago
            ttl=3600  # 1 hour TTL
        )
        
        assert entry.is_expired() is True
        
        # Create non-expired entry
        entry2 = CacheEntry(
            key="test_key2",
            value="test_value2",
            timestamp=time.time(),
            ttl=3600
        )
        
        assert entry2.is_expired() is False
    
    def test_cache_entry_touch(self):
        """Test cache entry touch functionality."""
        entry = CacheEntry(
            key="test_key",
            value="test_value",
            timestamp=time.time() - 100
        )
        
        initial_count = entry.access_count
        initial_timestamp = entry.timestamp
        
        entry.touch()
        
        assert entry.access_count == initial_count + 1
        assert entry.timestamp > initial_timestamp


class TestMemoryCache:
    """Test cases for MemoryCache."""
    
    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            max_size=10,
            ttl_seconds=3600,
            eviction_policy="lru"
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_cache")
    
    @pytest.fixture
    async def memory_cache(self, cache_config, logger):
        """Create memory cache."""
        return MemoryCache(cache_config, logger)
    
    @pytest.mark.asyncio
    async def test_set_and_get(self, memory_cache):
        """Test basic set and get operations."""
        key = "test_key"
        value = "test_value"
        
        success = await memory_cache.set(key, value)
        assert success is True
        
        retrieved_value = await memory_cache.get(key)
        assert retrieved_value == value
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, memory_cache):
        """Test cache miss."""
        value = await memory_cache.get("nonexistent_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_expiration(self, memory_cache):
        """Test cache entry expiration."""
        key = "test_key"
        value = "test_value"
        
        # Set with very short TTL
        await memory_cache.set(key, value, ttl=0.1)
        
        # Should be available immediately
        retrieved_value = await memory_cache.get(key)
        assert retrieved_value == value
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Should be expired now
        retrieved_value = await memory_cache.get(key)
        assert retrieved_value is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, memory_cache):
        """Test LRU eviction policy."""
        # Fill cache to capacity
        for i in range(10):
            await memory_cache.set(f"key_{i}", f"value_{i}")
        
        # Access first key to make it recently used
        await memory_cache.get("key_0")
        
        # Add one more item to trigger eviction
        await memory_cache.set("key_10", "value_10")
        
        # key_0 should still be there (recently used)
        assert await memory_cache.get("key_0") == "value_0"
        
        # key_1 should be evicted (least recently used)
        assert await memory_cache.get("key_1") is None
    
    @pytest.mark.asyncio
    async def test_delete(self, memory_cache):
        """Test cache deletion."""
        key = "test_key"
        value = "test_value"
        
        await memory_cache.set(key, value)
        assert await memory_cache.get(key) == value
        
        success = await memory_cache.delete(key)
        assert success is True
        
        assert await memory_cache.get(key) is None
    
    @pytest.mark.asyncio
    async def test_clear(self, memory_cache):
        """Test cache clearing."""
        # Add multiple items
        for i in range(5):
            await memory_cache.set(f"key_{i}", f"value_{i}")
        
        # Clear cache
        success = await memory_cache.clear()
        assert success is True
        
        # All items should be gone
        for i in range(5):
            assert await memory_cache.get(f"key_{i}") is None
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, memory_cache):
        """Test cache statistics."""
        # Generate some hits and misses
        await memory_cache.set("key1", "value1")
        await memory_cache.get("key1")  # Hit
        await memory_cache.get("key2")  # Miss
        
        stats = await memory_cache.get_stats()
        
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert stats["hit_rate"] > 0
        assert stats["total_requests"] >= 2


class TestRedisCache:
    """Test cases for RedisCache."""
    
    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            cache_type="redis",
            redis_url="redis://localhost:6379",
            ttl_seconds=3600
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_redis_cache")
    
    @pytest.fixture
    async def redis_cache(self, cache_config, logger):
        """Create Redis cache."""
        return RedisCache(cache_config, logger)
    
    @pytest.mark.asyncio
    async def test_redis_connection_error(self, redis_cache):
        """Test Redis connection error handling."""
        # Mock Redis to raise connection error
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_client.ping.side_effect = Exception("Connection failed")
            mock_redis.return_value = mock_client
            
            with pytest.raises(Exception):
                await redis_cache._get_redis_client()
    
    @pytest.mark.asyncio
    async def test_redis_operations_with_mock(self, redis_cache):
        """Test Redis operations with mocked client."""
        # Mock Redis client
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.setex.return_value = True
        mock_client.delete.return_value = 1
        
        with patch('redis.asyncio.from_url', return_value=mock_client):
            # Test set operation
            success = await redis_cache.set("test_key", "test_value")
            assert success is True
            
            # Test get operation (miss)
            value = await redis_cache.get("test_key")
            assert value is None
            
            # Test delete operation
            success = await redis_cache.delete("test_key")
            assert success is True


class TestHybridCache:
    """Test cases for HybridCache."""
    
    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            cache_type="hybrid",
            max_size=100,
            redis_url="redis://localhost:6379",
            ttl_seconds=3600
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_hybrid_cache")
    
    @pytest.fixture
    async def hybrid_cache(self, cache_config, logger):
        """Create hybrid cache."""
        return HybridCache(cache_config, logger)
    
    @pytest.mark.asyncio
    async def test_l1_cache_hit(self, hybrid_cache):
        """Test L1 cache hit."""
        key = "test_key"
        value = "test_value"
        
        # Set in L1 cache directly
        await hybrid_cache.l1_cache.set(key, value)
        
        # Should get from L1
        retrieved_value = await hybrid_cache.get(key)
        assert retrieved_value == value
        assert hybrid_cache.stats["l1_hits"] >= 1
    
    @pytest.mark.asyncio
    async def test_cache_promotion(self, hybrid_cache):
        """Test L2 to L1 cache promotion."""
        key = "test_key"
        value = "test_value"
        
        # Mock L2 cache to return value
        with patch.object(hybrid_cache.l2_cache, 'get', new_callable=AsyncMock) as mock_l2_get:
            mock_l2_get.return_value = value
            
            # Should get from L2 and promote to L1
            retrieved_value = await hybrid_cache.get(key)
            assert retrieved_value == value
            assert hybrid_cache.stats["l2_hits"] >= 1
            assert hybrid_cache.stats["promotions"] >= 1


class TestCacheManager:
    """Test cases for CacheManager."""
    
    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            enabled=True,
            cache_type="memory",
            max_size=50,
            ttl_seconds=3600
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_cache_manager")
    
    @pytest.fixture
    def metrics(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    @pytest.fixture
    async def cache_manager(self, cache_config, logger, metrics):
        """Create cache manager."""
        return CacheManager(cache_config, logger, metrics)
    
    @pytest.mark.asyncio
    async def test_get_or_compute_cache_hit(self, cache_manager):
        """Test get_or_compute with cache hit."""
        key = "test_key"
        value = "cached_value"
        
        # Pre-populate cache
        await cache_manager.cache.set(key, value)
        
        # Mock compute function
        compute_func = AsyncMock(return_value="computed_value")
        
        result = await cache_manager.get_or_compute(key, compute_func)
        
        # Should return cached value, not computed
        assert result == value
        compute_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_or_compute_cache_miss(self, cache_manager):
        """Test get_or_compute with cache miss."""
        key = "test_key"
        computed_value = "computed_value"
        
        # Mock compute function
        compute_func = AsyncMock(return_value=computed_value)
        
        result = await cache_manager.get_or_compute(key, compute_func)
        
        # Should return computed value
        assert result == computed_value
        compute_func.assert_called_once()
        
        # Value should now be cached
        cached_value = await cache_manager.cache.get(key)
        assert cached_value == computed_value
    
    @pytest.mark.asyncio
    async def test_cache_disabled(self, cache_config, logger, metrics):
        """Test cache manager with caching disabled."""
        cache_config.enabled = False
        cache_manager = CacheManager(cache_config, logger, metrics)
        
        compute_func = AsyncMock(return_value="computed_value")
        
        result = await cache_manager.get_or_compute("key", compute_func)
        
        # Should always compute when caching is disabled
        assert result == "computed_value"
        compute_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_warming(self, cache_manager):
        """Test cache warming functionality."""
        warming_data = [
            ("key1", "value1"),
            ("key2", "value2"),
            ("key3", "value3")
        ]
        
        await cache_manager.warm_cache(warming_data)
        
        # All values should be cached
        for key, expected_value in warming_data:
            cached_value = await cache_manager.cache.get(key)
            assert cached_value == expected_value
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, cache_manager):
        """Test cache statistics."""
        # Generate some cache activity
        await cache_manager.cache.set("key1", "value1")
        await cache_manager.cache.get("key1")
        await cache_manager.cache.get("key2")  # Miss
        
        stats = await cache_manager.get_cache_stats()
        
        assert "cache_type" in stats
        assert "enabled" in stats
        assert "max_size" in stats
        assert "hit_rate" in stats
    
    def test_generate_cache_key(self, cache_manager):
        """Test cache key generation."""
        key1 = cache_manager._generate_cache_key("prefix", "arg1", "arg2", param1="value1")
        key2 = cache_manager._generate_cache_key("prefix", "arg1", "arg2", param1="value1")
        key3 = cache_manager._generate_cache_key("prefix", "arg1", "arg3", param1="value1")
        
        # Same inputs should generate same key
        assert key1 == key2
        
        # Different inputs should generate different keys
        assert key1 != key3
    
    @pytest.mark.asyncio
    async def test_cleanup(self, cache_manager):
        """Test cache manager cleanup."""
        await cache_manager.cleanup()
        
        # Should complete without errors
        assert True
