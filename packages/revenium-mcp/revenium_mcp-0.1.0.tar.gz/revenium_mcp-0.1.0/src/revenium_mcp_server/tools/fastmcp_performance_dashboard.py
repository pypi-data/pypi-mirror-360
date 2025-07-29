"""FastMCP Performance Dashboard Tool

Provides FastMCP performance dashboard with real-time alerting and enhanced monitoring.
Refactored to meet enterprise Python standards with functions ≤25 lines.
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


def _get_dashboard_data() -> Dict[str, Any]:
    """Get FastMCP dashboard data from performance module.
    
    Returns:
        Dictionary containing dashboard data and metrics
    """
    from revenium_mcp_server.fastmcp_performance import get_fastmcp_dashboard
    return get_fastmcp_dashboard()


def _format_no_data_response(dashboard_data: Dict[str, Any]) -> str:
    """Format response when no performance data is available.
    
    Args:
        dashboard_data: Dashboard data containing status and message
        
    Returns:
        Formatted no data response string
    """
    return f"""# **FastMCP Performance Dashboard**

⚠️ **Status**: No recent performance data available

**Message**: {dashboard_data["message"]}

**Recommendations**:
- Wait for tool operations to generate performance data
- Check if performance monitoring is enabled
- Verify FastMCP decorators are applied to tools

**Next Steps**:
- Use any MCP tool to generate performance metrics
- Check back in a few minutes for updated data
"""


def _extract_dashboard_components(dashboard_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Extract main dashboard components from data.
    
    Args:
        dashboard_data: Complete dashboard data
        
    Returns:
        Tuple of (performance_summary, compliance, alerts)
    """
    perf = dashboard_data["performance_summary"]
    compliance = dashboard_data["target_compliance"]
    alerts = dashboard_data["alerts"]
    return perf, compliance, alerts


def _get_status_emoji(dashboard_data: Dict[str, Any]) -> str:
    """Get status emoji based on dashboard health.
    
    Args:
        dashboard_data: Dashboard data containing status
        
    Returns:
        Status emoji string
    """
    return "🟢" if dashboard_data["status"] == "healthy" else "🔴"


def _format_dashboard_header(dashboard_data: Dict[str, Any], status_emoji: str) -> str:
    """Format dashboard header section.
    
    Args:
        dashboard_data: Dashboard data containing metadata
        status_emoji: Status emoji for the header
        
    Returns:
        Formatted header string
    """
    return f"""# **FastMCP Performance Dashboard** {status_emoji}

**Status**: {dashboard_data["status"].upper()}
**Last Updated**: {dashboard_data["timestamp"]}
**Monitoring Window**: {dashboard_data["monitoring_window_hours"]} hour(s)
**Metrics Collected**: {dashboard_data["metrics_collected"]:,}

"""


def _format_latency_metrics(perf: Dict[str, Any], compliance: Dict[str, Any]) -> str:
    """Format latency metrics subsection.
    
    Args:
        perf: Performance summary data
        compliance: Target compliance data
        
    Returns:
        Formatted latency metrics string
    """
    return f"""### **Latency Metrics**
- **P50 Latency**: {perf["latency_p50_ms"]:.2f}ms
- **P95 Latency**: {perf["latency_p95_ms"]:.2f}ms {'✅' if compliance["latency_p95_target_met"] else '❌'} (Target: ≤100ms)
- **P99 Latency**: {perf["latency_p99_ms"]:.2f}ms {'✅' if compliance["latency_p99_target_met"] else '❌'} (Target: ≤250ms)
"""


def _format_throughput_reliability(perf: Dict[str, Any], compliance: Dict[str, Any]) -> str:
    """Format throughput and reliability subsection.
    
    Args:
        perf: Performance summary data
        compliance: Target compliance data
        
    Returns:
        Formatted throughput and reliability string
    """
    return f"""### **Throughput & Reliability**
- **Average Throughput**: {perf["throughput_avg_ops_per_sec"]:.2f} ops/sec
- **Error Rate**: {perf["error_rate_avg_percent"]:.2f}% {'✅' if compliance["error_rate_target_met"] else '❌'} (Target: ≤1.0%)
"""


def _format_resource_usage(perf: Dict[str, Any]) -> str:
    """Format resource usage subsection.
    
    Args:
        perf: Performance summary data
        
    Returns:
        Formatted resource usage string
    """
    return f"""### **Resource Usage**
- **Memory Usage**: {perf["memory_usage_avg_mb"]:.2f} MB
- **CPU Usage**: {perf["cpu_usage_avg_percent"]:.2f}%
- **Cache Hit Rate**: {perf["cache_hit_rate_avg_percent"]:.2f}%
"""


def _format_performance_summary(perf: Dict[str, Any], compliance: Dict[str, Any]) -> str:
    """Format performance summary section.
    
    Args:
        perf: Performance summary data
        compliance: Target compliance data
        
    Returns:
        Formatted performance summary string
    """
    latency = _format_latency_metrics(perf, compliance)
    throughput = _format_throughput_reliability(perf, compliance)
    resources = _format_resource_usage(perf)
    
    return f"""## **Performance Summary**

{latency}

{throughput}

{resources}

"""


def _format_alert_summary(alerts: Dict[str, Any]) -> str:
    """Format alert summary subsection.
    
    Args:
        alerts: Alerts data containing active alert counts
        
    Returns:
        Formatted alert summary string
    """
    return f"""## **Active Alerts**

**Total Active**: {alerts["total_active"]}
- **Critical**: {alerts["critical"]} 🔴
- **Warning**: {alerts["warning"]} 🟡

"""


