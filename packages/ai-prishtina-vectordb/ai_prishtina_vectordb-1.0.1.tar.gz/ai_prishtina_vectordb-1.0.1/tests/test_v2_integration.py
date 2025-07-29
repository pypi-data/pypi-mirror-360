"""
Integration tests for Version 0.2.0 features.

This module tests the integration of all new features:
- Multi-modal search capabilities
- Advanced caching strategies
- Performance optimizations
- Enhanced monitoring and metrics
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch

from ai_prishtina_vectordb.multimodal_search import (
    MultiModalSearchEngine,
    SearchQuery,
    ModalityType
)
from ai_prishtina_vectordb.caching import CacheManager, CacheConfig
from ai_prishtina_vectordb.performance import PerformanceManager, PerformanceConfig
from ai_prishtina_vectordb.metrics import AdvancedMetricsCollector
from ai_prishtina_vectordb.database import Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger


class TestVersion2Integration:
    """Integration tests for Version 0.2.0 features."""
    
    @pytest.fixture
    async def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        db.collection_name = "test_collection"
        db.query = AsyncMock(return_value={
            'ids': [['doc1', 'doc2', 'doc3']],
            'distances': [[0.1, 0.2, 0.3]],
            'documents': [['Document 1', 'Document 2', 'Document 3']],
            'metadatas': [[{'type': 'text'}, {'type': 'text'}, {'type': 'text'}]]
        })
        return db
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_v2_integration")
    
    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            enabled=True,
            cache_type="memory",
            max_size=100,
            ttl_seconds=3600
        )
    
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
    async def cache_manager(self, cache_config, logger):
        """Create cache manager."""
        return CacheManager(cache_config, logger)
    
    @pytest.fixture
    async def performance_manager(self, performance_config, logger):
        """Create performance manager."""
        metrics = AdvancedMetricsCollector(logger)
        return PerformanceManager(performance_config, logger, metrics)
    
    @pytest.fixture
    async def metrics_collector(self, logger):
        """Create advanced metrics collector."""
        return AdvancedMetricsCollector(logger, enable_real_time=True)
    
    @pytest.fixture
    async def search_engine(self, mock_database, logger, metrics_collector):
        """Create multi-modal search engine."""
        return MultiModalSearchEngine(
            database=mock_database,
            logger=logger,
            metrics=metrics_collector
        )
    
    @pytest.mark.asyncio
    async def test_multimodal_search_with_caching(
        self,
        search_engine,
        cache_manager,
        metrics_collector
    ):
        """Test multi-modal search with caching integration."""
        # Create search query
        query = SearchQuery(text="machine learning algorithms")
        
        # Mock text embedder
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [[0.1] * 384]
            
            # Define search function
            async def search_func():
                return await search_engine.search(query, n_results=5)
            
            # First search - should compute and cache
            cache_key = "multimodal_search_test"
            results1 = await cache_manager.get_or_compute(
                cache_key,
                search_func
            )
            
            # Second search - should use cache
            results2 = await cache_manager.get_or_compute(
                cache_key,
                search_func
            )
            
            # Results should be identical
            assert len(results1) == len(results2)
            
            # Verify caching worked (embedder called only once)
            assert mock_encode.call_count == 1
    
    @pytest.mark.asyncio
    async def test_performance_optimized_batch_search(
        self,
        search_engine,
        performance_manager,
        metrics_collector
    ):
        """Test batch search with performance optimizations."""
        # Create multiple search queries
        queries = [
            SearchQuery(text=f"query {i}")
            for i in range(20)
        ]
        
        # Mock text embedder
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [[0.1] * 384]
            
            # Define batch search function
            async def batch_search_func(query_batch):
                results = []
                for query in query_batch:
                    result = await search_engine.search(query, n_results=3)
                    results.extend(result)
                return results
            
            # Process queries in batches
            results = await performance_manager.batch_processor.process_batches(
                queries,
                batch_search_func
            )
            
            # Should process all queries
            assert len(results) > 0
            
            # Verify performance metrics were collected
            assert "batch_processing" in performance_manager.metrics.metrics
    
    @pytest.mark.asyncio
    async def test_real_time_monitoring_during_operations(
        self,
        search_engine,
        metrics_collector,
        cache_manager
    ):
        """Test real-time monitoring during search operations."""
        # Start real-time monitoring
        await metrics_collector.start_real_time_monitoring(interval=0.1)
        
        # Set up thresholds
        await metrics_collector.set_threshold(
            "system.cpu_usage",
            warning=70.0,
            error=85.0,
            critical=95.0
        )
        
        try:
            # Perform multiple operations
            with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
                mock_encode.return_value = [[0.1] * 384]
                
                # Multiple search operations
                for i in range(5):
                    query = SearchQuery(text=f"test query {i}")
                    
                    # Use cache manager for search
                    cache_key = f"search_{i}"
                    await cache_manager.get_or_compute(
                        cache_key,
                        lambda: search_engine.search(query, n_results=3)
                    )
                    
                    # Record custom metrics
                    await metrics_collector.record_metric(
                        f"search_operation_{i}",
                        float(i * 10)
                    )
            
            # Let monitoring collect some data
            await asyncio.sleep(0.3)
            
            # Verify system metrics were collected
            assert len(metrics_collector.system_metrics["timestamps"]) > 0
            assert len(metrics_collector.system_metrics["cpu_usage"]) > 0
            assert len(metrics_collector.system_metrics["memory_usage"]) > 0
            
            # Verify custom metrics were recorded
            for i in range(5):
                metric_name = f"search_operation_{i}"
                assert metric_name in metrics_collector.metrics
        
        finally:
            # Stop monitoring
            await metrics_collector.stop_real_time_monitoring()
    
    @pytest.mark.asyncio
    async def test_comprehensive_performance_report(
        self,
        performance_manager,
        metrics_collector,
        cache_manager
    ):
        """Test comprehensive performance reporting."""
        # Start performance monitoring
        await performance_manager.start_monitoring(interval=0.1)
        
        try:
            # Simulate various operations
            
            # 1. Cache operations
            for i in range(10):
                await cache_manager.cache.set(f"key_{i}", f"value_{i}")
                await cache_manager.cache.get(f"key_{i}")
            
            # 2. Memory optimization
            await performance_manager.memory_optimizer.optimize_memory_usage()
            
            # 3. Record performance metrics
            await metrics_collector.record_metric("operation_latency", 150.0)
            await metrics_collector.record_metric("throughput", 1000.0)
            await metrics_collector.record_metric("error_rate", 0.5)
            
            # Let monitoring collect data
            await asyncio.sleep(0.2)
            
            # Get comprehensive report
            performance_report = await performance_manager.get_performance_report()
            cache_stats = await cache_manager.get_cache_stats()
            metrics_export = await metrics_collector.export_metrics()
            
            # Verify performance report
            assert "config" in performance_report
            assert "stats" in performance_report
            assert "memory" in performance_report
            assert "system" in performance_report
            
            # Verify cache stats
            assert "cache_type" in cache_stats
            assert "hit_rate" in cache_stats
            
            # Verify metrics export
            metrics_data = json.loads(metrics_export)
            assert "metrics" in metrics_data
            assert "system_metrics" in metrics_data
            assert "health_score" in metrics_data
            
            # Check specific metrics
            assert "operation_latency" in metrics_data["metrics"]
            assert "throughput" in metrics_data["metrics"]
            assert "error_rate" in metrics_data["metrics"]
        
        finally:
            await performance_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_multimodal_search_with_document_processing(
        self,
        search_engine,
        cache_manager,
        performance_manager
    ):
        """Test multi-modal search with document processing and optimization."""
        # Create temporary document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a comprehensive test document for multi-modal search capabilities.")
            doc_path = f.name
        
        try:
            # Create multi-modal query
            query = SearchQuery(
                text="comprehensive test",
                document_path=doc_path,
                modality_weights={
                    ModalityType.TEXT: 0.6,
                    ModalityType.DOCUMENT: 0.4
                },
                fusion_strategy="weighted_average"
            )
            
            # Mock embedders
            with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
                mock_encode.return_value = [[0.1] * 384]
                
                # Define optimized search function
                async def optimized_search():
                    # Use performance optimization for query
                    optimized_params = await performance_manager.query_optimizer.optimize_query({
                        "query": query,
                        "n_results": 10
                    })
                    
                    # Perform search
                    return await search_engine.search(query, n_results=10)
                
                # Use cache manager for the search
                cache_key = cache_manager._generate_cache_key(
                    "multimodal_search",
                    query.text,
                    query.document_path,
                    str(query.modality_weights)
                )
                
                results = await cache_manager.get_or_compute(
                    cache_key,
                    optimized_search
                )
                
                # Verify results
                assert isinstance(results, list)
                assert len(results) <= 10
                
                # Verify that both modalities were processed
                mock_encode.assert_called()  # Text embedding
                
                # Check cache was used
                cache_stats = await cache_manager.get_cache_stats()
                assert cache_stats["total_requests"] > 0
        
        finally:
            os.unlink(doc_path)
    
    @pytest.mark.asyncio
    async def test_alert_system_integration(
        self,
        metrics_collector,
        performance_manager
    ):
        """Test alert system integration with performance monitoring."""
        alerts_received = []
        
        # Define alert callback
        async def alert_callback(alert):
            alerts_received.append(alert)
        
        # Add callback to metrics collector
        metrics_collector.add_alert_callback(alert_callback)
        
        # Set thresholds
        await metrics_collector.set_threshold(
            "memory_usage",
            warning=50.0,
            error=70.0,
            critical=90.0
        )
        
        # Start monitoring
        await performance_manager.start_monitoring(interval=0.1)
        
        try:
            # Simulate high memory usage
            await metrics_collector.record_metric("memory_usage", 75.0)  # Should trigger error alert
            await metrics_collector.record_metric("memory_usage", 95.0)  # Should trigger critical alert
            
            # Let monitoring process
            await asyncio.sleep(0.2)
            
            # Verify alerts were created and callbacks called
            assert len(alerts_received) >= 2
            
            # Check alert levels
            alert_levels = [alert.level for alert in alerts_received]
            assert any(level.value == "error" for level in alert_levels)
            assert any(level.value == "critical" for level in alert_levels)
            
            # Verify alerts are in metrics collector
            assert len(metrics_collector.alerts) >= 2
        
        finally:
            await performance_manager.stop_monitoring()
    
    @pytest.mark.asyncio
    async def test_cleanup_all_components(
        self,
        search_engine,
        cache_manager,
        performance_manager,
        metrics_collector
    ):
        """Test cleanup of all Version 0.2.0 components."""
        # Start all monitoring
        await metrics_collector.start_real_time_monitoring(interval=0.1)
        await performance_manager.start_monitoring(interval=0.1)
        
        # Add some data
        await cache_manager.cache.set("test_key", "test_value")
        await metrics_collector.record_metric("test_metric", 50.0)
        
        # Cleanup all components
        await cache_manager.cleanup()
        await performance_manager.cleanup()
        await metrics_collector.cleanup()
        
        # Verify cleanup
        assert performance_manager.monitoring_task is None
        assert metrics_collector.monitoring_task is None
        assert len(metrics_collector.metrics) == 0
        assert len(metrics_collector.alerts) == 0
