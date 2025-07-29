"""
Performance Dashboard Tool

Provides comprehensive performance monitoring dashboard with enterprise-grade metrics.
"""

import logging
from dataclasses import dataclass
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetrics:
    """Container for dashboard metrics data."""
    summary: Dict
    overall: Dict
    ucm: Dict
    introspection: Dict


def _get_dashboard_data() -> dict:
    """Get performance dashboard data from monitoring service.
    
    Returns:
        dict: Complete dashboard data with metrics and summaries
    """
    from revenium_mcp_server.performance_monitor import get_performance_dashboard
    return get_performance_dashboard()


def _format_success_criteria_table(metrics: DashboardMetrics) -> str:
    """Format success criteria summary table.
    
    Args:
        metrics: Dashboard metrics container
    
    Returns:
        str: Formatted success criteria table
    """
    return f"""# **Performance Monitoring Dashboard**

## **Success Criteria Summary**

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Agent Success Rate | {metrics.summary['agent_success_rate_target']} | {metrics.summary['agent_success_rate_actual']} | {'✅' if metrics.overall['target_success_rate_met'] else '❌'} |
| Tool Execution Time | {metrics.summary['tool_execution_time_target']} | {metrics.summary['tool_execution_time_actual']} | {'✅' if metrics.overall['target_execution_time_met'] else '❌'} |
| UCM Lookup Time | {metrics.summary['ucm_lookup_time_target']} | {metrics.summary['ucm_lookup_time_actual']} | {'✅' if metrics.ucm['target_lookup_time_met'] else '❌'} |
| Introspection Overhead | {metrics.summary['introspection_overhead_target']} | {metrics.summary['introspection_overhead_actual']} | {'✅' if metrics.introspection['target_introspection_time_met'] else '❌'} |

**Overall Status**: {'✅ ALL TARGETS MET' if metrics.summary['all_targets_met'] else '❌ TARGETS NOT MET'}"""


def _format_detailed_metrics(metrics: DashboardMetrics) -> str:
    """Format detailed performance metrics sections.
    
    Args:
        metrics: Dashboard metrics container
    
    Returns:
        str: Formatted detailed metrics sections
    """
    return f"""
## **Detailed Metrics**

### Overall Performance
- **Total Metrics Collected**: {metrics.overall['total_metrics_collected']:,}
- **Success Rate**: {metrics.overall['success_rate_percent']:.2f}%
- **95th Percentile Execution Time**: {metrics.overall['execution_time_95th_percentile_ms']:.2f}ms
- **99th Percentile Execution Time**: {metrics.overall['execution_time_99th_percentile_ms']:.2f}ms

### UCM Performance
- **Total Lookups**: {metrics.ucm['total_lookups']:,}
- **50th Percentile**: {metrics.ucm['lookup_time_50th_percentile_ms']:.2f}ms
- **95th Percentile**: {metrics.ucm['lookup_time_95th_percentile_ms']:.2f}ms
- **99th Percentile**: {metrics.ucm['lookup_time_99th_percentile_ms']:.2f}ms

### Introspection Performance
- **Total Operations**: {metrics.introspection['total_operations']:,}
- **50th Percentile**: {metrics.introspection['time_50th_percentile_ms']:.2f}ms
- **95th Percentile**: {metrics.introspection['time_95th_percentile_ms']:.2f}ms
- **99th Percentile**: {metrics.introspection['time_99th_percentile_ms']:.2f}ms

### Tool-Specific Metrics"""


def _format_tool_specific_metrics(tool_metrics: dict) -> str:
    """Format tool-specific performance metrics.
    
    Args:
        tool_metrics: Dictionary of tool-specific metrics
    
    Returns:
        str: Formatted tool-specific metrics
    """
    metrics_text = ""
    for tool_name, metrics in tool_metrics.items():
        metrics_text += f"""
**{tool_name}**:
- Success Rate: {metrics['success_rate']:.2f}%
- Total Calls: {metrics['total_calls']:,}
- Avg Execution Time: {metrics['avg_execution_time']:.2f}ms
- 95th Percentile: {metrics['95th_percentile']:.2f}ms
"""
    return metrics_text


def _format_dashboard_footer(dashboard_data: dict, summary: dict) -> str:
    """Format dashboard footer with timestamps and status.
    
    Args:
        dashboard_data: Complete dashboard data
        summary: Success criteria summary
    
    Returns:
        str: Formatted dashboard footer
    """
    return f"""

---
**Last Updated**: {dashboard_data['timestamp']}
**Enterprise-Grade Completion Standards**: {'✅ MET' if summary['all_targets_met'] else '❌ NOT MET'}"""


def _handle_dashboard_error(e: Exception) -> str:
    """Handle dashboard generation errors with structured error response.
    
    Args:
        e: Exception that occurred during dashboard generation
    
    Returns:
        str: Formatted error response
    """
    logger.error(f"Error generating performance dashboard: {e}")
    from revenium_mcp_server.common.error_handling import ToolError, ErrorCodes
    error = ToolError(
        message="Failed to generate performance dashboard",
        error_code=ErrorCodes.TOOL_ERROR,
        field="performance_dashboard",
        value=str(e),
        suggestions=[
            "Check system performance monitoring service status",
            "Verify performance metrics collection is working",
            "Try again after a few moments",
            "Contact system administrator if issue persists"
        ],
        examples={
            "troubleshooting": ["Check service status", "Verify metrics collection", "Test connectivity"],
            "system_context": "🔧 SYSTEM: Performance dashboard provides enterprise-grade monitoring metrics"
        }
    )
    from revenium_mcp_server.common.error_handling import format_structured_error
    return format_structured_error(error)


def _build_complete_dashboard(dashboard_data: dict, metrics: DashboardMetrics) -> str:
    """Build complete dashboard by combining all sections.
    
    Args:
        dashboard_data: Raw dashboard data
        metrics: Structured metrics container
        
    Returns:
        str: Complete formatted dashboard
    """
    success_table = _format_success_criteria_table(metrics)
    detailed_metrics = _format_detailed_metrics(metrics)
    tool_metrics = _format_tool_specific_metrics(dashboard_data["tool_specific_metrics"])
    footer = _format_dashboard_footer(dashboard_data, metrics.summary)
    
    return success_table + detailed_metrics + tool_metrics + footer


def performance_dashboard() -> str:
    """Get comprehensive performance monitoring dashboard with enterprise-grade metrics.

    Returns performance metrics including:
    - Agent success rate (target: ≥99.5%)
    - Tool execution time (target: ≤100ms 95th percentile)
    - UCM lookup performance (target: ≤50ms 99th percentile)
    - Introspection overhead (target: ≤10ms 95th percentile)
    """
    try:
        dashboard_data = _get_dashboard_data()
        
        metrics = DashboardMetrics(
            summary=dashboard_data["success_criteria_summary"],
            overall=dashboard_data["overall_metrics"],
            ucm=dashboard_data["ucm_performance"],
            introspection=dashboard_data["introspection_performance"]
        )
        
        return _build_complete_dashboard(dashboard_data, metrics)
        
    except Exception as e:
        return _handle_dashboard_error(e)