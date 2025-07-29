"""Prometheus metrics collection for MCP server performance monitoring.

This module provides Prometheus-compatible metrics collection for tracking
tool execution times, success rates, and system performance metrics.
"""

import time
from typing import Dict, Optional, Any
from collections import defaultdict
from datetime import datetime, timezone

from loguru import logger

# Import FastMCP for MCP tool integration
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    logger.warning("FastMCP not available, MCP tool integration disabled")
    
    # Create dummy decorator for when FastMCP is not available
    class FastMCP:
        def tool(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

# Initialize FastMCP instance for tool decorators
mcp = FastMCP("prometheus_metrics") if FASTMCP_AVAILABLE else FastMCP()

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, CollectorRegistry,
        generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("prometheus_client not available, metrics collection disabled")
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for when Prometheus is not available
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def inc(self, *args): pass

    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def observe(self, *args): pass

    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def labels(self, **kwargs): return self
        def set(self, *args): pass

    class CollectorRegistry:
        def __init__(self): pass

    def generate_latest(registry=None):
        return b"# Prometheus not available\n"

    CONTENT_TYPE_LATEST = "text/plain"


class PrometheusMetrics:
    """Prometheus metrics collector for MCP server."""

    def __init__(self, registry: Optional[Any] = None):
        """Initialize Prometheus metrics.
        
        Args:
            registry: Custom registry to use, defaults to default registry
        """
        self.registry = registry
        self.enabled = PROMETHEUS_AVAILABLE
        
        if not self.enabled:
            logger.warning("Prometheus metrics disabled - prometheus_client not installed")
            return
            
        # Tool execution metrics
        self.tool_requests_total = Counter(
            'mcp_tool_requests_total',
            'Total number of tool requests',
            ['tool_name', 'action', 'status'],
            registry=registry
        )
        
        self.tool_duration_seconds = Histogram(
            'mcp_tool_duration_seconds',
            'Tool execution duration in seconds',
            ['tool_name', 'action'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=registry
        )
        
        self.tool_success_rate = Gauge(
            'mcp_tool_success_rate',
            'Tool success rate (0-1)',
            ['tool_name', 'action'],
            registry=registry
        )
        
        # UCM performance metrics
        self.ucm_lookup_duration_seconds = Histogram(
            'mcp_ucm_lookup_duration_seconds',
            'UCM capability lookup duration in seconds',
            ['capability_type'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            registry=registry
        )
        
        self.ucm_cache_hits_total = Counter(
            'mcp_ucm_cache_hits_total',
            'Total UCM cache hits',
            ['cache_level'],  # L1, L2, L3
            registry=registry
        )
        
        self.ucm_cache_misses_total = Counter(
            'mcp_ucm_cache_misses_total',
            'Total UCM cache misses',
            ['capability_type'],
            registry=registry
        )
        
        # API performance metrics
        self.api_requests_total = Counter(
            'mcp_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status_code'],
            registry=registry
        )
        
        self.api_duration_seconds = Histogram(
            'mcp_api_duration_seconds',
            'API request duration in seconds',
            ['endpoint', 'method'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=registry
        )
        
        # System metrics
        self.active_connections = Gauge(
            'mcp_active_connections',
            'Number of active HTTP connections',
            registry=registry
        )
        
        self.memory_usage_bytes = Gauge(
            'mcp_memory_usage_bytes',
            'Memory usage in bytes',
            registry=registry
        )
        
        self.cpu_usage_percent = Gauge(
            'mcp_cpu_usage_percent',
            'CPU usage percentage',
            registry=registry
        )
        
        # Error tracking
        self.errors_total = Counter(
            'mcp_errors_total',
            'Total errors by type',
            ['error_type', 'tool_name', 'action'],
            registry=registry
        )
        
        # Performance targets tracking
        self.performance_target_violations = Counter(
            'mcp_performance_target_violations_total',
            'Performance target violations',
            ['target_type', 'tool_name'],  # execution_time, success_rate, ucm_lookup
            registry=registry
        )

        # Cache performance metrics
        self.cache_operations_total = Counter(
            'mcp_cache_operations_total',
            'Total cache operations',
            ['cache_type', 'operation', 'result'],  # cache_type: api/validation/ucm, operation: get/set, result: hit/miss/error
            registry=registry
        )

        self.cache_hit_rate = Gauge(
            'mcp_cache_hit_rate',
            'Cache hit rate (0-1)',
            ['cache_type', 'cache_level'],  # cache_level: l1/l2/l3/l4
            registry=registry
        )

        self.cache_size_bytes = Gauge(
            'mcp_cache_size_bytes',
            'Cache size in bytes',
            ['cache_type', 'cache_level'],
            registry=registry
        )

        self.validation_performance = Histogram(
            'mcp_validation_duration_seconds',
            'Validation step duration in seconds',
            ['validation_type', 'result'],  # validation_type: fast_check/detailed/concurrent, result: pass/fail
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
            registry=registry
        )
        
        # Internal tracking for success rate calculations
        self._success_counts: Dict[str, int] = defaultdict(int)
        self._total_counts: Dict[str, int] = defaultdict(int)
        
        logger.info("Prometheus metrics initialized successfully")

    def record_tool_execution(
        self,
        tool_name: str,
        action: str,
        duration_seconds: float,
        success: bool,
        error_type: Optional[str] = None
    ) -> None:
        """Record tool execution metrics.
        
        Args:
            tool_name: Name of the tool
            action: Action performed
            duration_seconds: Execution duration in seconds
            success: Whether execution was successful
            error_type: Type of error if failed
        """
        if not self.enabled:
            return
            
        try:
            status = 'success' if success else 'error'
            
            # Record request count
            self.tool_requests_total.labels(
                tool_name=tool_name,
                action=action,
                status=status
            ).inc()
            
            # Record duration
            self.tool_duration_seconds.labels(
                tool_name=tool_name,
                action=action
            ).observe(duration_seconds)
            
            # Update success rate tracking
            key = f"{tool_name}.{action}"
            self._total_counts[key] += 1
            if success:
                self._success_counts[key] += 1
            
            # Update success rate gauge
            success_rate = self._success_counts[key] / self._total_counts[key]
            self.tool_success_rate.labels(
                tool_name=tool_name,
                action=action
            ).set(success_rate)
            
            # Record errors
            if not success and error_type:
                self.errors_total.labels(
                    error_type=error_type,
                    tool_name=tool_name,
                    action=action
                ).inc()
            
            # Check performance targets
            if duration_seconds > 0.1:  # 100ms target
                self.performance_target_violations.labels(
                    target_type='execution_time',
                    tool_name=tool_name
                ).inc()
                
            if success_rate < 0.995:  # 99.5% target
                self.performance_target_violations.labels(
                    target_type='success_rate',
                    tool_name=tool_name
                ).inc()
                
        except Exception as e:
            logger.error(f"Error recording tool execution metrics: {e}")

    def record_ucm_lookup(
        self,
        capability_type: str,
        duration_seconds: float,
        cache_hit: bool,
        cache_level: Optional[str] = None
    ) -> None:
        """Record UCM lookup metrics.
        
        Args:
            capability_type: Type of capability looked up
            duration_seconds: Lookup duration in seconds
            cache_hit: Whether this was a cache hit
            cache_level: Cache level if hit (L1, L2, L3)
        """
        if not self.enabled:
            return
            
        try:
            # Record lookup duration
            self.ucm_lookup_duration_seconds.labels(
                capability_type=capability_type
            ).observe(duration_seconds)
            
            if cache_hit and cache_level:
                self.ucm_cache_hits_total.labels(
                    cache_level=cache_level
                ).inc()
            else:
                self.ucm_cache_misses_total.labels(
                    capability_type=capability_type
                ).inc()
            
            # Check UCM performance target (50ms)
            if duration_seconds > 0.05:
                self.performance_target_violations.labels(
                    target_type='ucm_lookup',
                    tool_name='ucm'
                ).inc()
                
        except Exception as e:
            logger.error(f"Error recording UCM lookup metrics: {e}")

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_seconds: float
    ) -> None:
        """Record API request metrics.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            duration_seconds: Request duration in seconds
        """
        if not self.enabled:
            return
            
        try:
            self.api_requests_total.labels(
                endpoint=endpoint,
                method=method,
                status_code=str(status_code)
            ).inc()
            
            self.api_duration_seconds.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration_seconds)
            
        except Exception as e:
            logger.error(f"Error recording API request metrics: {e}")

    def record_cache_operation(
        self,
        cache_type: str,
        operation: str,
        result: str,
        cache_level: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> None:
        """Record cache operation metrics.

        Args:
            cache_type: Type of cache (api, validation, ucm)
            operation: Operation type (get, set)
            result: Operation result (hit, miss, error)
            cache_level: Cache level (l1, l2, l3, l4)
            duration_seconds: Operation duration in seconds
        """
        if not self.enabled:
            return

        try:
            self.cache_operations_total.labels(
                cache_type=cache_type,
                operation=operation,
                result=result
            ).inc()

            if cache_level and duration_seconds is not None:
                # Record cache performance by level
                if result == "hit":
                    # Update hit rate (this is a simplified calculation)
                    # In production, you'd want more sophisticated hit rate tracking
                    pass

        except Exception as e:
            logger.error(f"Error recording cache operation metrics: {e}")

    def record_validation_performance(
        self,
        validation_type: str,
        duration_seconds: float,
        result: str
    ) -> None:
        """Record validation performance metrics.

        Args:
            validation_type: Type of validation (fast_check, detailed, concurrent)
            duration_seconds: Validation duration in seconds
            result: Validation result (pass, fail)
        """
        if not self.enabled:
            return

        try:
            self.validation_performance.labels(
                validation_type=validation_type,
                result=result
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Error recording validation performance metrics: {e}")

    def update_cache_stats(
        self,
        cache_type: str,
        cache_level: str,
        hit_rate: float,
        size_bytes: int
    ) -> None:
        """Update cache statistics.

        Args:
            cache_type: Type of cache (api, validation, ucm)
            cache_level: Cache level (l1, l2, l3, l4)
            hit_rate: Hit rate (0.0-1.0)
            size_bytes: Cache size in bytes
        """
        if not self.enabled:
            return

        try:
            self.cache_hit_rate.labels(
                cache_type=cache_type,
                cache_level=cache_level
            ).set(hit_rate)

            self.cache_size_bytes.labels(
                cache_type=cache_type,
                cache_level=cache_level
            ).set(size_bytes)

        except Exception as e:
            logger.error(f"Error updating cache statistics: {e}")

    def update_system_metrics(
        self,
        active_connections: int,
        memory_usage_bytes: int,
        cpu_usage_percent: float
    ) -> None:
        """Update system metrics.
        
        Args:
            active_connections: Number of active connections
            memory_usage_bytes: Memory usage in bytes
            cpu_usage_percent: CPU usage percentage
        """
        if not self.enabled:
            return
            
        try:
            self.active_connections.set(active_connections)
            self.memory_usage_bytes.set(memory_usage_bytes)
            self.cpu_usage_percent.set(cpu_usage_percent)
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")

    def get_metrics(self) -> str:
        """Get Prometheus metrics in text format.
        
        Returns:
            Prometheus metrics text format
        """
        if not self.enabled:
            return "# Prometheus metrics not available\n"
            
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return f"# Error generating metrics: {e}\n"

    def get_content_type(self) -> str:
        """Get Prometheus content type.
        
        Returns:
            Content type for Prometheus metrics
        """
        return CONTENT_TYPE_LATEST if self.enabled else "text/plain"


# Global metrics instance
prometheus_metrics = PrometheusMetrics()


def record_tool_execution(
    tool_name: str,
    action: str,
    duration_seconds: float,
    success: bool,
    error_type: Optional[str] = None
) -> None:
    """Record tool execution using global metrics instance."""
    prometheus_metrics.record_tool_execution(
        tool_name, action, duration_seconds, success, error_type
    )


def record_ucm_lookup(
    capability_type: str,
    duration_seconds: float,
    cache_hit: bool,
    cache_level: Optional[str] = None
) -> None:
    """Record UCM lookup using global metrics instance."""
    prometheus_metrics.record_ucm_lookup(
        capability_type, duration_seconds, cache_hit, cache_level
    )


def record_api_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration_seconds: float
) -> None:
    """Record API request using global metrics instance."""
    prometheus_metrics.record_api_request(
        endpoint, method, status_code, duration_seconds
    )


def record_cache_operation(
    cache_type: str,
    operation: str,
    result: str,
    cache_level: Optional[str] = None,
    duration_seconds: Optional[float] = None
) -> None:
    """Record cache operation using global metrics instance."""
    prometheus_metrics.record_cache_operation(
        cache_type, operation, result, cache_level, duration_seconds
    )


def record_validation_performance(
    validation_type: str,
    duration_seconds: float,
    result: str
) -> None:
    """Record validation performance using global metrics instance."""
    prometheus_metrics.record_validation_performance(
        validation_type, duration_seconds, result
    )


def update_cache_stats(
    cache_type: str,
    cache_level: str,
    hit_rate: float,
    size_bytes: int
) -> None:
    """Update cache statistics using global metrics instance."""
    prometheus_metrics.update_cache_stats(
        cache_type, cache_level, hit_rate, size_bytes
    )


# MCP Tool Functions

@mcp.tool()
def get_prometheus_metrics(action: str = "get_metrics") -> str:
    """Get Prometheus metrics in text format.
    
    Args:
        action: The action to perform (get_metrics, get_content_type, status)
        
    Returns:
        str: Prometheus metrics text format or status information
    """
    try:
        if action == "get_metrics":
            return prometheus_metrics.get_metrics()
        elif action == "get_content_type":
            return prometheus_metrics.get_content_type()
        elif action == "status":
            return f"Prometheus metrics enabled: {prometheus_metrics.enabled}"
        else:
            return f"Unknown action: {action}. Available actions: get_metrics, get_content_type, status"
    except Exception as e:
        logger.error(f"Error in get_prometheus_metrics: {e}")
        return f"Error retrieving metrics: {str(e)}"


@mcp.tool()
def record_tool_metric(
    tool_name: str,
    action: str,
    duration_seconds: float,
    success: bool,
    error_type: Optional[str] = None
) -> str:
    """Record tool execution metrics.
    
    Args:
        tool_name: Name of the tool
        action: Action performed
        duration_seconds: Execution duration in seconds
        success: Whether execution was successful
        error_type: Type of error if failed
        
    Returns:
        str: Confirmation message
    """
    try:
        record_tool_execution(
            tool_name, action, duration_seconds, success, error_type
        )
        return f"✅ Recorded metrics for {tool_name}.{action}: {duration_seconds}s, success={success}"
    except Exception as e:
        logger.error(f"Error recording tool metric: {e}")
        return f"❌ Error recording metric: {str(e)}"
