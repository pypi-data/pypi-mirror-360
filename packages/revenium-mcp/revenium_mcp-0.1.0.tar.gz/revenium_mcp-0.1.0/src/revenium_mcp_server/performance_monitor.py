"""Performance monitoring for MCP tools.

This module provides performance monitoring capabilities for tracking tool execution times,
UCM lookup performance, and agent success rates as required by the UCM refactor validation.
"""

import time
import json
import asyncio
import functools
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import defaultdict, deque
from loguru import logger

# Import Prometheus metrics if available
try:
    from .prometheus_metrics import record_tool_execution, record_ucm_lookup
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.debug("Prometheus metrics not available")
    PROMETHEUS_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    tool_name: str
    action: str
    execution_time_ms: float
    ucm_lookup_time_ms: Optional[float]
    introspection_time_ms: Optional[float]
    execution_path: str  # "introspection", "direct", "failed", "error"
    success: bool
    timestamp: str
    error_message: Optional[str] = None


class PerformanceMonitor:
    """Performance monitoring system for MCP tools."""

    def __init__(self, max_metrics: int = 10000):
        """Initialize performance monitor.

        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.success_counts: Dict[str, int] = defaultdict(int)
        self.failure_counts: Dict[str, int] = defaultdict(int)
        self.execution_times: Dict[str, List[float]] = defaultdict(list)
        self.ucm_lookup_times: List[float] = []
        self.introspection_times: List[float] = []

    def record_metric(
        self,
        tool_name: str,
        action: str,
        execution_time_ms: float,
        execution_path: str,
        success: bool,
        ucm_lookup_time_ms: Optional[float] = None,
        introspection_time_ms: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Record a performance metric with Prometheus integration.

        Args:
            tool_name: Name of the tool
            action: Action performed
            execution_time_ms: Total execution time in milliseconds
            execution_path: Execution path taken
            success: Whether the execution was successful
            ucm_lookup_time_ms: UCM lookup time in milliseconds
            introspection_time_ms: Introspection time in milliseconds
            error_message: Error message if failed
        """
        metric = PerformanceMetric(
            tool_name=tool_name,
            action=action,
            execution_time_ms=execution_time_ms,
            ucm_lookup_time_ms=ucm_lookup_time_ms,
            introspection_time_ms=introspection_time_ms,
            execution_path=execution_path,
            success=success,
            timestamp=datetime.now(timezone.utc).isoformat(),
            error_message=error_message
        )

        self.metrics.append(metric)

        # Update aggregated statistics
        tool_action = f"{tool_name}.{action}"
        if success:
            self.success_counts[tool_action] += 1
        else:
            self.failure_counts[tool_action] += 1

        # Track execution times for percentile calculations
        self.execution_times[tool_action].append(execution_time_ms)
        if len(self.execution_times[tool_action]) > 1000:  # Keep last 1000 measurements
            self.execution_times[tool_action] = self.execution_times[tool_action][-1000:]

        # Track UCM and introspection times
        if ucm_lookup_time_ms is not None:
            self.ucm_lookup_times.append(ucm_lookup_time_ms)
            if len(self.ucm_lookup_times) > 1000:
                self.ucm_lookup_times = self.ucm_lookup_times[-1000:]

        if introspection_time_ms is not None:
            self.introspection_times.append(introspection_time_ms)
            if len(self.introspection_times) > 1000:
                self.introspection_times = self.introspection_times[-1000:]

        # Record to Prometheus if available
        if PROMETHEUS_AVAILABLE:
            try:
                # Determine error type for Prometheus
                error_type = None
                if not success and error_message:
                    if "validation" in error_message.lower():
                        error_type = "validation_error"
                    elif "api" in error_message.lower():
                        error_type = "api_error"
                    elif "timeout" in error_message.lower():
                        error_type = "timeout_error"
                    else:
                        error_type = "unknown_error"

                record_tool_execution(
                    tool_name=tool_name,
                    action=action,
                    duration_seconds=execution_time_ms / 1000.0,  # Convert to seconds
                    success=success,
                    error_type=error_type
                )

                # Record UCM lookup if available
                if ucm_lookup_time_ms is not None:
                    record_ucm_lookup(
                        capability_type="general",
                        duration_seconds=ucm_lookup_time_ms / 1000.0,
                        cache_hit=False  # We don't have cache info here
                    )

            except Exception as e:
                logger.debug(f"Failed to record Prometheus metrics: {e}")

    def get_success_rate(self, tool_name: Optional[str] = None) -> float:
        """Get success rate for a tool or overall.

        Args:
            tool_name: Tool name to filter by, or None for overall

        Returns:
            Success rate as a percentage (0-100)
        """
        if tool_name:
            pattern = f"{tool_name}."
            successes = sum(count for key, count in self.success_counts.items() if key.startswith(pattern))
            failures = sum(count for key, count in self.failure_counts.items() if key.startswith(pattern))
        else:
            successes = sum(self.success_counts.values())
            failures = sum(self.failure_counts.values())

        total = successes + failures
        if total == 0:
            return 100.0  # No data means 100% success rate

        return (successes / total) * 100.0

    def get_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile from a list of values.

        Args:
            values: List of values
            percentile: Percentile to calculate (0-100)

        Returns:
            Percentile value
        """
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        if index >= len(sorted_values):
            index = len(sorted_values) - 1
        return sorted_values[index]

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data.

        Returns:
            Performance dashboard data
        """
        # Calculate overall metrics
        overall_success_rate = self.get_success_rate()

        # Calculate execution time percentiles
        all_execution_times = []
        for times in self.execution_times.values():
            all_execution_times.extend(times)

        execution_95th = self.get_percentile(all_execution_times, 95.0)
        execution_99th = self.get_percentile(all_execution_times, 99.0)

        # Calculate UCM lookup percentiles
        ucm_50th = self.get_percentile(self.ucm_lookup_times, 50.0)
        ucm_95th = self.get_percentile(self.ucm_lookup_times, 95.0)
        ucm_99th = self.get_percentile(self.ucm_lookup_times, 99.0)

        # Calculate introspection percentiles
        introspection_50th = self.get_percentile(self.introspection_times, 50.0)
        introspection_95th = self.get_percentile(self.introspection_times, 95.0)
        introspection_99th = self.get_percentile(self.introspection_times, 99.0)

        # Tool-specific metrics
        tool_metrics = {}
        for tool_action in set(list(self.success_counts.keys()) + list(self.failure_counts.keys())):
            tool_name = tool_action.split('.')[0]
            if tool_name not in tool_metrics:
                tool_metrics[tool_name] = {
                    "success_rate": self.get_success_rate(tool_name),
                    "total_calls": 0,
                    "avg_execution_time": 0.0,
                    "95th_percentile": 0.0
                }

            successes = self.success_counts.get(tool_action, 0)
            failures = self.failure_counts.get(tool_action, 0)
            tool_metrics[tool_name]["total_calls"] += successes + failures

            if tool_action in self.execution_times and self.execution_times[tool_action]:
                times = self.execution_times[tool_action]
                tool_metrics[tool_name]["avg_execution_time"] = sum(times) / len(times)
                tool_metrics[tool_name]["95th_percentile"] = self.get_percentile(times, 95.0)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_metrics": {
                "success_rate_percent": overall_success_rate,
                "total_metrics_collected": len(self.metrics),
                "execution_time_95th_percentile_ms": execution_95th,
                "execution_time_99th_percentile_ms": execution_99th,
                "target_success_rate_met": overall_success_rate >= 99.5,
                "target_execution_time_met": execution_95th <= 100.0
            },
            "ucm_performance": {
                "lookup_time_50th_percentile_ms": ucm_50th,
                "lookup_time_95th_percentile_ms": ucm_95th,
                "lookup_time_99th_percentile_ms": ucm_99th,
                "target_lookup_time_met": ucm_99th <= 50.0,
                "total_lookups": len(self.ucm_lookup_times)
            },
            "introspection_performance": {
                "time_50th_percentile_ms": introspection_50th,
                "time_95th_percentile_ms": introspection_95th,
                "time_99th_percentile_ms": introspection_99th,
                "target_introspection_time_met": introspection_95th <= 10.0,
                "total_operations": len(self.introspection_times)
            },
            "tool_specific_metrics": tool_metrics,
            "success_criteria_summary": {
                "agent_success_rate_target": "≥99.5%",
                "agent_success_rate_actual": f"{overall_success_rate:.2f}%",
                "tool_execution_time_target": "≤100ms (95th percentile)",
                "tool_execution_time_actual": f"{execution_95th:.2f}ms",
                "ucm_lookup_time_target": "≤50ms (99th percentile)",
                "ucm_lookup_time_actual": f"{ucm_99th:.2f}ms",
                "introspection_overhead_target": "≤10ms (95th percentile)",
                "introspection_overhead_actual": f"{introspection_95th:.2f}ms",
                "all_targets_met": (
                    overall_success_rate >= 99.5 and
                    execution_95th <= 100.0 and
                    ucm_99th <= 50.0 and
                    introspection_95th <= 10.0
                )
            }
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def performance_monitor_decorator(tool_name: str, action: Optional[str] = None):
    """Decorator for automatic performance monitoring of tool methods.

    Args:
        tool_name: Name of the tool
        action: Action name (defaults to function name)

    Returns:
        Decorated function with performance monitoring
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            action_name = action or func.__name__
            success = False
            error_message = None

            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                record_performance_metric(
                    tool_name=tool_name,
                    action=action_name,
                    execution_time_ms=execution_time_ms,
                    execution_path="direct",
                    success=success,
                    error_message=error_message
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            action_name = action or func.__name__
            success = False
            error_message = None

            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000
                record_performance_metric(
                    tool_name=tool_name,
                    action=action_name,
                    execution_time_ms=execution_time_ms,
                    execution_path="direct",
                    success=success,
                    error_message=error_message
                )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def record_performance_metric(
    tool_name: str,
    action: str,
    execution_time_ms: float,
    execution_path: str,
    success: bool,
    ucm_lookup_time_ms: Optional[float] = None,
    introspection_time_ms: Optional[float] = None,
    error_message: Optional[str] = None
) -> None:
    """Record a performance metric using the global monitor.

    Args:
        tool_name: Name of the tool
        action: Action performed
        execution_time_ms: Total execution time in milliseconds
        execution_path: Execution path taken
        success: Whether the execution was successful
        ucm_lookup_time_ms: UCM lookup time in milliseconds
        introspection_time_ms: Introspection time in milliseconds
        error_message: Error message if failed
    """
    performance_monitor.record_metric(
        tool_name=tool_name,
        action=action,
        execution_time_ms=execution_time_ms,
        execution_path=execution_path,
        success=success,
        ucm_lookup_time_ms=ucm_lookup_time_ms,
        introspection_time_ms=introspection_time_ms,
        error_message=error_message
    )


def get_performance_dashboard() -> Dict[str, Any]:
    """Get performance dashboard data from the global monitor.

    Returns:
        Performance dashboard data
    """
    return performance_monitor.get_performance_dashboard()