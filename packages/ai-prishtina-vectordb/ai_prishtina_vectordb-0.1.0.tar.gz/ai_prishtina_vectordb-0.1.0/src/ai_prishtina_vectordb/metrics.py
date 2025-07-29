"""
Metrics and monitoring functionality for AIPrishtina VectorDB.
"""

import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from .logger import AIPrishtinaLogger

class MetricsCollector:
    """Collects and manages metrics for AIPrishtina VectorDB."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize metrics collector.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or AIPrishtinaLogger()
        self.metrics = {
            "search_metrics": {
                "total_queries": 0,
                "total_results": 0,
                "avg_response_time": 0.0
            },
            "embedding_metrics": {
                "total_documents": 0,
                "total_embedding_time": 0.0,
                "avg_embedding_time": 0.0
            }
        }
        
    async def record_search(
        self,
        query: str,
        n_results: int,
        response_time: float
    ) -> None:
        """Record search metrics.
        
        Args:
            query: Search query
            n_results: Number of results
            response_time: Response time in seconds
        """
        self.metrics["search_metrics"]["total_queries"] += 1
        self.metrics["search_metrics"]["total_results"] += n_results
        
        # Update average response time
        current_avg = self.metrics["search_metrics"]["avg_response_time"]
        current_count = self.metrics["search_metrics"]["total_queries"]
        self.metrics["search_metrics"]["avg_response_time"] = (
            (current_avg * (current_count - 1) + response_time) / current_count
        )
        
        await self.logger.debug(f"Recorded search metrics: {query}")
        
    async def record_embedding(
        self,
        n_documents: int,
        embedding_time: float
    ) -> None:
        """Record embedding metrics.
        
        Args:
            n_documents: Number of documents embedded
            embedding_time: Embedding time in seconds
        """
        self.metrics["embedding_metrics"]["total_documents"] += n_documents
        self.metrics["embedding_metrics"]["total_embedding_time"] += embedding_time
        
        # Update average embedding time
        current_avg = self.metrics["embedding_metrics"]["avg_embedding_time"]
        current_count = self.metrics["embedding_metrics"]["total_documents"]
        self.metrics["embedding_metrics"]["avg_embedding_time"] = (
            (current_avg * (current_count - n_documents) + embedding_time) / current_count
        )
        
        await self.logger.debug(f"Recorded embedding metrics: {n_documents} documents")
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics.
        
        Returns:
            Dict containing current metrics
        """
        return self.metrics
        
    async def reset(self) -> None:
        """Reset all metrics to initial values."""
        self.metrics = {
            "search_metrics": {
                "total_queries": 0,
                "total_results": 0,
                "avg_response_time": 0.0
            },
            "embedding_metrics": {
                "total_documents": 0,
                "total_embedding_time": 0.0,
                "avg_embedding_time": 0.0
            }
        }
        await self.logger.debug("Reset all metrics")

class PerformanceMonitor:
    """Monitors performance of operations in AIPrishtina VectorDB."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize performance monitor.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or AIPrishtinaLogger()
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.thresholds: Dict[str, float] = {}
        
    @asynccontextmanager
    async def measure(self, operation: str):
        """Measure execution time of an operation.
        
        Args:
            operation: Name of the operation to measure
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            await self._record_operation(operation, duration)
            
    async def _record_operation(self, operation: str, duration: float) -> None:
        """Record operation metrics.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
        """
        if operation not in self.metrics:
            self.metrics[operation] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0
            }
            
        metrics = self.metrics[operation]
        metrics["count"] += 1
        metrics["total_time"] += duration
        metrics["avg_time"] = metrics["total_time"] / metrics["count"]
        metrics["min_time"] = min(metrics["min_time"], duration)
        metrics["max_time"] = max(metrics["max_time"], duration)
        
        await self.logger.debug(f"Recorded operation metrics: {operation}")
        
    def set_threshold(self, operation: str, threshold: float) -> None:
        """Set performance threshold for an operation.
        
        Args:
            operation: Operation name
            threshold: Threshold in seconds
        """
        self.thresholds[operation] = threshold
        asyncio.create_task(self.logger.debug(f"Set threshold for {operation}: {threshold}s"))
        
    def is_threshold_exceeded(self, operation: str) -> bool:
        """Check if operation exceeds its threshold.
        
        Args:
            operation: Operation name
            
        Returns:
            True if threshold is exceeded, False otherwise
        """
        if operation not in self.metrics or operation not in self.thresholds:
            return False
            
        return self.metrics[operation]["avg_time"] > self.thresholds[operation]
        
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current performance metrics.
        
        Returns:
            Dict containing current metrics
        """
        return self.metrics 