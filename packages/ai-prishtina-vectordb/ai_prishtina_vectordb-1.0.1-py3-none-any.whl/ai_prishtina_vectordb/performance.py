"""
Performance optimizations for AI Prishtina VectorDB.

This module provides advanced performance optimization techniques including
batch processing, parallel execution, memory optimization, and query optimization.
"""

import asyncio
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
import numpy as np
from functools import wraps
import gc
import sys

from .logger import AIPrishtinaLogger
from .metrics import MetricsCollector
from .exceptions import PerformanceError


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations."""
    batch_size: int = 100
    max_workers: int = 4
    enable_parallel_processing: bool = True
    enable_memory_optimization: bool = True
    enable_query_optimization: bool = True
    memory_threshold_mb: float = 1000.0
    cpu_threshold_percent: float = 80.0
    enable_adaptive_batching: bool = True
    enable_connection_pooling: bool = True
    prefetch_size: int = 50
    compression_enabled: bool = True


class BatchProcessor:
    """Advanced batch processing with adaptive sizing."""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """Initialize batch processor."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="batch_processor")
        self.metrics = metrics or MetricsCollector()
        self.adaptive_batch_size = config.batch_size
        self.performance_history = []
    
    async def process_batches(
        self,
        items: List[Any],
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """Process items in optimized batches."""
        if not items:
            return []
        
        start_time = time.time()
        
        try:
            # Determine optimal batch size
            batch_size = await self._get_optimal_batch_size(len(items))
            
            # Create batches
            batches = [
                items[i:i + batch_size] 
                for i in range(0, len(items), batch_size)
            ]
            
            await self.logger.info(f"Processing {len(items)} items in {len(batches)} batches")
            
            # Process batches
            if self.config.enable_parallel_processing:
                results = await self._process_batches_parallel(batches, process_func, *args, **kwargs)
            else:
                results = await self._process_batches_sequential(batches, process_func, *args, **kwargs)
            
            # Flatten results
            flattened_results = []
            for batch_result in results:
                if isinstance(batch_result, list):
                    flattened_results.extend(batch_result)
                else:
                    flattened_results.append(batch_result)
            
            if hasattr(self.metrics, 'record_metric'):
                await self.metrics.record_metric("batch_processing_time", time.time() - start_time)
            await self.logger.info(f"Batch processing completed. Processed {len(flattened_results)} results")
            
            return flattened_results
            
        except Exception as e:
            if hasattr(self.metrics, 'record_metric'):
                await self.metrics.record_metric("batch_processing_time", time.time() - start_time)
            await self.logger.error(f"Batch processing failed: {str(e)}")
            raise PerformanceError(f"Batch processing failed: {str(e)}")
    
    async def _get_optimal_batch_size(self, total_items: int) -> int:
        """Determine optimal batch size based on system resources and history."""
        if not self.config.enable_adaptive_batching:
            return self.config.batch_size
        
        # Check system resources
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Adjust batch size based on resource usage
        if memory_usage > self.config.memory_threshold_mb:
            self.adaptive_batch_size = max(10, self.adaptive_batch_size // 2)
        elif cpu_usage > self.config.cpu_threshold_percent:
            self.adaptive_batch_size = max(10, self.adaptive_batch_size // 2)
        elif memory_usage < 50 and cpu_usage < 50:
            self.adaptive_batch_size = min(self.config.batch_size * 2, self.adaptive_batch_size * 2)
        
        # Consider performance history
        if len(self.performance_history) > 5:
            avg_performance = sum(self.performance_history[-5:]) / 5
            if avg_performance > 2.0:  # If average processing time > 2 seconds
                self.adaptive_batch_size = max(10, self.adaptive_batch_size // 2)
        
        return min(self.adaptive_batch_size, total_items)
    
    async def _process_batches_parallel(
        self,
        batches: List[List[Any]],
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """Process batches in parallel."""
        semaphore = asyncio.Semaphore(self.config.max_workers)
        
        async def process_single_batch(batch):
            async with semaphore:
                batch_start = time.time()
                try:
                    result = await process_func(batch, *args, **kwargs)
                    batch_time = time.time() - batch_start
                    self.performance_history.append(batch_time)
                    
                    # Keep only recent history
                    if len(self.performance_history) > 20:
                        self.performance_history = self.performance_history[-20:]
                    
                    return result
                except Exception as e:
                    await self.logger.error(f"Batch processing error: {str(e)}")
                    raise
        
        # Process all batches concurrently
        tasks = [process_single_batch(batch) for batch in batches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        successful_results = []
        for result in results:
            if isinstance(result, Exception):
                await self.logger.error(f"Batch failed: {str(result)}")
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def _process_batches_sequential(
        self,
        batches: List[List[Any]],
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """Process batches sequentially."""
        results = []
        
        for i, batch in enumerate(batches):
            batch_start = time.time()
            try:
                result = await process_func(batch, *args, **kwargs)
                results.append(result)
                
                batch_time = time.time() - batch_start
                self.performance_history.append(batch_time)
                
                await self.logger.debug(f"Processed batch {i+1}/{len(batches)} in {batch_time:.2f}s")
                
            except Exception as e:
                await self.logger.error(f"Batch {i+1} failed: {str(e)}")
                raise
        
        return results


class MemoryOptimizer:
    """Memory optimization utilities."""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize memory optimizer."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="memory_optimizer")
        self.memory_threshold = config.memory_threshold_mb * 1024 * 1024  # Convert to bytes
    
    async def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        if not self.config.enable_memory_optimization:
            return {"optimized": False, "reason": "Memory optimization disabled"}
        
        initial_memory = psutil.Process().memory_info().rss
        
        # Force garbage collection
        gc.collect()
        
        # Clear caches if available
        if hasattr(sys, '_clear_type_cache'):
            sys._clear_type_cache()
        
        final_memory = psutil.Process().memory_info().rss
        memory_freed = initial_memory - final_memory
        
        await self.logger.info(f"Memory optimization freed {memory_freed / 1024 / 1024:.2f} MB")
        
        return {
            "optimized": True,
            "initial_memory_mb": initial_memory / 1024 / 1024,
            "final_memory_mb": final_memory / 1024 / 1024,
            "memory_freed_mb": memory_freed / 1024 / 1024
        }
    
    def memory_efficient_generator(self, items: List[Any], chunk_size: int = 100):
        """Create memory-efficient generator for large datasets."""
        for i in range(0, len(items), chunk_size):
            yield items[i:i + chunk_size]
    
    async def monitor_memory_usage(self) -> Dict[str, float]:
        """Monitor current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }


class QueryOptimizer:
    """Query optimization utilities."""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize query optimizer."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="query_optimizer")
        self.query_cache = {}
        self.query_stats = {}
    
    async def optimize_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize query parameters."""
        if not self.config.enable_query_optimization:
            return query_params
        
        optimized_params = query_params.copy()
        
        # Optimize batch size based on query complexity
        if 'n_results' in optimized_params:
            n_results = optimized_params['n_results']
            if n_results > 1000:
                # For large result sets, use smaller initial fetch and pagination
                optimized_params['n_results'] = min(n_results, 500)
                optimized_params['_original_n_results'] = n_results
        
        # Optimize embedding dimensions if possible
        if 'query_embeddings' in optimized_params:
            embeddings = optimized_params['query_embeddings']
            if isinstance(embeddings, list) and len(embeddings) > 0:
                # Normalize embeddings for better performance
                normalized_embeddings = []
                for embedding in embeddings:
                    if isinstance(embedding, (list, np.ndarray)):
                        norm_embedding = np.array(embedding)
                        norm_embedding = norm_embedding / np.linalg.norm(norm_embedding)
                        normalized_embeddings.append(norm_embedding.tolist())
                    else:
                        normalized_embeddings.append(embedding)
                optimized_params['query_embeddings'] = normalized_embeddings
        
        await self.logger.debug("Query parameters optimized")
        return optimized_params
    
    async def analyze_query_performance(
        self,
        query_id: str,
        execution_time: float,
        result_count: int
    ) -> None:
        """Analyze query performance for future optimizations."""
        if query_id not in self.query_stats:
            self.query_stats[query_id] = {
                "executions": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0,
                "total_results": 0
            }
        
        stats = self.query_stats[query_id]
        stats["executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["executions"]
        stats["min_time"] = min(stats["min_time"], execution_time)
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["total_results"] += result_count
        
        # Log slow queries
        if execution_time > 5.0:  # 5 seconds threshold
            await self.logger.warning(f"Slow query detected: {query_id} took {execution_time:.2f}s")


class ConnectionPool:
    """Connection pooling for database operations."""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize connection pool."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="connection_pool")
        self.pool_size = config.max_workers
        self.connections = asyncio.Queue(maxsize=self.pool_size)
        self.active_connections = 0
        self._lock = asyncio.Lock()
    
    async def get_connection(self):
        """Get connection from pool."""
        if not self.config.enable_connection_pooling:
            return None
        
        try:
            # Try to get existing connection
            connection = self.connections.get_nowait()
            return connection
        except asyncio.QueueEmpty:
            # Create new connection if under limit
            async with self._lock:
                if self.active_connections < self.pool_size:
                    connection = await self._create_connection()
                    self.active_connections += 1
                    return connection
                else:
                    # Wait for available connection
                    return await self.connections.get()
    
    async def return_connection(self, connection):
        """Return connection to pool."""
        if not self.config.enable_connection_pooling or connection is None:
            return
        
        try:
            self.connections.put_nowait(connection)
        except asyncio.QueueFull:
            # Pool is full, close connection
            await self._close_connection(connection)
            async with self._lock:
                self.active_connections -= 1
    
    async def _create_connection(self):
        """Create new connection."""
        # Placeholder for actual connection creation
        await self.logger.debug("Created new database connection")
        return {"id": f"conn_{self.active_connections}", "created_at": time.time()}
    
    async def _close_connection(self, connection):
        """Close connection."""
        await self.logger.debug(f"Closed connection {connection.get('id', 'unknown')}")
    
    async def close_all(self):
        """Close all connections in pool."""
        while not self.connections.empty():
            try:
                connection = self.connections.get_nowait()
                await self._close_connection(connection)
            except asyncio.QueueEmpty:
                break
        
        self.active_connections = 0
        await self.logger.info("Closed all connections in pool")


class PerformanceManager:
    """Main performance manager coordinating all optimizations."""
    
    def __init__(
        self,
        config: PerformanceConfig,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """Initialize performance manager."""
        self.config = config
        self.logger = logger or AIPrishtinaLogger(name="performance_manager")
        self.metrics = metrics or MetricsCollector()
        
        # Initialize components
        self.batch_processor = BatchProcessor(config, logger, metrics)
        self.memory_optimizer = MemoryOptimizer(config, logger)
        self.query_optimizer = QueryOptimizer(config, logger)
        self.connection_pool = ConnectionPool(config, logger)
        
        # Performance monitoring
        self.monitoring_task = None
        self.performance_stats = {
            "operations_count": 0,
            "total_processing_time": 0.0,
            "avg_processing_time": 0.0,
            "memory_optimizations": 0,
            "query_optimizations": 0
        }
    
    async def start_monitoring(self, interval: float = 60.0):
        """Start performance monitoring."""
        if self.monitoring_task is not None:
            return
        
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval)
        )
        await self.logger.info("Started performance monitoring")
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        if self.monitoring_task is not None:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        await self.logger.info("Stopped performance monitoring")
    
    async def _monitoring_loop(self, interval: float):
        """Performance monitoring loop."""
        while True:
            try:
                # Monitor memory usage
                memory_stats = await self.memory_optimizer.monitor_memory_usage()
                
                # Optimize memory if threshold exceeded
                if memory_stats["rss_mb"] > self.config.memory_threshold_mb:
                    await self.memory_optimizer.optimize_memory_usage()
                    self.performance_stats["memory_optimizations"] += 1
                
                # Log performance stats
                await self.logger.debug(f"Performance stats: {self.performance_stats}")
                
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Performance monitoring error: {str(e)}")
                await asyncio.sleep(interval)
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        memory_stats = await self.memory_optimizer.monitor_memory_usage()
        
        return {
            "config": {
                "batch_size": self.config.batch_size,
                "max_workers": self.config.max_workers,
                "parallel_processing": self.config.enable_parallel_processing,
                "memory_optimization": self.config.enable_memory_optimization,
                "query_optimization": self.config.enable_query_optimization
            },
            "stats": self.performance_stats,
            "memory": memory_stats,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }
    
    async def cleanup(self):
        """Cleanup performance manager resources."""
        await self.stop_monitoring()
        await self.connection_pool.close_all()
        await self.logger.info("Performance manager cleanup completed")
