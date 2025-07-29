"""
Tests for performance optimizations.
"""

import pytest
import asyncio
import time
import psutil
from unittest.mock import Mock, AsyncMock, patch

from ai_prishtina_vectordb.performance import (
    PerformanceConfig,
    BatchProcessor,
    MemoryOptimizer,
    QueryOptimizer,
    ConnectionPool,
    PerformanceManager
)
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
from ai_prishtina_vectordb.metrics import MetricsCollector


class TestPerformanceConfig:
    """Test cases for PerformanceConfig."""
    
    def test_default_config(self):
        """Test default performance configuration."""
        config = PerformanceConfig()
        
        assert config.batch_size == 100
        assert config.max_workers == 4
        assert config.enable_parallel_processing is True
        assert config.enable_memory_optimization is True
        assert config.enable_query_optimization is True
        assert config.memory_threshold_mb == 1000.0
        assert config.cpu_threshold_percent == 80.0
    
    def test_custom_config(self):
        """Test custom performance configuration."""
        config = PerformanceConfig(
            batch_size=50,
            max_workers=8,
            enable_parallel_processing=False,
            memory_threshold_mb=500.0
        )
        
        assert config.batch_size == 50
        assert config.max_workers == 8
        assert config.enable_parallel_processing is False
        assert config.memory_threshold_mb == 500.0


