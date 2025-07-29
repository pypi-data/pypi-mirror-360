"""FastMCP performance patterns integration for enhanced monitoring.

This module implements FastMCP-specific performance patterns and real-time alerting
capabilities to complement the existing Prometheus metrics system.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from loguru import logger

try:
    from .prometheus_metrics import prometheus_metrics
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class FastMCPMetric:
    """FastMCP-specific performance metric."""
    timestamp: datetime
    tool_name: str
    action: str
    latency_ms: float
    throughput_ops_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float
    cache_hit_rate: float
    concurrent_requests: int
    error_rate: float
    success: bool


@dataclass
class PerformanceAlert:
    """Real-time performance alert."""
    alert_id: str
    timestamp: datetime
    severity: str  # CRITICAL, WARNING, INFO
    metric_type: str
    threshold_value: float
    actual_value: float
    tool_name: str
    action: Optional[str]
    message: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class FastMCPPerformanceMonitor:
    """Enhanced performance monitor with FastMCP patterns and real-time alerting."""
    
    def __init__(self, max_metrics: int = 50000):
        """Initialize FastMCP performance monitor.
        
        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.alerts: deque = deque(maxlen=1000)
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # Real-time tracking
        self.active_requests: Dict[str, datetime] = {}
        self.throughput_tracker: Dict[str, List[datetime]] = defaultdict(list)
        self.latency_tracker: Dict[str, List[float]] = defaultdict(list)
        
        # Performance targets (FastMCP standards)
        self.performance_targets = {
            "latency_p95_ms": 100.0,
            "latency_p99_ms": 250.0,
            "throughput_min_ops_per_sec": 10.0,
            "error_rate_max_percent": 1.0,
            "memory_usage_max_mb": 512.0,
            "cpu_usage_max_percent": 80.0,
            "cache_hit_rate_min_percent": 80.0
        }
        
        # Initialize default alert rules
        self._setup_default_alert_rules()

        # Background tasks will be started when first metric is recorded
        self._background_tasks_started = False
    
    def _setup_default_alert_rules(self):
        """Setup default FastMCP alert rules."""
        self.alert_rules = {
            "high_latency": {
                "metric": "latency_p95_ms",
                "threshold": 100.0,
                "severity": "WARNING",
                "window_seconds": 60
            },
            "critical_latency": {
                "metric": "latency_p99_ms", 
                "threshold": 250.0,
                "severity": "CRITICAL",
                "window_seconds": 30
            },
            "low_throughput": {
                "metric": "throughput_ops_per_sec",
                "threshold": 10.0,
                "severity": "WARNING",
                "operator": "less_than",
                "window_seconds": 120
            },
            "high_error_rate": {
                "metric": "error_rate_percent",
                "threshold": 1.0,
                "severity": "CRITICAL",
                "window_seconds": 60
            },
            "memory_pressure": {
                "metric": "memory_usage_mb",
                "threshold": 512.0,
                "severity": "WARNING",
                "window_seconds": 300
            },
            "cpu_pressure": {
                "metric": "cpu_usage_percent",
                "threshold": 80.0,
                "severity": "WARNING",
                "window_seconds": 180
            },
            "low_cache_hit_rate": {
                "metric": "cache_hit_rate_percent",
                "threshold": 80.0,
                "severity": "WARNING",
                "operator": "less_than",
                "window_seconds": 300
            }
        }
    
    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        # Start alert evaluation task
        asyncio.create_task(self._alert_evaluation_loop())
        # Start metrics cleanup task
        asyncio.create_task(self._metrics_cleanup_loop())
        # Start baseline calculation task
        asyncio.create_task(self._baseline_calculation_loop())
    
    async def record_fastmcp_metric(
        self,
        tool_name: str,
        action: str,
        latency_ms: float,
        success: bool,
        memory_usage_mb: Optional[float] = None,
        cpu_usage_percent: Optional[float] = None,
        cache_hit_rate: Optional[float] = None
    ):
        """Record a FastMCP performance metric.

        Args:
            tool_name: Name of the tool
            action: Action performed
            latency_ms: Latency in milliseconds
            success: Whether the operation was successful
            memory_usage_mb: Memory usage in MB
            cpu_usage_percent: CPU usage percentage
            cache_hit_rate: Cache hit rate (0.0-1.0)
        """
        # Start background tasks if not already started
        if not self._background_tasks_started:
            self._start_background_tasks()
            self._background_tasks_started = True

        now = datetime.now(timezone.utc)
        
        # Calculate throughput
        tool_action_key = f"{tool_name}:{action}"
        self.throughput_tracker[tool_action_key].append(now)
        
        # Clean old throughput entries (keep last 60 seconds)
        cutoff_time = now - timedelta(seconds=60)
        self.throughput_tracker[tool_action_key] = [
            t for t in self.throughput_tracker[tool_action_key] if t > cutoff_time
        ]
        
        throughput_ops_per_sec = len(self.throughput_tracker[tool_action_key])
        
        # Track latency
        self.latency_tracker[tool_action_key].append(latency_ms)
        if len(self.latency_tracker[tool_action_key]) > 1000:
            self.latency_tracker[tool_action_key] = self.latency_tracker[tool_action_key][-1000:]
        
        # Calculate error rate
        recent_metrics = [m for m in self.metrics if m.tool_name == tool_name and m.action == action]
        if len(recent_metrics) > 0:
            error_count = sum(1 for m in recent_metrics[-100:] if not m.success)
            error_rate = (error_count / min(len(recent_metrics), 100)) * 100
        else:
            error_rate = 0.0 if success else 100.0
        
        # Get system metrics
        if memory_usage_mb is None:
            memory_usage_mb = self._get_memory_usage_mb()
        if cpu_usage_percent is None:
            cpu_usage_percent = self._get_cpu_usage_percent()
        if cache_hit_rate is None:
            cache_hit_rate = 0.0
        
        # Create metric
        metric = FastMCPMetric(
            timestamp=now,
            tool_name=tool_name,
            action=action,
            latency_ms=latency_ms,
            throughput_ops_per_sec=throughput_ops_per_sec,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            cache_hit_rate=cache_hit_rate * 100,  # Convert to percentage
            concurrent_requests=len(self.active_requests),
            error_rate=error_rate,
            success=success
        )
        
        self.metrics.append(metric)
        
        # Record to Prometheus if available
        if PROMETHEUS_AVAILABLE:
            prometheus_metrics.record_tool_execution(
                tool_name=tool_name,
                action=action,
                duration_seconds=latency_ms / 1000.0,
                success=success
            )
        
        # Trigger real-time alert evaluation
        await self._evaluate_alerts_for_metric(metric)
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback: Use basic memory estimation
            import sys
            return sys.getsizeof(self.metrics) / 1024 / 1024
        except Exception:
            return 0.0

    def _get_cpu_usage_percent(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            # Fallback: Return a reasonable default
            return 5.0  # Assume low CPU usage when psutil unavailable
        except Exception:
            return 0.0
    
    async def _evaluate_alerts_for_metric(self, metric: FastMCPMetric):
        """Evaluate alert rules for a specific metric."""
        for rule_name, rule in self.alert_rules.items():
            try:
                await self._check_alert_rule(rule_name, rule, metric)
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_name}: {e}")
    
    async def _check_alert_rule(self, rule_name: str, rule: Dict[str, Any], metric: FastMCPMetric):
        """Check if an alert rule is triggered."""
        metric_name = rule["metric"]
        threshold = rule["threshold"]
        severity = rule["severity"]
        operator = rule.get("operator", "greater_than")
        
        # Get metric value
        metric_value = getattr(metric, metric_name.replace("_percent", "").replace("_ms", "_ms").replace("_mb", "_mb"), None)
        if metric_value is None:
            return
        
        # Check threshold
        triggered = False
        if operator == "greater_than" and metric_value > threshold:
            triggered = True
        elif operator == "less_than" and metric_value < threshold:
            triggered = True
        
        if triggered:
            alert = PerformanceAlert(
                alert_id=f"{rule_name}_{metric.tool_name}_{int(time.time())}",
                timestamp=metric.timestamp,
                severity=severity,
                metric_type=metric_name,
                threshold_value=threshold,
                actual_value=metric_value,
                tool_name=metric.tool_name,
                action=metric.action,
                message=f"{severity}: {metric_name} {operator} {threshold} (actual: {metric_value:.2f})"
            )
            
            self.alerts.append(alert)
            logger.warning(f"Performance alert triggered: {alert.message}")
    
    async def _alert_evaluation_loop(self):
        """Background task for continuous alert evaluation."""
        while True:
            try:
                await asyncio.sleep(30)  # Evaluate every 30 seconds
                await self._evaluate_window_based_alerts()
            except Exception as e:
                logger.error(f"Error in alert evaluation loop: {e}")
    
    async def _evaluate_window_based_alerts(self):
        """Evaluate alerts based on time windows."""
        now = datetime.now(timezone.utc)
        
        for rule_name, rule in self.alert_rules.items():
            window_seconds = rule.get("window_seconds", 60)
            cutoff_time = now - timedelta(seconds=window_seconds)
            
            # Get metrics in window
            window_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
            
            if not window_metrics:
                continue
            
            # Calculate aggregated metrics
            await self._check_window_alert(rule_name, rule, window_metrics)
    
    async def _check_window_alert(self, rule_name: str, rule: Dict[str, Any], metrics: List[FastMCPMetric]):
        """Check alert rule against window of metrics."""
        metric_name = rule["metric"]
        threshold = rule["threshold"]
        
        if metric_name == "latency_p95_ms":
            latencies = [m.latency_ms for m in metrics]
            if latencies:
                p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
                if p95_latency > threshold:
                    await self._create_window_alert(rule_name, rule, "latency_p95_ms", p95_latency, threshold)
        
        elif metric_name == "latency_p99_ms":
            latencies = [m.latency_ms for m in metrics]
            if latencies:
                p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
                if p99_latency > threshold:
                    await self._create_window_alert(rule_name, rule, "latency_p99_ms", p99_latency, threshold)
    
    async def _create_window_alert(self, rule_name: str, rule: Dict[str, Any], metric_type: str, actual_value: float, threshold: float):
        """Create a window-based alert."""
        alert = PerformanceAlert(
            alert_id=f"{rule_name}_window_{int(time.time())}",
            timestamp=datetime.now(timezone.utc),
            severity=rule["severity"],
            metric_type=metric_type,
            threshold_value=threshold,
            actual_value=actual_value,
            tool_name="system",
            action=None,
            message=f"{rule['severity']}: {metric_type} exceeded threshold {threshold} (actual: {actual_value:.2f})"
        )
        
        self.alerts.append(alert)
        logger.warning(f"Window-based alert triggered: {alert.message}")
    
    async def _metrics_cleanup_loop(self):
        """Background task for metrics cleanup."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_old_metrics()
            except Exception as e:
                logger.error(f"Error in metrics cleanup loop: {e}")
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics and tracking data."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=24)  # Keep 24 hours of data
        
        # Clean throughput tracker
        for key in list(self.throughput_tracker.keys()):
            self.throughput_tracker[key] = [
                t for t in self.throughput_tracker[key] if t > cutoff_time
            ]
            if not self.throughput_tracker[key]:
                del self.throughput_tracker[key]
        
        # Clean latency tracker (keep more recent data)
        for key in list(self.latency_tracker.keys()):
            if len(self.latency_tracker[key]) > 1000:
                self.latency_tracker[key] = self.latency_tracker[key][-1000:]
    
    async def _baseline_calculation_loop(self):
        """Background task for calculating performance baselines."""
        while True:
            try:
                await asyncio.sleep(3600)  # Calculate baselines every hour
                await self._calculate_performance_baselines()
            except Exception as e:
                logger.error(f"Error in baseline calculation loop: {e}")
    
    async def _calculate_performance_baselines(self):
        """Calculate performance baselines for anomaly detection."""
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(days=7)  # Use last 7 days for baseline
        
        baseline_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        
        if not baseline_metrics:
            return
        
        # Group by tool and action
        grouped_metrics = defaultdict(list)
        for metric in baseline_metrics:
            key = f"{metric.tool_name}:{metric.action}"
            grouped_metrics[key].append(metric)
        
        # Calculate baselines
        for key, metrics in grouped_metrics.items():
            if len(metrics) < 10:  # Need minimum data points
                continue
            
            latencies = [m.latency_ms for m in metrics]
            throughputs = [m.throughput_ops_per_sec for m in metrics]
            error_rates = [m.error_rate for m in metrics]
            
            self.performance_baselines[key] = {
                "latency_p50": sorted(latencies)[len(latencies) // 2],
                "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)],
                "latency_p99": sorted(latencies)[int(len(latencies) * 0.99)],
                "throughput_avg": sum(throughputs) / len(throughputs),
                "error_rate_avg": sum(error_rates) / len(error_rates),
                "sample_count": len(metrics)
            }
    
    def get_fastmcp_dashboard(self) -> Dict[str, Any]:
        """Get FastMCP performance dashboard data."""
        now = datetime.now(timezone.utc)
        
        # Get recent metrics (last hour)
        recent_cutoff = now - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics if m.timestamp > recent_cutoff]
        
        if not recent_metrics:
            return {
                "timestamp": now.isoformat(),
                "status": "no_data",
                "message": "No recent performance data available"
            }
        
        # Calculate current performance
        latencies = [m.latency_ms for m in recent_metrics]
        throughputs = [m.throughput_ops_per_sec for m in recent_metrics]
        error_rates = [m.error_rate for m in recent_metrics]
        memory_usage = [m.memory_usage_mb for m in recent_metrics]
        cpu_usage = [m.cpu_usage_percent for m in recent_metrics]
        cache_hit_rates = [m.cache_hit_rate for m in recent_metrics]
        
        # Calculate percentiles
        latency_p50 = sorted(latencies)[len(latencies) // 2] if latencies else 0
        latency_p95 = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
        latency_p99 = sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0
        
        # Get active alerts
        active_alerts = [a for a in self.alerts if not a.resolved]
        critical_alerts = [a for a in active_alerts if a.severity == "CRITICAL"]
        warning_alerts = [a for a in active_alerts if a.severity == "WARNING"]
        
        return {
            "timestamp": now.isoformat(),
            "status": "healthy" if not critical_alerts else "critical",
            "performance_summary": {
                "latency_p50_ms": latency_p50,
                "latency_p95_ms": latency_p95,
                "latency_p99_ms": latency_p99,
                "throughput_avg_ops_per_sec": sum(throughputs) / len(throughputs) if throughputs else 0,
                "error_rate_avg_percent": sum(error_rates) / len(error_rates) if error_rates else 0,
                "memory_usage_avg_mb": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                "cpu_usage_avg_percent": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                "cache_hit_rate_avg_percent": sum(cache_hit_rates) / len(cache_hit_rates) if cache_hit_rates else 0
            },
            "target_compliance": {
                "latency_p95_target_met": latency_p95 <= self.performance_targets["latency_p95_ms"],
                "latency_p99_target_met": latency_p99 <= self.performance_targets["latency_p99_ms"],
                "error_rate_target_met": (sum(error_rates) / len(error_rates) if error_rates else 0) <= self.performance_targets["error_rate_max_percent"]
            },
            "alerts": {
                "total_active": len(active_alerts),
                "critical": len(critical_alerts),
                "warning": len(warning_alerts),
                "recent_alerts": [
                    {
                        "severity": a.severity,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "tool_name": a.tool_name
                    }
                    for a in sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)[:5]
                ]
            },
            "metrics_collected": len(recent_metrics),
            "monitoring_window_hours": 1
        }


# Global FastMCP performance monitor instance
fastmcp_monitor = FastMCPPerformanceMonitor()


def fastmcp_performance_decorator(tool_name: str, action: Optional[str] = None):
    """Decorator for FastMCP performance monitoring.
    
    Args:
        tool_name: Name of the tool
        action: Action name (defaults to function name)
    
    Returns:
        Decorated function with FastMCP performance monitoring
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            action_name = action or func.__name__
            success = False
            
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                raise
            finally:
                latency_ms = (time.time() - start_time) * 1000
                await fastmcp_monitor.record_fastmcp_metric(
                    tool_name=tool_name,
                    action=action_name,
                    latency_ms=latency_ms,
                    success=success
                )
        
        return wrapper
    return decorator


def get_fastmcp_dashboard() -> Dict[str, Any]:
    """Get FastMCP performance dashboard data.
    
    Returns:
        FastMCP dashboard data
    """
    return fastmcp_monitor.get_fastmcp_dashboard()
