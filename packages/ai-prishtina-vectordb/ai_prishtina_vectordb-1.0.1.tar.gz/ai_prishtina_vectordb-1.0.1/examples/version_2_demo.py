#!/usr/bin/env python3
"""
AI Prishtina VectorDB Version 0.2.0 Feature Demonstration

This script demonstrates all the new features introduced in Version 0.2.0:
- Multi-modal search capabilities
- Advanced caching strategies
- Performance optimizations
- Enhanced monitoring and metrics
"""

import asyncio
import tempfile
import os
import sys
import time
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_prishtina_vectordb.multimodal_search import (
    MultiModalSearchEngine,
    SearchQuery,
    ModalityType
)
from ai_prishtina_vectordb.caching import CacheManager, CacheConfig
from ai_prishtina_vectordb.performance import PerformanceManager, PerformanceConfig
from ai_prishtina_vectordb.metrics import AdvancedMetricsCollector
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
from unittest.mock import Mock, AsyncMock


async def demo_caching_features():
    """Demonstrate advanced caching capabilities."""
    print("\n🗄️  ADVANCED CACHING DEMONSTRATION")
    print("=" * 50)
    
    # Configure different cache types
    cache_configs = [
        ("Memory Cache", CacheConfig(cache_type="memory", max_size=100)),
        ("Hybrid Cache", CacheConfig(cache_type="hybrid", max_size=100)),
    ]
    
    for cache_name, config in cache_configs:
        print(f"\n📦 Testing {cache_name}")
        
        cache_manager = CacheManager(config)
        
        # Simulate expensive computation
        async def expensive_computation(x):
            await asyncio.sleep(0.1)  # Simulate work
            return x ** 2
        
        # Test cache performance
        start_time = time.time()
        
        # First call - should compute
        result1 = await cache_manager.get_or_compute(
            "computation_5", 
            expensive_computation, 
            5
        )
        first_call_time = time.time() - start_time
        
        # Second call - should use cache
        start_time = time.time()
        result2 = await cache_manager.get_or_compute(
            "computation_5", 
            expensive_computation, 
            5
        )
        second_call_time = time.time() - start_time
        
        print(f"   First call (computed): {result1} in {first_call_time:.3f}s")
        print(f"   Second call (cached): {result2} in {second_call_time:.3f}s")
        print(f"   Speedup: {first_call_time/second_call_time:.1f}x faster")
        
        # Get cache statistics
        stats = await cache_manager.get_cache_stats()
        print(f"   Cache hit rate: {stats.get('hit_rate', 0):.2%}")
        
        await cache_manager.cleanup()


async def demo_performance_optimizations():
    """Demonstrate performance optimization features."""
    print("\n⚡ PERFORMANCE OPTIMIZATION DEMONSTRATION")
    print("=" * 50)
    
    # Configure performance manager
    perf_config = PerformanceConfig(
        batch_size=20,
        max_workers=4,
        enable_parallel_processing=True,
        enable_memory_optimization=True,
        enable_adaptive_batching=True
    )
    
    logger = AIPrishtinaLogger(name="performance_demo")
    metrics = AdvancedMetricsCollector(logger)
    perf_manager = PerformanceManager(perf_config, logger, metrics)
    
    print("🔧 Starting performance monitoring...")
    await perf_manager.start_monitoring(interval=1.0)
    
    try:
        # Demonstrate batch processing
        print("\n📊 Batch Processing Test")
        
        # Create large dataset
        large_dataset = list(range(1000))
        
        async def process_batch(batch):
            # Simulate processing time
            await asyncio.sleep(0.01)
            return [x * 2 + 1 for x in batch]
        
        start_time = time.time()
        results = await perf_manager.batch_processor.process_batches(
            large_dataset, 
            process_batch
        )
        processing_time = time.time() - start_time
        
        print(f"   Processed {len(results)} items in {processing_time:.2f}s")
        print(f"   Throughput: {len(results)/processing_time:.0f} items/second")
        
        # Demonstrate memory optimization
        print("\n🧠 Memory Optimization Test")
        memory_stats_before = await perf_manager.memory_optimizer.monitor_memory_usage()
        
        # Create some memory pressure
        large_data = [list(range(1000)) for _ in range(100)]
        
        memory_stats_after = await perf_manager.memory_optimizer.monitor_memory_usage()
        optimization_result = await perf_manager.memory_optimizer.optimize_memory_usage()
        
        print(f"   Memory before: {memory_stats_before['rss_mb']:.1f} MB")
        print(f"   Memory after data creation: {memory_stats_after['rss_mb']:.1f} MB")
        print(f"   Memory freed: {optimization_result['memory_freed_mb']:.1f} MB")
        
        # Clean up
        del large_data
        
        # Get performance report
        print("\n📈 Performance Report")
        report = await perf_manager.get_performance_report()
        
        print(f"   CPU Usage: {report['system']['cpu_percent']:.1f}%")
        print(f"   Memory Usage: {report['system']['memory_percent']:.1f}%")
        print(f"   Operations Count: {report['stats']['operations_count']}")
        
    finally:
        await perf_manager.stop_monitoring()
        await perf_manager.cleanup()


