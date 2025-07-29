"""Prometheus Metrics Tool for Revenium MCP Server.

This tool provides Prometheus-compatible metrics for external monitoring systems.
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


class PrometheusMetrics(ToolBase):
    """Prometheus metrics provider for external monitoring systems.
    
    This tool provides Prometheus-compatible metrics in text format for integration
    with Prometheus monitoring systems, Grafana dashboards, and external alerting.
    """
    
    tool_name: ClassVar[str] = "prometheus_metrics"
    tool_description: ClassVar[str] = "Get Prometheus-compatible metrics for external monitoring systems"
    business_category: ClassVar[str] = "System & Monitoring Tools"
    tool_type = ToolType.UTILITY
    tool_version = "1.0.0"
    
    def __init__(self, ucm_helper=None):
        """Initialize Prometheus metrics.
        
        Args:
            ucm_helper: UCM integration helper for capability management
        """
        super().__init__(ucm_helper)
        self.formatter = UnifiedResponseFormatter("prometheus_metrics")
    
    async def handle_action(
        self, 
        action: str, 
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle Prometheus metrics actions.
        
        Args:
            action: Action to perform
            arguments: Action arguments
            
        Returns:
            Prometheus metrics response
        """
        try:
            if action == "get_metrics":
                return await self._handle_get_metrics(arguments)
            elif action == "get_capabilities":
                return await self._handle_get_capabilities()
            elif action == "get_examples":
                return await self._handle_get_examples()
            else:
                raise ToolError(
                    message=f"Unknown Prometheus metrics action: {action}",
                    error_code=ErrorCodes.ACTION_NOT_SUPPORTED,
                    field="action",
                    value=action,
                    suggestions=[
                        "Use get_metrics() to retrieve Prometheus metrics",
                        "Use get_capabilities() to see available actions",
                        "Use get_examples() for usage examples"
                    ],
                    examples={
                        "valid_actions": ["get_metrics", "get_capabilities", "get_examples"]
                    }
                )
                
        except ToolError as e:
            logger.error(f"Tool error in Prometheus metrics: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error in Prometheus metrics: {e}")
            raise e
    
    async def _handle_get_metrics(self, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get metrics action."""
        try:
            from ..prometheus_metrics import prometheus_metrics
            metrics_text = prometheus_metrics.get_metrics()
            
            # Format with proper headers for Prometheus format
            formatted_metrics = f"""# Revenium MCP Server Prometheus Metrics
# Generated at: {prometheus_metrics.get_timestamp() if hasattr(prometheus_metrics, 'get_timestamp') else 'N/A'}

{metrics_text}"""
            
            return [TextContent(type="text", text=formatted_metrics)]
            
        except ImportError:
            error_text = """# Prometheus Metrics Error

Prometheus metrics module not available. Please ensure:
1. prometheus_metrics module is properly configured
2. Required dependencies are installed
3. Metrics collection is enabled

Example metrics format:
```
# HELP revenium_tool_calls_total Total number of tool calls
# TYPE revenium_tool_calls_total counter
revenium_tool_calls_total{tool="manage_alerts"} 42

# HELP revenium_response_time_seconds Tool response time in seconds
# TYPE revenium_response_time_seconds histogram
revenium_response_time_seconds_bucket{le="0.1"} 100
revenium_response_time_seconds_bucket{le="0.5"} 150
revenium_response_time_seconds_bucket{le="1.0"} 200
revenium_response_time_seconds_bucket{le="+Inf"} 200
revenium_response_time_seconds_count 200
revenium_response_time_seconds_sum 45.2
```"""
            return [TextContent(type="text", text=error_text)]
        except Exception as e:
            error_text = f"""# Prometheus Metrics Error

Unable to retrieve metrics: {str(e)}

Please check:
1. Metrics collection is properly configured
2. Performance monitoring is enabled
3. Prometheus metrics module is available"""
            return [TextContent(type="text", text=error_text)]
    
    async def _handle_get_capabilities(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get capabilities action."""
        capabilities_text = """# **Prometheus Metrics Capabilities**

## **Purpose**
Provides Prometheus-compatible metrics for external monitoring systems.

## **Available Actions**
- `get_metrics` - Retrieve metrics in Prometheus text format
- `get_capabilities` - Show this capabilities overview
- `get_examples` - Show usage examples

## **Key Features**
- **Prometheus Format** - Standard Prometheus text format output
- **Tool Metrics** - Tool execution counts, response times, error rates
- **System Metrics** - Memory usage, CPU usage, connection counts
- **Custom Labels** - Tool-specific and action-specific labels
- **Histogram Support** - Response time percentiles and buckets

## **Integration Targets**
- **Prometheus** - Direct scraping of metrics endpoint
- **Grafana** - Dashboard visualization and alerting
- **External Alerting** - Custom alerting systems
- **Performance Monitoring** - Third-party monitoring tools

## **Metric Types**
- **Counters** - Tool call counts, error counts
- **Gauges** - Active connections, memory usage
- **Histograms** - Response time distributions
- **Summaries** - Performance percentiles
"""
        return [TextContent(type="text", text=capabilities_text)]
    
    async def _handle_get_examples(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get examples action."""
        examples_text = """# **Prometheus Metrics Examples**

## **Get All Metrics**
```json
{
  "action": "get_metrics"
}
```

## **Sample Prometheus Output**
```
# HELP revenium_tool_calls_total Total number of tool calls
# TYPE revenium_tool_calls_total counter
revenium_tool_calls_total{tool="manage_alerts",action="create_alert"} 42
revenium_tool_calls_total{tool="manage_products",action="list_products"} 156

# HELP revenium_response_time_seconds Tool response time in seconds
# TYPE revenium_response_time_seconds histogram
revenium_response_time_seconds_bucket{tool="manage_alerts",le="0.1"} 100
revenium_response_time_seconds_bucket{tool="manage_alerts",le="0.5"} 150
revenium_response_time_seconds_bucket{tool="manage_alerts",le="1.0"} 200
revenium_response_time_seconds_count{tool="manage_alerts"} 200
revenium_response_time_seconds_sum{tool="manage_alerts"} 45.2

# HELP revenium_errors_total Total number of errors
# TYPE revenium_errors_total counter
revenium_errors_total{tool="manage_alerts",error_type="validation"} 3
```

## **Integration Examples**

### **Prometheus Configuration**
```yaml
scrape_configs:
  - job_name: 'revenium-mcp'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### **Grafana Dashboard Query**
```promql
rate(revenium_tool_calls_total[5m])
histogram_quantile(0.95, rate(revenium_response_time_seconds_bucket[5m]))
```

## **Usage Tips**
1. **Regular Collection**: Set up automated scraping every 30-60 seconds
2. **Alerting Rules**: Configure alerts for error rates and response times
3. **Dashboard Creation**: Use Grafana for visual monitoring
4. **Capacity Planning**: Monitor resource usage trends
"""
        return [TextContent(type="text", text=examples_text)]