class TestBatchProcessor:
    """Test cases for BatchProcessor."""
    
    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            batch_size=5,
            max_workers=2,
            enable_parallel_processing=True,
            enable_adaptive_batching=True
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_batch_processor")
    
    @pytest.fixture
    def metrics(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    @pytest.fixture
    async def batch_processor(self, performance_config, logger, metrics):
        """Create batch processor."""
        return BatchProcessor(performance_config, logger, metrics)
    
    @pytest.mark.asyncio
    async def test_process_batches_sequential(self, batch_processor):
        """Test sequential batch processing."""
        batch_processor.config.enable_parallel_processing = False
        
        items = list(range(10))
        
        async def mock_process_func(batch):
            # Simulate processing time
            await asyncio.sleep(0.01)
            return [item * 2 for item in batch]
        
        results = await batch_processor.process_batches(items, mock_process_func)
        
        # Should process all items
        assert len(results) == 10
        assert results == [item * 2 for item in items]
    
    @pytest.mark.asyncio
    async def test_process_batches_parallel(self, batch_processor):
        """Test parallel batch processing."""
        items = list(range(10))
        
        async def mock_process_func(batch):
            await asyncio.sleep(0.01)
            return [item * 2 for item in batch]
        
        results = await batch_processor.process_batches(items, mock_process_func)
        
        # Should process all items
        assert len(results) == 10
        assert results == [item * 2 for item in items]
    
    @pytest.mark.asyncio
    async def test_empty_items(self, batch_processor):
        """Test processing empty items list."""
        async def mock_process_func(batch):
            return batch
        
        results = await batch_processor.process_batches([], mock_process_func)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_adaptive_batch_sizing(self, batch_processor):
        """Test adaptive batch sizing."""
        items = list(range(100))
        
        # Mock system resources to trigger batch size adjustment
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu:
            
            mock_memory.return_value.percent = 90  # High memory usage
            mock_cpu.return_value = 85  # High CPU usage
            
            async def mock_process_func(batch):
                return batch
            
            optimal_size = await batch_processor._get_optimal_batch_size(100)
            
            # Should reduce batch size due to high resource usage
            assert optimal_size <= batch_processor.config.batch_size
    
    @pytest.mark.asyncio
    async def test_batch_processing_error_handling(self, batch_processor):
        """Test error handling in batch processing."""
        items = list(range(5))
        
        async def failing_process_func(batch):
            if batch[0] == 2:  # Fail on third batch
                raise ValueError("Processing failed")
            return batch
        
        with pytest.raises(Exception):
            await batch_processor.process_batches(items, failing_process_func)


class TestMemoryOptimizer:
    """Test cases for MemoryOptimizer."""
    
    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            enable_memory_optimization=True,
            memory_threshold_mb=100.0
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_memory_optimizer")
    
    @pytest.fixture
    async def memory_optimizer(self, performance_config, logger):
        """Create memory optimizer."""
        return MemoryOptimizer(performance_config, logger)
    
    @pytest.mark.asyncio
    async def test_optimize_memory_usage(self, memory_optimizer):
        """Test memory optimization."""
        result = await memory_optimizer.optimize_memory_usage()
        
        assert "optimized" in result
        assert "initial_memory_mb" in result
        assert "final_memory_mb" in result
        assert "memory_freed_mb" in result
    
    @pytest.mark.asyncio
    async def test_memory_optimization_disabled(self, performance_config, logger):
        """Test memory optimization when disabled."""
        performance_config.enable_memory_optimization = False
        memory_optimizer = MemoryOptimizer(performance_config, logger)
        
        result = await memory_optimizer.optimize_memory_usage()
        
        assert result["optimized"] is False
        assert result["reason"] == "Memory optimization disabled"
    
    def test_memory_efficient_generator(self, memory_optimizer):
        """Test memory efficient generator."""
        items = list(range(100))
        chunk_size = 10
        
        chunks = list(memory_optimizer.memory_efficient_generator(items, chunk_size))
        
        assert len(chunks) == 10
        assert all(len(chunk) == chunk_size for chunk in chunks)
        
        # Verify all items are included
        flattened = [item for chunk in chunks for item in chunk]
        assert flattened == items
    
    @pytest.mark.asyncio
    async def test_monitor_memory_usage(self, memory_optimizer):
        """Test memory usage monitoring."""
        memory_stats = await memory_optimizer.monitor_memory_usage()
        
        assert "rss_mb" in memory_stats
        assert "vms_mb" in memory_stats
        assert "percent" in memory_stats
        assert "available_mb" in memory_stats
        
        # All values should be positive
        assert all(value >= 0 for value in memory_stats.values())


class TestQueryOptimizer:
    """Test cases for QueryOptimizer."""
    
    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            enable_query_optimization=True
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_query_optimizer")
    
    @pytest.fixture
    async def query_optimizer(self, performance_config, logger):
        """Create query optimizer."""
        return QueryOptimizer(performance_config, logger)
    
    @pytest.mark.asyncio
    async def test_optimize_query_large_results(self, query_optimizer):
        """Test query optimization for large result sets."""
        query_params = {
            "n_results": 2000,
            "query_text": "test query"
        }
        
        optimized = await query_optimizer.optimize_query(query_params)
        
        # Should limit n_results for large queries
        assert optimized["n_results"] <= 500
        assert optimized["_original_n_results"] == 2000
    
    @pytest.mark.asyncio
    async def test_optimize_query_embeddings(self, query_optimizer):
        """Test query optimization for embeddings."""
        import numpy as np
        
        embeddings = [
            np.random.rand(384).tolist(),
            np.random.rand(384).tolist()
        ]
        
        query_params = {
            "query_embeddings": embeddings,
            "n_results": 10
        }
        
        optimized = await query_optimizer.optimize_query(query_params)
        
        # Should normalize embeddings
        assert "query_embeddings" in optimized
        assert len(optimized["query_embeddings"]) == 2
    
    @pytest.mark.asyncio
    async def test_query_optimization_disabled(self, performance_config, logger):
        """Test query optimization when disabled."""
        performance_config.enable_query_optimization = False
        query_optimizer = QueryOptimizer(performance_config, logger)
        
        original_params = {"n_results": 1000, "query_text": "test"}
        optimized = await query_optimizer.optimize_query(original_params)
        
        # Should return unchanged params
        assert optimized == original_params
    
    @pytest.mark.asyncio
    async def test_analyze_query_performance(self, query_optimizer):
        """Test query performance analysis."""
        query_id = "test_query"
        execution_time = 2.5
        result_count = 100
        
        await query_optimizer.analyze_query_performance(query_id, execution_time, result_count)
        
        # Should track statistics
        assert query_id in query_optimizer.query_stats
        stats = query_optimizer.query_stats[query_id]
        assert stats["executions"] == 1
        assert stats["total_time"] == execution_time
        assert stats["avg_time"] == execution_time
        assert stats["total_results"] == result_count


class TestConnectionPool:
    """Test cases for ConnectionPool."""
    
    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            enable_connection_pooling=True,
            max_workers=3
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_connection_pool")
    
    @pytest.fixture
    async def connection_pool(self, performance_config, logger):
        """Create connection pool."""
        return ConnectionPool(performance_config, logger)
    
    @pytest.mark.asyncio
    async def test_get_and_return_connection(self, connection_pool):
        """Test getting and returning connections."""
        # Get connection
        conn1 = await connection_pool.get_connection()
        assert conn1 is not None
        assert connection_pool.active_connections == 1
        
        # Return connection
        await connection_pool.return_connection(conn1)
        
        # Get connection again (should reuse)
        conn2 = await connection_pool.get_connection()
        assert conn2 == conn1
    
    @pytest.mark.asyncio
    async def test_connection_pool_limit(self, connection_pool):
        """Test connection pool size limit."""
        connections = []
        
        # Get connections up to limit
        for i in range(connection_pool.pool_size):
            conn = await connection_pool.get_connection()
            connections.append(conn)
        
        assert connection_pool.active_connections == connection_pool.pool_size
        
        # Return all connections
        for conn in connections:
            await connection_pool.return_connection(conn)
    
    @pytest.mark.asyncio
    async def test_connection_pooling_disabled(self, performance_config, logger):
        """Test connection pool when disabled."""
        performance_config.enable_connection_pooling = False
        connection_pool = ConnectionPool(performance_config, logger)
        
        conn = await connection_pool.get_connection()
        assert conn is None
        
        await connection_pool.return_connection(conn)
        # Should not raise error
    
    @pytest.mark.asyncio
    async def test_close_all_connections(self, connection_pool):
        """Test closing all connections."""
        # Create some connections
        connections = []
        for i in range(3):
            conn = await connection_pool.get_connection()
            connections.append(conn)
            await connection_pool.return_connection(conn)
        
        # Close all
        await connection_pool.close_all()
        
        assert connection_pool.active_connections == 0
        assert connection_pool.connections.empty()


class TestPerformanceManager:
    """Test cases for PerformanceManager."""
    
    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            batch_size=10,
            max_workers=2,
            enable_parallel_processing=True,
            enable_memory_optimization=True,
            enable_query_optimization=True
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_performance_manager")
    
    @pytest.fixture
    def metrics(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    @pytest.fixture
    async def performance_manager(self, performance_config, logger, metrics):
        """Create performance manager."""
        return PerformanceManager(performance_config, logger, metrics)
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, performance_manager):
        """Test starting and stopping performance monitoring."""
        # Start monitoring
        await performance_manager.start_monitoring(interval=0.1)
        assert performance_manager.monitoring_task is not None
        
        # Let it run briefly
        await asyncio.sleep(0.2)
        
        # Stop monitoring
        await performance_manager.stop_monitoring()
        assert performance_manager.monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_get_performance_report(self, performance_manager):
        """Test getting performance report."""
        report = await performance_manager.get_performance_report()
        
        assert "config" in report
        assert "stats" in report
        assert "memory" in report
        assert "system" in report
        
        # Check config section
        config = report["config"]
        assert "batch_size" in config
        assert "max_workers" in config
        assert "parallel_processing" in config
        
        # Check system section
        system = report["system"]
        assert "cpu_percent" in system
        assert "memory_percent" in system
        assert "disk_usage" in system
    
    @pytest.mark.asyncio
    async def test_cleanup(self, performance_manager):
        """Test performance manager cleanup."""
        # Start monitoring first
        await performance_manager.start_monitoring(interval=0.1)
        
        # Cleanup
        await performance_manager.cleanup()
        
        # Should stop monitoring and close connections
        assert performance_manager.monitoring_task is None
