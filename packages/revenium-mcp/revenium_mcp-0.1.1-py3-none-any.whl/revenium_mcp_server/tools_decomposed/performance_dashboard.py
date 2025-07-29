"""Performance Dashboard Tool for Revenium MCP Server.

This tool provides comprehensive performance monitoring focused on overall system health,
includes dashboard with enterprise-grade metrics.
"""

import json
from typing import Any, Dict, List, Union, ClassVar
from loguru import logger

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .unified_tool_base import ToolBase
from ..introspection.metadata import ToolType, ToolCapability
from ..agent_friendly import UnifiedResponseFormatter
from ..common.error_handling import (
    ErrorCodes, ToolError,
    create_structured_validation_error,
    create_structured_missing_parameter_error,
    format_structured_error
)


class PerformanceDashboard(ToolBase):
    """Performance dashboard with comprehensive system health monitoring.
    
    This tool provides enterprise-grade performance metrics for overall system health
    including agent success rates, tool execution times, and performance targets.
    """
    
    tool_name: ClassVar[str] = "performance_dashboard"
    tool_description: ClassVar[str] = "Get comprehensive performance monitoring focused on overall system health, includes dashboard with enterprise-grade metrics"
    business_category: ClassVar[str] = "System & Monitoring Tools"
    tool_type = ToolType.ANALYTICS
    tool_version = "1.0.0"
    
    def __init__(self, ucm_helper=None):
        """Initialize performance dashboard.
        
        Args:
            ucm_helper: UCM integration helper for capability management
        """
        super().__init__(ucm_helper)
        self.formatter = UnifiedResponseFormatter("performance_dashboard")
    
    async def handle_action(
        self, 
        action: str, 
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle performance dashboard actions.
        
        Args:
            action: Action to perform
            arguments: Action arguments
            
        Returns:
            Performance dashboard response
        """
        try:
            if action == "get_dashboard":
                return await self._handle_get_dashboard(arguments)
            elif action == "get_capabilities":
                return await self._handle_get_capabilities()
            elif action == "get_examples":
                return await self._handle_get_examples()
            else:
                raise ToolError(
                    message=f"Unknown performance dashboard action: {action}",
                    error_code=ErrorCodes.ACTION_NOT_SUPPORTED,
                    field="action",
                    value=action,
                    suggestions=[
                        "Use get_dashboard() to view performance metrics",
                        "Use get_capabilities() to see available actions",
                        "Use get_examples() for usage examples"
                    ],
                    examples={
                        "valid_actions": ["get_dashboard", "get_capabilities", "get_examples"]
                    }
                )
                
        except ToolError as e:
            logger.error(f"Tool error in performance dashboard: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error in performance dashboard: {e}")
            raise e
    
    async def _handle_get_dashboard(self, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get dashboard action."""
        try:
            from ..performance_monitor import get_performance_dashboard
            dashboard_data = get_performance_dashboard()
            
            dashboard_text = """# **Performance Dashboard**

## **System Health Overview**

### **Agent Performance**
- **Success Rate**: {agent_success_rate}% (Target: ≥99.5%)
- **Error Rate**: {agent_error_rate}%
- **Uptime**: {uptime}

### **Tool Execution Metrics**
- **Average Response Time**: {avg_response_time}ms
- **95th Percentile**: {p95_response_time}ms (Target: ≤100ms)
- **99th Percentile**: {p99_response_time}ms
- **Total Tool Calls**: {total_tool_calls}

### **UCM Performance**
- **Lookup Performance**: {ucm_lookup_time}ms (Target: ≤50ms 99th percentile)
- **Cache Hit Rate**: {cache_hit_rate}%
- **Cache Size**: {cache_size} entries

### **Introspection Overhead**
- **Average Overhead**: {introspection_overhead}ms (Target: ≤10ms 95th percentile)
- **Registration Time**: {registration_time}ms

### **Resource Usage**
- **Memory Usage**: {memory_usage}MB
- **CPU Usage**: {cpu_usage}%
- **Active Connections**: {active_connections}

### **Performance Targets**
- 🎯 **Agent Success Rate**: ≥99.5%
- 🎯 **Tool Response Time**: ≤100ms (95th percentile)
- 🎯 **UCM Lookup Time**: ≤50ms (99th percentile)
- 🎯 **Introspection Overhead**: ≤10ms (95th percentile)

**Status**: {overall_status}
""".format(
                agent_success_rate=dashboard_data.get("agent_success_rate", "N/A"),
                agent_error_rate=dashboard_data.get("agent_error_rate", "N/A"),
                uptime=dashboard_data.get("uptime", "N/A"),
                avg_response_time=dashboard_data.get("avg_response_time", "N/A"),
                p95_response_time=dashboard_data.get("p95_response_time", "N/A"),
                p99_response_time=dashboard_data.get("p99_response_time", "N/A"),
                total_tool_calls=dashboard_data.get("total_tool_calls", "N/A"),
                ucm_lookup_time=dashboard_data.get("ucm_lookup_time", "N/A"),
                cache_hit_rate=dashboard_data.get("cache_hit_rate", "N/A"),
                cache_size=dashboard_data.get("cache_size", "N/A"),
                introspection_overhead=dashboard_data.get("introspection_overhead", "N/A"),
                registration_time=dashboard_data.get("registration_time", "N/A"),
                memory_usage=dashboard_data.get("memory_usage", "N/A"),
                cpu_usage=dashboard_data.get("cpu_usage", "N/A"),
                active_connections=dashboard_data.get("active_connections", "N/A"),
                overall_status=dashboard_data.get("overall_status", "Healthy")
            )
            
            return [TextContent(type="text", text=dashboard_text)]
            
        except Exception as e:
            error_text = f"# **Performance Dashboard Error**\n\nUnable to retrieve performance data: {str(e)}\n\nPlease ensure the performance monitoring system is properly configured."
            return [TextContent(type="text", text=error_text)]
    
    async def _handle_get_capabilities(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get capabilities action."""
        capabilities_text = """# **Performance Dashboard Capabilities**

## **Purpose**
Comprehensive performance monitoring focused on overall system health with enterprise-grade metrics.

## **Available Actions**
- `get_dashboard` - View comprehensive performance metrics and system health
- `get_capabilities` - Show this capabilities overview
- `get_examples` - Show usage examples

## **Key Features**
- **Agent Performance Monitoring** - Success rates, error tracking, uptime
- **Tool Execution Metrics** - Response times, percentile analysis, call volumes
- **UCM Performance Tracking** - Lookup times, cache performance
- **Resource Monitoring** - Memory, CPU, connection tracking
- **Performance Targets** - Enterprise-grade SLA monitoring

## **Integration**
- Works with performance_monitor module
- Provides enterprise-grade metrics
- Supports performance target compliance tracking
"""
        return [TextContent(type="text", text=capabilities_text)]
    
    async def _handle_get_examples(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get examples action."""
        examples_text = """# **Performance Dashboard Examples**

## **View Performance Dashboard**
```json
{
  "action": "get_dashboard"
}
```

## **Get Tool Capabilities**
```json
{
  "action": "get_capabilities"
}
```

## **Usage Tips**
1. **Regular Monitoring**: Use `get_dashboard()` for regular system health checks
2. **Performance Analysis**: Monitor response time percentiles for optimization opportunities
3. **Target Compliance**: Track performance against enterprise SLA targets
4. **Resource Planning**: Use resource metrics for capacity planning

## **Performance Targets**
- **Agent Success Rate**: ≥99.5%
- **Tool Response Time**: ≤100ms (95th percentile)
- **UCM Lookup Time**: ≤50ms (99th percentile)
- **Introspection Overhead**: ≤10ms (95th percentile)
"""
        return [TextContent(type="text", text=examples_text)]