async def demo_enhanced_metrics():
    """Demonstrate enhanced monitoring and metrics."""
    print("\n📊 ENHANCED METRICS & MONITORING DEMONSTRATION")
    print("=" * 50)
    
    logger = AIPrishtinaLogger(name="metrics_demo")
    metrics = AdvancedMetricsCollector(logger, enable_real_time=True)
    
    # Set up alerting
    alerts_received = []
    
    async def alert_handler(alert):
        alerts_received.append(alert)
        print(f"   🚨 ALERT: {alert.level.value.upper()} - {alert.message}")
    
    metrics.add_alert_callback(alert_handler)
    
    # Configure thresholds
    await metrics.set_threshold(
        "response_time",
        warning=100.0,
        error=200.0,
        critical=500.0
    )
    
    await metrics.set_threshold(
        "error_rate",
        warning=5.0,
        error=10.0,
        critical=20.0
    )
    
    print("🔍 Starting real-time monitoring...")
    await metrics.start_real_time_monitoring(interval=0.5)
    
    try:
        # Simulate application metrics
        print("\n📈 Recording Application Metrics")
        
        # Normal operations
        for i in range(10):
            await metrics.record_metric("response_time", 50.0 + i * 5)
            await metrics.record_metric("throughput", 1000 - i * 10)
            await metrics.record_metric("error_rate", 1.0)
            await asyncio.sleep(0.1)
        
        # Simulate performance degradation
        print("\n⚠️  Simulating Performance Issues")
        await metrics.record_metric("response_time", 150.0)  # Warning
        await metrics.record_metric("response_time", 250.0)  # Error
        await metrics.record_metric("error_rate", 15.0)      # Error
        
        # Let alerts process
        await asyncio.sleep(0.5)
        
        # Get comprehensive statistics
        print("\n📊 Metrics Statistics")
        response_stats = await metrics.get_metric_statistics("response_time")
        print(f"   Response Time - Avg: {response_stats['average']:.1f}ms")
        print(f"   Response Time - 95th percentile: {response_stats['percentile_95']:.1f}ms")
        print(f"   Response Time - Trend: {response_stats['trend']}")
        
        # System health score
        health_score = await metrics.get_system_health_score()
        print(f"   System Health Score: {health_score:.1f}/100")
        
        # Export metrics
        print("\n💾 Exporting Metrics")
        exported_data = await metrics.export_metrics()
        print(f"   Exported {len(exported_data)} characters of metrics data")
        
        print(f"\n🚨 Total Alerts Generated: {len(alerts_received)}")
        for alert in alerts_received:
            print(f"   - {alert.level.value}: {alert.metric_name} = {alert.metric_value}")
        
    finally:
        await metrics.stop_real_time_monitoring()
        await metrics.cleanup()


