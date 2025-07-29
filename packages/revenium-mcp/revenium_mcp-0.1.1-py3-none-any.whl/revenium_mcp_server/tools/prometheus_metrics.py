"""Prometheus Metrics Tool

Provides Prometheus-compatible metrics for external monitoring systems.
Extracted from enhanced_server.py as part of the refactoring effort.
"""

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
mcp = FastMCP("prometheus_metrics_tool") if FASTMCP_AVAILABLE else FastMCP()


@mcp.tool()
async def prometheus_metrics() -> str:
    """Get Prometheus-compatible metrics for external monitoring systems.

    Returns metrics in Prometheus text format for integration with:
    - Prometheus monitoring systems
    - Grafana dashboards
    - External alerting systems
    - Performance monitoring tools
    """
    try:
        from revenium_mcp_server.prometheus_metrics import prometheus_metrics

        metrics_text = prometheus_metrics.get_metrics()

        # Add header information
        header = """# Revenium MCP Server Metrics
# TYPE mcp_tool_requests_total counter
# HELP mcp_tool_requests_total Total number of tool requests
# TYPE mcp_tool_duration_seconds histogram
# HELP mcp_tool_duration_seconds Tool execution duration in seconds
# TYPE mcp_tool_success_rate gauge
# HELP mcp_tool_success_rate Tool success rate (0-1)
# TYPE mcp_ucm_lookup_duration_seconds histogram
# HELP mcp_ucm_lookup_duration_seconds UCM capability lookup duration in seconds
# TYPE mcp_api_requests_total counter
# HELP mcp_api_requests_total Total API requests
# TYPE mcp_errors_total counter
# HELP mcp_errors_total Total errors by type
# TYPE mcp_performance_target_violations_total counter
# HELP mcp_performance_target_violations_total Performance target violations

"""

        return header + metrics_text

    except Exception as e:
        logger.error(f"Error generating Prometheus metrics: {e}")
        return f"""# Error generating Prometheus metrics
# Error: {str(e)}
# Timestamp: {datetime.now(timezone.utc).isoformat()}

# Fallback metrics
mcp_server_status{{status="error"}} 0
mcp_metrics_generation_errors_total 1
"""