"""
Advanced analytics and reporting for AI Prishtina VectorDB.

This module provides comprehensive analytics capabilities including
usage analytics, performance analytics, business intelligence, and reporting.
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
from collections import defaultdict, deque

from .logger import AIPrishtinaLogger
from .metrics import AdvancedMetricsCollector
from .exceptions import AIPrishtinaError


class ReportType(Enum):
    """Report type enumeration."""
    USAGE = "usage"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class AnalyticsTimeframe(Enum):
    """Analytics timeframe enumeration."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AggregationType(Enum):
    """Aggregation type enumeration."""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    DISTINCT_COUNT = "distinct_count"


@dataclass
class AnalyticsQuery:
    """Analytics query specification."""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metrics: List[str] = field(default_factory=list)
    dimensions: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.DAILY
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    aggregation: AggregationType = AggregationType.SUM
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_desc: bool = True


@dataclass
class AnalyticsResult:
    """Analytics query result."""
    query_id: str
    data: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    total_rows: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Report:
    """Report specification and data."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType = ReportType.USAGE
    title: str = ""
    description: str = ""
    queries: List[AnalyticsQuery] = field(default_factory=list)
    results: List[AnalyticsResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_at: Optional[datetime] = None
    format: str = "json"  # json, csv, pdf, html
    schedule: Optional[str] = None  # cron expression
    recipients: List[str] = field(default_factory=list)


class UsageAnalytics:
    """Tracks and analyzes usage patterns."""
    
    def __init__(self, logger: Optional[AIPrishtinaLogger] = None):
        """Initialize usage analytics."""
        self.logger = logger or AIPrishtinaLogger(name="usage_analytics")
        
        # Usage tracking
        self.user_sessions: Dict[str, List[datetime]] = defaultdict(list)
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.collection_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.feature_usage: Dict[str, int] = defaultdict(int)
        self.api_endpoints: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Time-series data
        self.hourly_usage = deque(maxlen=24 * 7)  # 7 days of hourly data
        self.daily_usage = deque(maxlen=365)  # 1 year of daily data
    
    async def track_user_session(self, user_id: str, session_start: datetime):
        """Track user session."""
        self.user_sessions[user_id].append(session_start)
        await self.logger.debug(f"Tracked session for user: {user_id}")
    
    async def track_query(self, query_type: str, collection: str, user_id: str):
        """Track query execution."""
        self.query_patterns[query_type] += 1
        self.collection_usage[collection]["queries"] += 1
        self.collection_usage[collection]["users"] = len(set([user_id] + list(self.user_sessions.keys())))
        
        await self.logger.debug(f"Tracked query: {query_type} on {collection}")
    
    async def track_feature_usage(self, feature: str, user_id: str):
        """Track feature usage."""
        self.feature_usage[feature] += 1
        await self.logger.debug(f"Tracked feature usage: {feature} by {user_id}")
    
    async def track_api_call(self, endpoint: str, method: str, status_code: int):
        """Track API call."""
        self.api_endpoints[endpoint][method] += 1
        self.api_endpoints[endpoint][f"status_{status_code}"] += 1
        
        await self.logger.debug(f"Tracked API call: {method} {endpoint} -> {status_code}")
    
    async def get_usage_summary(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Get usage summary for timeframe."""
        now = datetime.now(timezone.utc)
        
        if timeframe == AnalyticsTimeframe.DAILY:
            start_time = now - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_time = now - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(hours=1)
        
        # Filter sessions by timeframe
        active_users = set()
        for user_id, sessions in self.user_sessions.items():
            recent_sessions = [s for s in sessions if s >= start_time]
            if recent_sessions:
                active_users.add(user_id)
        
        return {
            "timeframe": timeframe.value,
            "active_users": len(active_users),
            "total_queries": sum(self.query_patterns.values()),
            "popular_query_types": dict(sorted(self.query_patterns.items(), key=lambda x: x[1], reverse=True)[:5]),
            "collection_usage": dict(self.collection_usage),
            "feature_usage": dict(sorted(self.feature_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            "api_usage": dict(self.api_endpoints)
        }


class PerformanceAnalytics:
    """Analyzes system performance metrics."""
    
    def __init__(
        self,
        metrics: AdvancedMetricsCollector,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize performance analytics."""
        self.metrics = metrics
        self.logger = logger or AIPrishtinaLogger(name="performance_analytics")
        
        # Performance tracking
        self.response_times: deque = deque(maxlen=10000)
        self.throughput_data: deque = deque(maxlen=1000)
        self.error_rates: deque = deque(maxlen=1000)
        self.resource_usage: deque = deque(maxlen=1000)
    
    async def analyze_response_times(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Analyze response time patterns."""
        response_time_stats = await self.metrics.get_metric_statistics("response_time")
        
        if not response_time_stats:
            return {"error": "No response time data available"}
        
        return {
            "average_ms": response_time_stats.get("average", 0),
            "median_ms": response_time_stats.get("percentile_50", 0),
            "p95_ms": response_time_stats.get("percentile_95", 0),
            "p99_ms": response_time_stats.get("percentile_99", 0),
            "min_ms": response_time_stats.get("min", 0),
            "max_ms": response_time_stats.get("max", 0),
            "trend": response_time_stats.get("trend", "stable"),
            "sample_count": response_time_stats.get("count", 0)
        }
    
    async def analyze_throughput(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Analyze throughput patterns."""
        throughput_stats = await self.metrics.get_metric_statistics("throughput")
        
        if not throughput_stats:
            return {"error": "No throughput data available"}
        
        return {
            "average_rps": throughput_stats.get("average", 0),
            "peak_rps": throughput_stats.get("max", 0),
            "min_rps": throughput_stats.get("min", 0),
            "trend": throughput_stats.get("trend", "stable"),
            "total_requests": throughput_stats.get("count", 0) * throughput_stats.get("average", 0)
        }
    
    async def analyze_error_patterns(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Analyze error patterns."""
        error_stats = await self.metrics.get_metric_statistics("error_rate")
        
        return {
            "error_rate_percent": error_stats.get("average", 0) if error_stats else 0,
            "peak_error_rate": error_stats.get("max", 0) if error_stats else 0,
            "trend": error_stats.get("trend", "stable") if error_stats else "stable",
            "total_errors": error_stats.get("count", 0) if error_stats else 0
        }
    
    async def analyze_resource_utilization(self) -> Dict[str, Any]:
        """Analyze resource utilization."""
        cpu_stats = await self.metrics.get_metric_statistics("system.cpu_usage")
        memory_stats = await self.metrics.get_metric_statistics("system.memory_usage")
        disk_stats = await self.metrics.get_metric_statistics("system.disk_usage")
        
        return {
            "cpu": {
                "average_percent": cpu_stats.get("average", 0) if cpu_stats else 0,
                "peak_percent": cpu_stats.get("max", 0) if cpu_stats else 0,
                "trend": cpu_stats.get("trend", "stable") if cpu_stats else "stable"
            },
            "memory": {
                "average_percent": memory_stats.get("average", 0) if memory_stats else 0,
                "peak_percent": memory_stats.get("max", 0) if memory_stats else 0,
                "trend": memory_stats.get("trend", "stable") if memory_stats else "stable"
            },
            "disk": {
                "average_percent": disk_stats.get("average", 0) if disk_stats else 0,
                "peak_percent": disk_stats.get("max", 0) if disk_stats else 0,
                "trend": disk_stats.get("trend", "stable") if disk_stats else "stable"
            }
        }
    
    async def get_performance_summary(self, timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        response_times = await self.analyze_response_times(timeframe)
        throughput = await self.analyze_throughput(timeframe)
        errors = await self.analyze_error_patterns(timeframe)
        resources = await self.analyze_resource_utilization()
        
        # Calculate performance score
        performance_score = 100
        
        # Deduct points for high response times
        if response_times.get("p95_ms", 0) > 1000:
            performance_score -= 20
        elif response_times.get("p95_ms", 0) > 500:
            performance_score -= 10
        
        # Deduct points for high error rates
        error_rate = errors.get("error_rate_percent", 0)
        if error_rate > 5:
            performance_score -= 30
        elif error_rate > 1:
            performance_score -= 15
        
        # Deduct points for high resource usage
        cpu_usage = resources.get("cpu", {}).get("average_percent", 0)
        memory_usage = resources.get("memory", {}).get("average_percent", 0)
        
        if cpu_usage > 80 or memory_usage > 80:
            performance_score -= 20
        elif cpu_usage > 60 or memory_usage > 60:
            performance_score -= 10
        
        return {
            "timeframe": timeframe.value,
            "performance_score": max(0, performance_score),
            "response_times": response_times,
            "throughput": throughput,
            "errors": errors,
            "resources": resources,
            "recommendations": await self._generate_performance_recommendations(
                response_times, throughput, errors, resources
            )
        }
    
    async def _generate_performance_recommendations(
        self,
        response_times: Dict[str, Any],
        throughput: Dict[str, Any],
        errors: Dict[str, Any],
        resources: Dict[str, Any]
    ) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []
        
        # Response time recommendations
        if response_times.get("p95_ms", 0) > 1000:
            recommendations.append("Consider optimizing query performance or adding caching")
        
        # Throughput recommendations
        if throughput.get("average_rps", 0) < 10:
            recommendations.append("Low throughput detected - consider load testing and optimization")
        
        # Error rate recommendations
        if errors.get("error_rate_percent", 0) > 1:
            recommendations.append("High error rate detected - review error logs and fix issues")
        
        # Resource recommendations
        cpu_usage = resources.get("cpu", {}).get("average_percent", 0)
        memory_usage = resources.get("memory", {}).get("average_percent", 0)
        
        if cpu_usage > 80:
            recommendations.append("High CPU usage - consider scaling up or optimizing algorithms")
        
        if memory_usage > 80:
            recommendations.append("High memory usage - consider memory optimization or scaling")
        
        if not recommendations:
            recommendations.append("System performance is optimal")
        
        return recommendations


class ReportGenerator:
    """Generates various types of reports."""
    
    def __init__(
        self,
        usage_analytics: UsageAnalytics,
        performance_analytics: PerformanceAnalytics,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize report generator."""
        self.usage_analytics = usage_analytics
        self.performance_analytics = performance_analytics
        self.logger = logger or AIPrishtinaLogger(name="report_generator")
        
        # Report storage
        self.reports: Dict[str, Report] = {}
        self.scheduled_reports: List[Report] = []
    
    async def generate_report(self, report: Report) -> Report:
        """Generate a report."""
        try:
            await self.logger.info(f"Generating report: {report.title}")
            
            start_time = time.time()
            
            # Execute queries
            for query in report.queries:
                result = await self._execute_analytics_query(query)
                report.results.append(result)
            
            # Set generation metadata
            report.generated_at = datetime.now(timezone.utc)
            
            # Store report
            self.reports[report.report_id] = report
            
            execution_time = (time.time() - start_time) * 1000
            await self.logger.info(f"Report generated in {execution_time:.2f}ms: {report.title}")
            
            return report
            
        except Exception as e:
            await self.logger.error(f"Report generation failed: {str(e)}")
            raise AnalyticsError(f"Report generation failed: {str(e)}")
    
    async def _execute_analytics_query(self, query: AnalyticsQuery) -> AnalyticsResult:
        """Execute an analytics query."""
        start_time = time.time()
        
        try:
            data = []
            
            # Handle different query types
            if "usage" in query.metrics:
                usage_data = await self.usage_analytics.get_usage_summary(query.timeframe)
                data.append(usage_data)
            
            if "performance" in query.metrics:
                perf_data = await self.performance_analytics.get_performance_summary(query.timeframe)
                data.append(perf_data)
            
            # Apply filters
            if query.filters:
                data = self._apply_filters(data, query.filters)
            
            # Apply sorting and limiting
            if query.sort_by and data:
                data = sorted(data, key=lambda x: x.get(query.sort_by, 0), reverse=query.sort_desc)
            
            if query.limit:
                data = data[:query.limit]
            
            execution_time = (time.time() - start_time) * 1000
            
            return AnalyticsResult(
                query_id=query.query_id,
                data=data,
                execution_time_ms=execution_time,
                total_rows=len(data)
            )
            
        except Exception as e:
            await self.logger.error(f"Analytics query failed: {str(e)}")
            raise AnalyticsError(f"Analytics query failed: {str(e)}")
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        filtered_data = []
        
        for item in data:
            include_item = True
            
            for filter_key, filter_value in filters.items():
                if filter_key in item:
                    if isinstance(filter_value, dict):
                        # Range filter
                        if "min" in filter_value and item[filter_key] < filter_value["min"]:
                            include_item = False
                            break
                        if "max" in filter_value and item[filter_key] > filter_value["max"]:
                            include_item = False
                            break
                    else:
                        # Exact match filter
                        if item[filter_key] != filter_value:
                            include_item = False
                            break
            
            if include_item:
                filtered_data.append(item)
        
        return filtered_data
    
    async def create_usage_report(self, timeframe: AnalyticsTimeframe) -> Report:
        """Create a usage report."""
        query = AnalyticsQuery(
            metrics=["usage"],
            timeframe=timeframe
        )
        
        report = Report(
            report_type=ReportType.USAGE,
            title=f"Usage Report - {timeframe.value.title()}",
            description=f"Comprehensive usage analytics for {timeframe.value} period",
            queries=[query]
        )
        
        return await self.generate_report(report)
    
    async def create_performance_report(self, timeframe: AnalyticsTimeframe) -> Report:
        """Create a performance report."""
        query = AnalyticsQuery(
            metrics=["performance"],
            timeframe=timeframe
        )
        
        report = Report(
            report_type=ReportType.PERFORMANCE,
            title=f"Performance Report - {timeframe.value.title()}",
            description=f"System performance analysis for {timeframe.value} period",
            queries=[query]
        )
        
        return await self.generate_report(report)
    
    async def create_executive_summary(self) -> Report:
        """Create an executive summary report."""
        usage_query = AnalyticsQuery(
            metrics=["usage"],
            timeframe=AnalyticsTimeframe.MONTHLY
        )
        
        performance_query = AnalyticsQuery(
            metrics=["performance"],
            timeframe=AnalyticsTimeframe.MONTHLY
        )
        
        report = Report(
            report_type=ReportType.BUSINESS,
            title="Executive Summary - Monthly",
            description="High-level business and technical metrics summary",
            queries=[usage_query, performance_query]
        )
        
        return await self.generate_report(report)


class AnalyticsManager:
    """Main analytics manager coordinating all analytics features."""
    
    def __init__(
        self,
        metrics: AdvancedMetricsCollector,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize analytics manager."""
        self.metrics = metrics
        self.logger = logger or AIPrishtinaLogger(name="analytics_manager")
        
        # Components
        self.usage_analytics = UsageAnalytics(logger)
        self.performance_analytics = PerformanceAnalytics(metrics, logger)
        self.report_generator = ReportGenerator(
            self.usage_analytics,
            self.performance_analytics,
            logger
        )
    
    async def track_event(self, event_type: str, data: Dict[str, Any]):
        """Track an analytics event."""
        try:
            if event_type == "user_session":
                await self.usage_analytics.track_user_session(
                    data["user_id"],
                    data.get("session_start", datetime.now(timezone.utc))
                )
            elif event_type == "query":
                await self.usage_analytics.track_query(
                    data["query_type"],
                    data["collection"],
                    data["user_id"]
                )
            elif event_type == "feature_usage":
                await self.usage_analytics.track_feature_usage(
                    data["feature"],
                    data["user_id"]
                )
            elif event_type == "api_call":
                await self.usage_analytics.track_api_call(
                    data["endpoint"],
                    data["method"],
                    data["status_code"]
                )
            
            await self.logger.debug(f"Tracked analytics event: {event_type}")
            
        except Exception as e:
            await self.logger.error(f"Failed to track event {event_type}: {str(e)}")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for analytics dashboard."""
        try:
            # Get real-time metrics
            usage_summary = await self.usage_analytics.get_usage_summary(AnalyticsTimeframe.DAILY)
            performance_summary = await self.performance_analytics.get_performance_summary(AnalyticsTimeframe.DAILY)
            
            # Get system health
            health_score = await self.metrics.get_system_health_score()
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "usage": usage_summary,
                "performance": performance_summary,
                "health_score": health_score,
                "alerts": len([a for a in self.metrics.alerts if not a.resolved])
            }
            
        except Exception as e:
            await self.logger.error(f"Failed to get dashboard data: {str(e)}")
            return {"error": str(e)}


class AnalyticsError(AIPrishtinaError):
    """Exception raised for analytics errors."""
    pass