async def demo_multimodal_search():
    """Demonstrate multi-modal search capabilities."""
    print("\n🔍 MULTI-MODAL SEARCH DEMONSTRATION")
    print("=" * 50)
    
    # Create mock database
    mock_db = Mock()
    mock_db.collection_name = "demo_collection"
    mock_db.query = AsyncMock(return_value={
        'ids': [['doc1', 'doc2', 'doc3']],
        'distances': [[0.1, 0.2, 0.3]],
        'documents': [['AI research paper', 'Machine learning tutorial', 'Deep learning guide']],
        'metadatas': [[{'type': 'text'}, {'type': 'text'}, {'type': 'text'}]]
    })
    
    logger = AIPrishtinaLogger(name="multimodal_demo")
    metrics = AdvancedMetricsCollector(logger)
    
    # Create search engine
    search_engine = MultiModalSearchEngine(
        database=mock_db,
        logger=logger,
        metrics=metrics
    )
    
    # Mock the text embedder
    search_engine.text_embedder.encode = AsyncMock(return_value=[[0.1] * 384])
    
    print("🔤 Text-only Search")
    text_query = SearchQuery(text="artificial intelligence machine learning")
    text_results = await search_engine.search(text_query, n_results=3)
    
    print(f"   Found {len(text_results)} results")
    for i, result in enumerate(text_results):
        print(f"   {i+1}. Score: {result.score:.3f} - {result.content}")
    
    # Create temporary document for multi-modal search
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This document discusses advanced machine learning techniques and neural networks.")
        doc_path = f.name
    
    try:
        print("\n📄 Multi-modal Search (Text + Document)")
        multimodal_query = SearchQuery(
            text="neural networks",
            document_path=doc_path,
            modality_weights={
                ModalityType.TEXT: 0.7,
                ModalityType.DOCUMENT: 0.3
            },
            fusion_strategy="weighted_average"
        )
        
        multimodal_results = await search_engine.search(multimodal_query, n_results=3)
        
        print(f"   Found {len(multimodal_results)} results")
        for i, result in enumerate(multimodal_results):
            print(f"   {i+1}. Score: {result.score:.3f}")
            print(f"       Modality scores: {result.modality_scores}")
            print(f"       Content: {result.content}")
    
    finally:
        os.unlink(doc_path)


async def demo_integrated_features():
    """Demonstrate all features working together."""
    print("\n🎯 INTEGRATED FEATURES DEMONSTRATION")
    print("=" * 50)
    
    # Set up all components
    logger = AIPrishtinaLogger(name="integrated_demo")
    metrics = AdvancedMetricsCollector(logger)
    
    cache_config = CacheConfig(cache_type="memory", max_size=50)
    cache_manager = CacheManager(cache_config, logger, metrics)
    
    perf_config = PerformanceConfig(batch_size=10, max_workers=2)
    perf_manager = PerformanceManager(perf_config, logger, metrics)
    
    print("🚀 Starting integrated system...")
    await metrics.start_real_time_monitoring(interval=1.0)
    await perf_manager.start_monitoring(interval=1.0)
    
    try:
        # Simulate a complex workflow
        print("\n⚙️  Running Complex Workflow")
        
        # Step 1: Batch processing with caching
        async def cached_computation(x):
            # Simulate expensive computation
            await asyncio.sleep(0.01)
            return x ** 2 + x + 1
        
        items = list(range(50))
        
        async def process_batch_with_cache(batch):
            results = []
            for item in batch:
                cache_key = f"computation_{item}"
                result = await cache_manager.get_or_compute(
                    cache_key,
                    cached_computation,
                    item
                )
                results.append(result)
            return results
        
        # Process with performance optimization
        start_time = time.time()
        results = await perf_manager.batch_processor.process_batches(
            items,
            process_batch_with_cache
        )
        processing_time = time.time() - start_time
        
        # Record metrics
        await metrics.record_metric("workflow_time", processing_time * 1000)
        await metrics.record_metric("items_processed", len(results))
        await metrics.record_metric("throughput", len(results) / processing_time)
        
        print(f"   Processed {len(results)} items in {processing_time:.2f}s")
        
        # Get comprehensive system status
        print("\n📊 System Status")
        cache_stats = await cache_manager.get_cache_stats()
        perf_report = await perf_manager.get_performance_report()
        health_score = await metrics.get_system_health_score()
        
        print(f"   Cache Hit Rate: {cache_stats.get('hit_rate', 0):.2%}")
        print(f"   Memory Usage: {perf_report['memory']['rss_mb']:.1f} MB")
        print(f"   System Health: {health_score:.1f}/100")
        
        # Export final metrics
        metrics_data = await metrics.export_metrics()
        print(f"   Metrics Export Size: {len(metrics_data)} characters")
        
    finally:
        await metrics.stop_real_time_monitoring()
        await perf_manager.stop_monitoring()
        await cache_manager.cleanup()
        await perf_manager.cleanup()
        await metrics.cleanup()


async def main():
    """Run all demonstrations."""
    print("🎉 AI PRISHTINA VECTORDB VERSION 0.2.0 FEATURE DEMO")
    print("=" * 60)
    print("This demo showcases all new features in Version 0.2.0:")
    print("• Multi-modal search capabilities")
    print("• Advanced caching strategies")
    print("• Performance optimizations")
    print("• Enhanced monitoring and metrics")
    print("=" * 60)
    
    try:
        await demo_caching_features()
        await demo_performance_optimizations()
        await demo_enhanced_metrics()
        await demo_multimodal_search()
        await demo_integrated_features()
        
        print("\n🎊 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("Version 0.2.0 features are working perfectly! 🚀")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