def _format_recent_alerts_list(alerts: Dict[str, Any]) -> str:
    """Format recent alerts list subsection.
    
    Args:
        alerts: Alerts data containing recent alerts
        
    Returns:
        Formatted recent alerts list string
    """
    if alerts["recent_alerts"]:
        alerts_text = "### **Recent Alerts**\n"
        for alert in alerts["recent_alerts"]:
            severity_emoji = "🔴" if alert["severity"] == "CRITICAL" else "🟡"
            alerts_text += f"- {severity_emoji} **{alert['severity']}**: {alert['message']} ({alert['tool_name']})\n"
    else:
        alerts_text = "### **Recent Alerts**\n✅ No active alerts\n"
    return alerts_text


def _format_alerts_section(alerts: Dict[str, Any]) -> str:
    """Format active alerts section.
    
    Args:
        alerts: Alerts data containing active alerts and recent alerts
        
    Returns:
        Formatted alerts section string
    """
    summary = _format_alert_summary(alerts)
    recent = _format_recent_alerts_list(alerts)
    return summary + recent + "\n"


def _format_compliance_section(compliance: Dict[str, Any]) -> str:
    """Format target compliance section.
    
    Args:
        compliance: Target compliance data
        
    Returns:
        Formatted compliance section string
    """
    return f"""## **Target Compliance**

- **Latency P95**: {'✅ PASS' if compliance["latency_p95_target_met"] else '❌ FAIL'} (≤100ms)
- **Latency P99**: {'✅ PASS' if compliance["latency_p99_target_met"] else '❌ FAIL'} (≤250ms)
- **Error Rate**: {'✅ PASS' if compliance["error_rate_target_met"] else '❌ FAIL'} (≤1.0%)

"""


def _format_features_section() -> str:
    """Format FastMCP features section.
    
    Returns:
        Formatted features section string
    """
    return """## **FastMCP Features**

- ✅ Real-time performance monitoring
- ✅ Automated alerting system
- ✅ Percentile-based latency tracking
- ✅ Throughput analysis
- ✅ Resource usage monitoring
- ✅ Performance baseline calculation
- ✅ Target compliance validation

---
**FastMCP Performance Monitoring**: Enhanced real-time visibility with automated alerting
"""


def _get_error_suggestions() -> list:
    """Get error suggestions for dashboard failures.
    
    Returns:
        List of error suggestions
    """
    return [
        "Check FastMCP performance monitoring service status",
        "Verify performance metrics collection is working",
        "Try again after a few moments",
        "Contact system administrator if issue persists"
    ]


def _get_error_examples() -> dict:
    """Get error examples for dashboard failures.
    
    Returns:
        Dictionary of error examples
    """
    return {
        "troubleshooting": ["Check service status", "Verify metrics collection", "Test connectivity"],
        "system_context": "🔧 SYSTEM: FastMCP dashboard provides real-time performance monitoring with alerting"
    }


def _create_dashboard_error(e: Exception) -> 'ToolError':
    """Create structured error for dashboard failures.
    
    Args:
        e: Exception that occurred during dashboard generation
        
    Returns:
        ToolError object for dashboard failure
    """
    from revenium_mcp_server.common.error_handling import ToolError, ErrorCodes
    
    return ToolError(
        message="Failed to generate FastMCP performance dashboard",
        error_code=ErrorCodes.TOOL_ERROR,
        field="fastmcp_performance_dashboard",
        value=str(e),
        suggestions=_get_error_suggestions(),
        examples=_get_error_examples()
    )


def _handle_dashboard_error(e: Exception) -> str:
    """Handle dashboard generation errors.
    
    Args:
        e: Exception that occurred during dashboard generation
        
    Returns:
        Formatted error response string
    """
    logger.error(f"Error generating FastMCP performance dashboard: {e}")
    error = _create_dashboard_error(e)
    from revenium_mcp_server.common.error_handling import format_structured_error
    return format_structured_error(error)


def _build_complete_dashboard(dashboard_data: Dict[str, Any]) -> str:
    """Build complete dashboard from data components.
    
    Args:
        dashboard_data: Complete dashboard data
        
    Returns:
        Formatted complete dashboard string
    """
    perf, compliance, alerts = _extract_dashboard_components(dashboard_data)
    status_emoji = _get_status_emoji(dashboard_data)
    
    header = _format_dashboard_header(dashboard_data, status_emoji)
    performance_summary = _format_performance_summary(perf, compliance)
    alerts_section = _format_alerts_section(alerts)
    compliance_section = _format_compliance_section(compliance)
    features_section = _format_features_section()
    
    return header + performance_summary + alerts_section + compliance_section + features_section


def fastmcp_performance_dashboard() -> str:
    """Get FastMCP performance dashboard with real-time alerting and enhanced monitoring.

    Returns FastMCP-specific performance metrics including:
    - Real-time latency percentiles (P50, P95, P99)
    - Throughput monitoring (ops/second)
    - Error rate tracking with alerting
    - Memory and CPU usage monitoring
    - Cache hit rate analysis
    - Active performance alerts
    - Target compliance status
    
    Returns:
        Formatted dashboard string
    """
    try:
        dashboard_data = _get_dashboard_data()
        
        if dashboard_data["status"] == "no_data":
            return _format_no_data_response(dashboard_data)
        
        return _build_complete_dashboard(dashboard_data)
        
    except Exception as e:
        return _handle_dashboard_error(e)