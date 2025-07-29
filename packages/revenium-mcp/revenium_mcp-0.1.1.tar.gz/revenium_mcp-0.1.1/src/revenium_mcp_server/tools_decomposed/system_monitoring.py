"""System Monitoring Tool

Unified system monitoring tool providing performance dashboards and metrics export
for comprehensive system health monitoring and performance analysis.
"""

from typing import Any, Dict, List, Optional, Union, ClassVar
from loguru import logger

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .unified_tool_base import ToolBase
from .fastmcp_performance_dashboard import FastMCPPerformanceDashboard
from ..common.error_handling import (
    create_structured_validation_error,
    format_structured_error
)
from ..introspection.metadata import ToolType


class SystemMonitoring(ToolBase):
    """FastMCP performance monitoring tool.

    Provides FastMCP-specific performance monitoring capabilities including:
    - FastMCP monitoring: Framework-specific performance tracking with real-time alerting
    """
    
    tool_name: ClassVar[str] = "system_monitoring"
    tool_description: ClassVar[str] = "FastMCP performance monitoring with real-time alerting and enhanced monitoring. Key actions: performance_dashboard. Use get_capabilities() for complete action list."
    business_category: ClassVar[str] = "System & Monitoring Tools"
    tool_type: ClassVar[ToolType] = ToolType.ANALYTICS
    tool_version: ClassVar[str] = "1.0.0"
    
    def __init__(self, ucm_helper=None):
        """Initialize consolidated system monitoring tool.
        
        Args:
            ucm_helper: UCM integration helper for capability management
        """
        super().__init__(ucm_helper)
        
        # Initialize source tool instances for delegation
        self.fastmcp_tool = FastMCPPerformanceDashboard(ucm_helper)
        
        # Action routing map - maps actions to source tools
        self.action_routing = {
            # FastMCP performance dashboard actions
            "performance_dashboard": self.fastmcp_tool
        }
        
        logger.info("🔧 System Monitoring consolidated tool initialized")
    
    async def handle_action(
        self,
        action: str,
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle system monitoring actions using delegation.
        
        Args:
            action: Action to perform
            arguments: Action arguments
            
        Returns:
            Tool response from delegated source tool
        """
        try:
            # Handle meta actions directly
            if action == "get_capabilities":
                return await self._handle_get_capabilities()
            elif action == "get_examples":
                return await self._handle_get_examples()
            
            # Route action to appropriate source tool
            if action in self.action_routing:
                source_tool = self.action_routing[action]
                logger.debug(f"Delegating action '{action}' to {source_tool.__class__.__name__}")
                return await source_tool.handle_action(action, arguments)
            else:
                # Unknown action - provide helpful error
                return await self._handle_unknown_action(action)
                
        except Exception as e:
            logger.error(f"Error in system monitoring action '{action}': {e}")
            raise e
    
    async def _handle_get_capabilities(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get consolidated capabilities from all source tools."""
        capabilities_text = f"""# System Monitoring - FastMCP Performance Tool

## **What This Tool Does**
FastMCP performance monitoring with real-time alerting and enhanced monitoring capabilities for framework-specific performance tracking.

## **Key Capabilities**

### **FastMCP Performance Dashboard**
• **Real-time Monitoring**: FastMCP-specific performance metrics
• **Latency Tracking**: P50, P95, P99 percentile analysis
• **Throughput Monitoring**: Operations per second tracking
• **Error Rate Analysis**: Error tracking with alerting
• **Cache Performance**: Hit rate and efficiency metrics

## **Primary Use Cases**
• **FastMCP Monitoring**: Track FastMCP framework performance
• **Performance Optimization**: Identify FastMCP bottlenecks and slow operations
• **Real-time Alerting**: Monitor FastMCP performance with alerts
• **Troubleshooting**: Diagnose FastMCP performance issues

## **Available Actions**

### Performance Monitoring
- `performance_dashboard` - FastMCP-specific performance metrics

### Meta Actions
- `get_capabilities` - Show this capabilities overview
- `get_examples` - Show usage examples for all actions

## **Performance Targets**
• **Agent Success Rate**: ≥99.5%
• **Tool Execution Time**: ≤100ms 95th percentile
• **UCM Lookup Performance**: ≤50ms 99th percentile
• **Introspection Overhead**: ≤10ms 95th percentile

Use `get_examples()` for detailed usage examples and parameter guidance.
"""
        
        return [TextContent(type="text", text=capabilities_text)]
    
    async def _handle_get_examples(self) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get examples from all source tools."""
        examples_text = f"""# System Monitoring Examples

## **FastMCP Performance Dashboard Examples**

### Get FastMCP Performance Dashboard
```json
{{"action": "performance_dashboard"}}
```

## **Common Monitoring Workflows**

### FastMCP Performance Check
1. `performance_dashboard()` - Check FastMCP-specific metrics and performance

### Performance Troubleshooting
1. `performance_dashboard()` - Analyze FastMCP bottlenecks and performance issues
2. Review specific FastMCP metrics in dashboard output

## **Dashboard Features**

### FastMCP Performance Dashboard
- Real-time latency percentiles (P50, P95, P99)
- Throughput monitoring (ops/second)
- Error rate tracking with alerting
- Memory and CPU usage monitoring
- Cache hit rate analysis

## **Performance Monitoring Best Practices**
• **Regular Monitoring**: Check FastMCP dashboard regularly for trends
• **Baseline Establishment**: Track normal FastMCP performance patterns
• **Proactive Optimization**: Address FastMCP issues before they impact users

All actions support the same parameters as their original tools for 100% compatibility.
"""
        
        return [TextContent(type="text", text=examples_text)]
    
    async def _handle_unknown_action(self, action: str) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle unknown actions with helpful guidance."""
        all_actions = list(self.action_routing.keys()) + ["get_capabilities", "get_examples"]
        
        error = create_structured_validation_error(
            field="action",
            value=action,
            message=f"Unknown system monitoring action: {action}",
            examples={
                "valid_actions": all_actions,
                "dashboard_actions": ["performance_dashboard"],
                "example_usage": {
                    "performance_dashboard": "FastMCP-specific performance metrics"
                }
            }
        )
        
        return [TextContent(type="text", text=format_structured_error(error))]
    
    async def _get_supported_actions(self) -> List[str]:
        """Get all supported actions from consolidated tool."""
        return list(self.action_routing.keys()) + ["get_capabilities", "get_examples"]
