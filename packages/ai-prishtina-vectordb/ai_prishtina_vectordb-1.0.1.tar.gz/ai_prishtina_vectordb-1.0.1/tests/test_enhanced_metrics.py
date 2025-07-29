"""
Tests for enhanced metrics and monitoring.
"""

import pytest
import asyncio
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from ai_prishtina_vectordb.metrics import (
    AdvancedMetricsCollector,
    AlertLevel,
    Alert,
    MetricThreshold
)
from ai_prishtina_vectordb.logger import AIPrishtinaLogger


class TestAlert:
    """Test cases for Alert."""
    
    def test_alert_creation(self):
        """Test alert creation."""
        alert = Alert(
            id="test_alert",
            level=AlertLevel.WARNING,
            message="Test alert message",
            timestamp=datetime.now(),
            metric_name="test_metric",
            metric_value=85.0,
            threshold=80.0
        )
        
        assert alert.id == "test_alert"
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "Test alert message"
        assert alert.metric_name == "test_metric"
        assert alert.metric_value == 85.0
        assert alert.threshold == 80.0
        assert alert.resolved is False
        assert alert.resolved_at is None


class TestMetricThreshold:
    """Test cases for MetricThreshold."""
    
    def test_threshold_creation(self):
        """Test threshold creation."""
        threshold = MetricThreshold(
            warning_threshold=70.0,
            error_threshold=85.0,
            critical_threshold=95.0,
            comparison="greater"
        )
        
        assert threshold.warning_threshold == 70.0
        assert threshold.error_threshold == 85.0
        assert threshold.critical_threshold == 95.0
        assert threshold.comparison == "greater"


