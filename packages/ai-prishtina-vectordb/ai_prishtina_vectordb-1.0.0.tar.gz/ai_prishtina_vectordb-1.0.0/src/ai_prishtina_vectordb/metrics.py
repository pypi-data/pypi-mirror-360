"""
Enhanced metrics and monitoring functionality for AIPrishtina VectorDB.

This module provides comprehensive monitoring capabilities including real-time metrics,
alerting, performance tracking, and advanced analytics.
"""

import time
import asyncio
import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, deque

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


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a monitoring alert."""
    id: str
    level: AlertLevel
    message: str
    timestamp: datetime
    metric_name: str
    metric_value: float
    threshold: float
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class MetricThreshold:
    """Defines thresholds for metrics."""
    warning_threshold: float
    error_threshold: float
    critical_threshold: float
    comparison: str = "greater"  # greater, less, equal


class AdvancedMetricsCollector:
    """Enhanced metrics collector with real-time monitoring and alerting."""

    def __init__(
        self,
        logger: Optional[AIPrishtinaLogger] = None,
        enable_real_time: bool = True,
        history_size: int = 1000
    ):
        """Initialize advanced metrics collector."""
        self.logger = logger or AIPrishtinaLogger(name="advanced_metrics")
        self.enable_real_time = enable_real_time
        self.history_size = history_size

        # Enhanced metrics storage
        self.metrics = defaultdict(lambda: {
            "count": 0,
            "total": 0.0,
            "average": 0.0,
            "min": float('inf'),
            "max": 0.0,
            "last_value": 0.0,
            "history": deque(maxlen=history_size),
            "timestamps": deque(maxlen=history_size)
        })

        # System metrics
        self.system_metrics = {
            "cpu_usage": deque(maxlen=history_size),
            "memory_usage": deque(maxlen=history_size),
            "disk_usage": deque(maxlen=history_size),
            "network_io": deque(maxlen=history_size),
            "timestamps": deque(maxlen=history_size)
        }

        # Alerting system
        self.thresholds: Dict[str, MetricThreshold] = {}
        self.alerts: List[Alert] = []
        self.alert_callbacks: List[Callable] = []

        # Performance tracking
        self.operation_timers = {}
        self.performance_baselines = {}

        # Real-time monitoring
        self.monitoring_task = None
        self.monitoring_interval = 10.0  # seconds

        # Custom metrics
        self.custom_metrics = defaultdict(float)

    async def start_real_time_monitoring(self, interval: float = 10.0):
        """Start real-time system monitoring."""
        if not self.enable_real_time or self.monitoring_task is not None:
            return

        self.monitoring_interval = interval
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        await self.logger.info("Started real-time metrics monitoring")

    async def stop_real_time_monitoring(self):
        """Stop real-time monitoring."""
        if self.monitoring_task is not None:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

        await self.logger.info("Stopped real-time metrics monitoring")

    async def _monitoring_loop(self):
        """Real-time monitoring loop."""
        while True:
            try:
                await self._collect_system_metrics()
                await self._check_thresholds()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)

    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        timestamp = datetime.now()

        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.system_metrics["cpu_usage"].append(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        self.system_metrics["memory_usage"].append(memory.percent)

        # Disk usage
        disk = psutil.disk_usage('/')
        self.system_metrics["disk_usage"].append(disk.percent)

        # Network I/O
        network = psutil.net_io_counters()
        network_total = network.bytes_sent + network.bytes_recv
        self.system_metrics["network_io"].append(network_total)

        # Timestamps
        self.system_metrics["timestamps"].append(timestamp)

        # Update metrics
        await self.record_metric("system.cpu_usage", cpu_percent)
        await self.record_metric("system.memory_usage", memory.percent)
        await self.record_metric("system.disk_usage", disk.percent)

    async def record_metric(self, name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a metric value with enhanced tracking."""
        if timestamp is None:
            timestamp = datetime.now()

        metric = self.metrics[name]
        metric["count"] += 1
        metric["total"] += value
        metric["average"] = metric["total"] / metric["count"]
        metric["min"] = min(metric["min"], value)
        metric["max"] = max(metric["max"], value)
        metric["last_value"] = value
        metric["history"].append(value)
        metric["timestamps"].append(timestamp)

        # Check for threshold violations
        await self._check_metric_threshold(name, value)

        await self.logger.debug(f"Recorded metric {name}: {value}")

    async def _check_metric_threshold(self, metric_name: str, value: float):
        """Check if metric violates thresholds."""
        if metric_name not in self.thresholds:
            return

        threshold = self.thresholds[metric_name]
        alert_level = None

        if threshold.comparison == "greater":
            if value >= threshold.critical_threshold:
                alert_level = AlertLevel.CRITICAL
            elif value >= threshold.error_threshold:
                alert_level = AlertLevel.ERROR
            elif value >= threshold.warning_threshold:
                alert_level = AlertLevel.WARNING
        elif threshold.comparison == "less":
            if value <= threshold.critical_threshold:
                alert_level = AlertLevel.CRITICAL
            elif value <= threshold.error_threshold:
                alert_level = AlertLevel.ERROR
            elif value <= threshold.warning_threshold:
                alert_level = AlertLevel.WARNING

        if alert_level:
            await self._create_alert(metric_name, value, threshold, alert_level)

    async def _create_alert(
        self,
        metric_name: str,
        value: float,
        threshold: MetricThreshold,
        level: AlertLevel
    ):
        """Create and process an alert."""
        alert_id = f"{metric_name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            level=level,
            message=f"Metric {metric_name} value {value:.2f} exceeded {level.value} threshold",
            timestamp=datetime.now(),
            metric_name=metric_name,
            metric_value=value,
            threshold=getattr(threshold, f"{level.value}_threshold")
        )

        self.alerts.append(alert)

        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                await self.logger.error(f"Alert callback error: {str(e)}")

        await self.logger.warning(f"Alert created: {alert.message}")

    async def set_threshold(
        self,
        metric_name: str,
        warning: float,
        error: float,
        critical: float,
        comparison: str = "greater"
    ):
        """Set thresholds for a metric."""
        self.thresholds[metric_name] = MetricThreshold(
            warning_threshold=warning,
            error_threshold=error,
            critical_threshold=critical,
            comparison=comparison
        )

        await self.logger.info(f"Set thresholds for {metric_name}: W={warning}, E={error}, C={critical}")

    def add_alert_callback(self, callback: Callable):
        """Add callback function for alerts."""
        self.alert_callbacks.append(callback)

    async def get_metric_statistics(self, metric_name: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a metric."""
        if metric_name not in self.metrics:
            return {}

        metric = self.metrics[metric_name]
        history = list(metric["history"])

        if not history:
            return metric

        # Calculate additional statistics
        percentiles = np.percentile(history, [25, 50, 75, 90, 95, 99])

        return {
            **metric,
            "percentile_25": percentiles[0],
            "percentile_50": percentiles[1],
            "percentile_75": percentiles[2],
            "percentile_90": percentiles[3],
            "percentile_95": percentiles[4],
            "percentile_99": percentiles[5],
            "standard_deviation": np.std(history),
            "variance": np.var(history),
            "trend": self._calculate_trend(history)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for metric values."""
        if len(values) < 2:
            return "stable"

        # Simple linear regression slope
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"

    async def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-100)."""
        scores = []

        # CPU health (lower is better)
        if self.system_metrics["cpu_usage"]:
            cpu_avg = np.mean(list(self.system_metrics["cpu_usage"])[-10:])
            cpu_score = max(0, 100 - cpu_avg)
            scores.append(cpu_score)

        # Memory health (lower is better)
        if self.system_metrics["memory_usage"]:
            memory_avg = np.mean(list(self.system_metrics["memory_usage"])[-10:])
            memory_score = max(0, 100 - memory_avg)
            scores.append(memory_score)

        # Disk health (lower is better)
        if self.system_metrics["disk_usage"]:
            disk_avg = np.mean(list(self.system_metrics["disk_usage"])[-10:])
            disk_score = max(0, 100 - disk_avg)
            scores.append(disk_score)

        # Alert penalty
        recent_alerts = [a for a in self.alerts if not a.resolved and
                        (datetime.now() - a.timestamp).seconds < 300]  # Last 5 minutes
        alert_penalty = len(recent_alerts) * 5

        if scores:
            base_score = np.mean(scores)
            final_score = max(0, base_score - alert_penalty)
            return final_score

        return 100.0  # Perfect score if no metrics available

    async def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": dict(self.metrics),
            "system_metrics": {
                k: list(v) if isinstance(v, deque) else v
                for k, v in self.system_metrics.items()
            },
            "alerts": [
                {
                    "id": alert.id,
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "metric_name": alert.metric_name,
                    "metric_value": alert.metric_value,
                    "threshold": alert.threshold,
                    "resolved": alert.resolved
                }
                for alert in self.alerts
            ],
            "health_score": await self.get_system_health_score()
        }

        if format == "json":
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def cleanup(self):
        """Cleanup metrics collector resources."""
        await self.stop_real_time_monitoring()
        self.metrics.clear()
        self.system_metrics.clear()
        self.alerts.clear()
        await self.logger.info("Metrics collector cleanup completed")
        
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get current performance metrics.
        
        Returns:
            Dict containing current metrics
        """
        return self.metrics 