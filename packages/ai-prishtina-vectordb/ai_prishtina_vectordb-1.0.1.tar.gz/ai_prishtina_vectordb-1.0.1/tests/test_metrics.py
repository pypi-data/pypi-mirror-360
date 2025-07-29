"""
Unit tests for metrics functionality in AIPrishtina VectorDB.
"""

import pytest
import asyncio
import time
import numpy as np
from ai_prishtina_vectordb.metrics import MetricsCollector, PerformanceMonitor
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

@pytest.fixture
async def logger():
    """Fixture to create a logger."""
    logger = AIPrishtinaLogger(level="DEBUG")
    yield logger
    await logger.close()

@pytest.fixture
async def metrics_collector(logger):
    """Fixture to create a metrics collector."""
    collector = MetricsCollector(logger=logger)
    yield collector
    # Cleanup if needed
    await collector.reset()

@pytest.fixture
async def performance_monitor(logger):
    """Fixture to create a performance monitor."""
    monitor = PerformanceMonitor(logger=logger)
    yield monitor
    # Cleanup if needed
    await monitor.reset()

@pytest.mark.asyncio
async def test_metrics_collection(metrics_collector):
    """Test metrics collection."""
    # Test search metrics
    await metrics_collector.record_search(
        query="test query",
        n_results=5,
        response_time=0.1
    )
    
    metrics = await metrics_collector.get_metrics()
    assert "search_metrics" in metrics
    assert metrics["search_metrics"]["total_queries"] == 1
    
    # Test embedding metrics
    await metrics_collector.record_embedding(
        n_documents=10,
        embedding_time=0.2
    )
    
    metrics = await metrics_collector.get_metrics()
    assert "embedding_metrics" in metrics
    assert metrics["embedding_metrics"]["total_documents"] == 10

@pytest.mark.asyncio
async def test_performance_monitoring(performance_monitor):
    """Test performance monitoring."""
    async with performance_monitor.measure("test_operation"):
        await asyncio.sleep(0.1)
        
    metrics = await performance_monitor.get_metrics()
    assert "test_operation" in metrics
    assert metrics["test_operation"]["avg_time"] > 0

@pytest.mark.asyncio
async def test_metrics_reset(metrics_collector):
    """Test metrics reset."""
    # Record some metrics
    await metrics_collector.record_search(
        query="test query",
        n_results=5,
        response_time=0.1
    )
    
    # Reset metrics
    await metrics_collector.reset()
    
    # Check if metrics are reset
    metrics = await metrics_collector.get_metrics()
    assert metrics["search_metrics"]["total_queries"] == 0

@pytest.mark.asyncio
async def test_performance_thresholds(performance_monitor):
    """Test performance thresholds."""
    await performance_monitor.set_threshold("test_operation", 0.2)
    
    async with performance_monitor.measure("test_operation"):
        await asyncio.sleep(0.1)
        
    metrics = await performance_monitor.get_metrics()
    assert "test_operation" in metrics
    assert metrics["test_operation"]["avg_time"] < 0.2 