class TestAdvancedMetricsCollector:
    """Test cases for AdvancedMetricsCollector."""
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_advanced_metrics")
    
    @pytest.fixture
    async def metrics_collector(self, logger):
        """Create advanced metrics collector."""
        return AdvancedMetricsCollector(
            logger=logger,
            enable_real_time=True,
            history_size=100
        )
    
    @pytest.mark.asyncio
    async def test_record_metric(self, metrics_collector):
        """Test recording a metric."""
        metric_name = "test_metric"
        value = 75.0
        
        await metrics_collector.record_metric(metric_name, value)
        
        metric = metrics_collector.metrics[metric_name]
        assert metric["count"] == 1
        assert metric["total"] == value
        assert metric["average"] == value
        assert metric["min"] == value
        assert metric["max"] == value
        assert metric["last_value"] == value
        assert len(metric["history"]) == 1
        assert len(metric["timestamps"]) == 1
    
    @pytest.mark.asyncio
    async def test_multiple_metric_records(self, metrics_collector):
        """Test recording multiple metric values."""
        metric_name = "test_metric"
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for value in values:
            await metrics_collector.record_metric(metric_name, value)
        
        metric = metrics_collector.metrics[metric_name]
        assert metric["count"] == 5
        assert metric["total"] == sum(values)
        assert metric["average"] == sum(values) / len(values)
        assert metric["min"] == min(values)
        assert metric["max"] == max(values)
        assert metric["last_value"] == values[-1]
        assert len(metric["history"]) == 5
    
    @pytest.mark.asyncio
    async def test_set_threshold(self, metrics_collector):
        """Test setting metric thresholds."""
        metric_name = "cpu_usage"
        
        await metrics_collector.set_threshold(
            metric_name=metric_name,
            warning=70.0,
            error=85.0,
            critical=95.0,
            comparison="greater"
        )
        
        assert metric_name in metrics_collector.thresholds
        threshold = metrics_collector.thresholds[metric_name]
        assert threshold.warning_threshold == 70.0
        assert threshold.error_threshold == 85.0
        assert threshold.critical_threshold == 95.0
        assert threshold.comparison == "greater"
    
    @pytest.mark.asyncio
    async def test_threshold_violation_warning(self, metrics_collector):
        """Test threshold violation creating warning alert."""
        metric_name = "cpu_usage"
        
        # Set threshold
        await metrics_collector.set_threshold(
            metric_name=metric_name,
            warning=70.0,
            error=85.0,
            critical=95.0
        )
        
        # Record value that exceeds warning threshold
        await metrics_collector.record_metric(metric_name, 75.0)
        
        # Should create warning alert
        assert len(metrics_collector.alerts) >= 1
        alert = metrics_collector.alerts[-1]
        assert alert.level == AlertLevel.WARNING
        assert alert.metric_name == metric_name
        assert alert.metric_value == 75.0
    
    @pytest.mark.asyncio
    async def test_threshold_violation_critical(self, metrics_collector):
        """Test threshold violation creating critical alert."""
        metric_name = "memory_usage"
        
        # Set threshold
        await metrics_collector.set_threshold(
            metric_name=metric_name,
            warning=70.0,
            error=85.0,
            critical=95.0
        )
        
        # Record value that exceeds critical threshold
        await metrics_collector.record_metric(metric_name, 98.0)
        
        # Should create critical alert
        assert len(metrics_collector.alerts) >= 1
        alert = metrics_collector.alerts[-1]
        assert alert.level == AlertLevel.CRITICAL
        assert alert.metric_name == metric_name
        assert alert.metric_value == 98.0
    
    @pytest.mark.asyncio
    async def test_alert_callback(self, metrics_collector):
        """Test alert callback functionality."""
        callback_called = False
        received_alert = None
        
        async def test_callback(alert):
            nonlocal callback_called, received_alert
            callback_called = True
            received_alert = alert
        
        # Add callback
        metrics_collector.add_alert_callback(test_callback)
        
        # Set threshold and trigger alert
        await metrics_collector.set_threshold("test_metric", 50.0, 70.0, 90.0)
        await metrics_collector.record_metric("test_metric", 60.0)
        
        # Callback should have been called
        assert callback_called is True
        assert received_alert is not None
        assert received_alert.level == AlertLevel.WARNING
    
    @pytest.mark.asyncio
    async def test_get_metric_statistics(self, metrics_collector):
        """Test getting comprehensive metric statistics."""
        metric_name = "response_time"
        values = [100, 150, 200, 120, 180, 90, 160, 140, 110, 170]
        
        for value in values:
            await metrics_collector.record_metric(metric_name, float(value))
        
        stats = await metrics_collector.get_metric_statistics(metric_name)
        
        assert "count" in stats
        assert "average" in stats
        assert "min" in stats
        assert "max" in stats
        assert "percentile_50" in stats
        assert "percentile_95" in stats
        assert "standard_deviation" in stats
        assert "variance" in stats
        assert "trend" in stats
        
        assert stats["count"] == 10
        assert stats["min"] == 90.0
        assert stats["max"] == 200.0
    
    @pytest.mark.asyncio
    async def test_start_stop_real_time_monitoring(self, metrics_collector):
        """Test starting and stopping real-time monitoring."""
        # Start monitoring
        await metrics_collector.start_real_time_monitoring(interval=0.1)
        assert metrics_collector.monitoring_task is not None
        
        # Let it run briefly
        await asyncio.sleep(0.2)
        
        # Should have collected some system metrics
        assert len(metrics_collector.system_metrics["timestamps"]) > 0
        
        # Stop monitoring
        await metrics_collector.stop_real_time_monitoring()
        assert metrics_collector.monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_system_health_score(self, metrics_collector):
        """Test system health score calculation."""
        # Mock system metrics
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.disk_usage') as mock_disk:
            
            # Mock good system health
            mock_memory.return_value.percent = 30  # Low memory usage
            mock_cpu.return_value = 25  # Low CPU usage
            mock_disk.return_value.percent = 40  # Low disk usage
            
            # Collect some system metrics
            await metrics_collector._collect_system_metrics()
            
            health_score = await metrics_collector.get_system_health_score()
            
            # Should have high health score
            assert health_score > 50.0
            assert health_score <= 100.0
    
    @pytest.mark.asyncio
    async def test_system_health_score_with_alerts(self, metrics_collector):
        """Test system health score with recent alerts."""
        # Create some recent alerts
        alert1 = Alert(
            id="alert1",
            level=AlertLevel.WARNING,
            message="Test alert 1",
            timestamp=datetime.now(),
            metric_name="test_metric",
            metric_value=80.0,
            threshold=70.0
        )
        
        alert2 = Alert(
            id="alert2",
            level=AlertLevel.ERROR,
            message="Test alert 2",
            timestamp=datetime.now(),
            metric_name="test_metric2",
            metric_value=90.0,
            threshold=85.0
        )
        
        metrics_collector.alerts.extend([alert1, alert2])
        
        # Mock good system metrics
        with patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 30
            mock_cpu.return_value = 25
            mock_disk.return_value.percent = 40
            
            await metrics_collector._collect_system_metrics()
            
            health_score = await metrics_collector.get_system_health_score()
            
            # Should have lower health score due to alerts
            assert health_score < 100.0
    
    @pytest.mark.asyncio
    async def test_export_metrics_json(self, metrics_collector):
        """Test exporting metrics in JSON format."""
        # Record some metrics
        await metrics_collector.record_metric("test_metric1", 50.0)
        await metrics_collector.record_metric("test_metric2", 75.0)
        
        # Create an alert
        await metrics_collector.set_threshold("test_metric2", 70.0, 80.0, 90.0)
        await metrics_collector.record_metric("test_metric2", 76.0)
        
        # Export metrics
        exported_data = await metrics_collector.export_metrics(format="json")
        
        # Should be valid JSON
        data = json.loads(exported_data)
        
        assert "timestamp" in data
        assert "metrics" in data
        assert "system_metrics" in data
        assert "alerts" in data
        assert "health_score" in data
        
        # Check metrics data
        assert "test_metric1" in data["metrics"]
        assert "test_metric2" in data["metrics"]
        
        # Check alerts data
        assert len(data["alerts"]) >= 1
        alert = data["alerts"][-1]
        assert "level" in alert
        assert "message" in alert
        assert "metric_name" in alert
    
    @pytest.mark.asyncio
    async def test_export_metrics_unsupported_format(self, metrics_collector):
        """Test exporting metrics with unsupported format."""
        with pytest.raises(ValueError):
            await metrics_collector.export_metrics(format="xml")
    
    def test_calculate_trend_increasing(self, metrics_collector):
        """Test trend calculation for increasing values."""
        values = [10, 15, 20, 25, 30, 35, 40]
        trend = metrics_collector._calculate_trend(values)
        assert trend == "increasing"
    
    def test_calculate_trend_decreasing(self, metrics_collector):
        """Test trend calculation for decreasing values."""
        values = [40, 35, 30, 25, 20, 15, 10]
        trend = metrics_collector._calculate_trend(values)
        assert trend == "decreasing"
    
    def test_calculate_trend_stable(self, metrics_collector):
        """Test trend calculation for stable values."""
        values = [20, 21, 19, 20, 22, 19, 21]
        trend = metrics_collector._calculate_trend(values)
        assert trend == "stable"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, metrics_collector):
        """Test metrics collector cleanup."""
        # Start monitoring
        await metrics_collector.start_real_time_monitoring(interval=0.1)
        
        # Add some data
        await metrics_collector.record_metric("test_metric", 50.0)
        
        # Cleanup
        await metrics_collector.cleanup()
        
        # Should stop monitoring and clear data
        assert metrics_collector.monitoring_task is None
        assert len(metrics_collector.metrics) == 0
        assert len(metrics_collector.system_metrics) == 0
        assert len(metrics_collector.alerts) == 0
    
    @pytest.mark.asyncio
    async def test_less_than_threshold_comparison(self, metrics_collector):
        """Test threshold with 'less than' comparison."""
        metric_name = "availability"
        
        # Set threshold with 'less' comparison
        await metrics_collector.set_threshold(
            metric_name=metric_name,
            warning=95.0,
            error=90.0,
            critical=85.0,
            comparison="less"
        )
        
        # Record value below critical threshold
        await metrics_collector.record_metric(metric_name, 80.0)
        
        # Should create critical alert
        assert len(metrics_collector.alerts) >= 1
        alert = metrics_collector.alerts[-1]
        assert alert.level == AlertLevel.CRITICAL
        assert alert.metric_name == metric_name
        assert alert.metric_value == 80.0
