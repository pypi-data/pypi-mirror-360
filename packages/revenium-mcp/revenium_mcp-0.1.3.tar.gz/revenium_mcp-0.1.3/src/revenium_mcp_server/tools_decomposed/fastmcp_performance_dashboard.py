"""FastMCP Performance Dashboard Tool for Revenium MCP Server.

This tool provides FastMCP performance dashboard with real-time alerting and enhanced monitoring.
Refactored to meet enterprise Python standards with functions ≤25 lines and class-based architecture.
Split into modules to maintain ≤300 lines per module enterprise standard.
"""

from typing import Any, Dict, List, Optional, Union, ClassVar

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .unified_tool_base import ToolBase
from .fastmcp_performance_formatters import FastMCPPerformanceFormatters
from .fastmcp_performance_errors import FastMCPPerformanceErrors
from ..common.error_handling import (
    ErrorCodes, ToolError,
    create_structured_missing_parameter_error,
    create_structured_validation_error
)
from ..introspection.metadata import ToolType, ToolCapability, UsagePattern


class FastMCPPerformanceDashboard(ToolBase):
    """FastMCP Performance Dashboard Tool.
    
    Provides FastMCP performance dashboard with real-time alerting and enhanced monitoring.
    """
    
    tool_name: ClassVar[str] = "fastmcp_performance_dashboard"
    tool_description: ClassVar[str] = "Operational monitoring that is specific to the FastMCP framework. Provides FastMCP performance dashboard with real-time alerting and enhanced monitoring"
    business_category: ClassVar[str] = "System & Monitoring Tools"
    tool_type: ClassVar[ToolType] = ToolType.ANALYTICS
    tool_version: ClassVar[str] = "1.0.0"
    
    
    def _get_dashboard_data(self) -> Dict[str, Any]:
        """Get FastMCP dashboard data from performance module.
        
        Returns:
            Dictionary containing dashboard data and metrics
        """
        from revenium_mcp_server.fastmcp_performance import get_fastmcp_dashboard
        return get_fastmcp_dashboard()

    def _format_no_data_response(self, dashboard_data: Dict[str, Any]) -> str:
        """Format response when no performance data is available.
        
        Args:
            dashboard_data: Dashboard data containing status and message
            
        Returns:
            Formatted no data response string
        """
        return FastMCPPerformanceFormatters.format_no_data_response(dashboard_data)

    def _extract_dashboard_components(self, dashboard_data: Dict[str, Any]) -> tuple:
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

    def _build_complete_dashboard(self, dashboard_data: Dict[str, Any]) -> str:
        """Build complete dashboard from data components.
        
        Args:
            dashboard_data: Complete dashboard data
            
        Returns:
            Formatted complete dashboard string
        """
        return FastMCPPerformanceFormatters.build_complete_dashboard(dashboard_data)

    async def handle_action(
        self, 
        action: str,
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle FastMCP performance dashboard tool actions.
        
        Args:
            action: Action to perform (supported: performance_dashboard, get_examples, get_capabilities)
            arguments: Additional arguments (unused for dashboard generation)
            
        Returns:
            Dashboard content as TextContent list
        """
        # Validate action
        supported_actions = await self._get_supported_actions()
        if action not in supported_actions:
            error_text = f"""
❌ **Invalid Action: {action}**

**Supported Actions for Performance Dashboard:**
- `performance_dashboard`: Generate FastMCP performance monitoring dashboard
- `get_examples`: Get tool-specific usage examples  
- `get_capabilities`: Get tool capabilities and supported actions

**Example Usage:**
```json
{{"action": "performance_dashboard"}}
```

Please use one of the supported actions above.
"""
            return [TextContent(type="text", text=error_text)]
        
        # Handle specific actions
        if action == "get_examples":
            examples = await self._get_examples()
            examples_text = self._format_examples_response(examples)
            return [TextContent(type="text", text=examples_text)]
        
        elif action == "get_capabilities":
            capabilities = await self._get_tool_capabilities()
            capabilities_text = self._format_capabilities_response(capabilities)
            return [TextContent(type="text", text=capabilities_text)]
        
        elif action in ["performance_dashboard", "get_dashboard"]:
            # Generate performance dashboard (support both action names for consistency)
            try:
                dashboard_data = self._get_dashboard_data()
                
                if dashboard_data["status"] == "no_data":
                    dashboard_text = self._format_no_data_response(dashboard_data)
                else:
                    dashboard_text = self._build_complete_dashboard(dashboard_data)
                
                return [TextContent(type="text", text=dashboard_text)]
                
            except Exception as e:
                return FastMCPPerformanceErrors.handle_dashboard_error(e)
        
        else:
            # Should not reach here due to validation above, but safety fallback
            return [TextContent(type="text", text=f"❌ Unsupported action: {action}")]
    
    async def _get_supported_actions(self) -> List[str]:
        """Get list of supported actions for this tool.
        
        Returns:
            List of supported action names
        """
        return ["get_dashboard", "performance_dashboard", "get_examples", "get_capabilities"]
    
    async def _get_examples(self) -> List[Dict[str, Any]]:
        """Get tool-specific examples for FastMCP Performance Dashboard.
        
        Returns:
            List of example usage patterns specific to performance dashboard
        """
        return [
            {
                "title": "Generate Performance Dashboard",
                "description": "Get comprehensive FastMCP performance monitoring dashboard with real-time metrics",
                "action": "performance_dashboard",
                "parameters": {},
                "example_request": {
                    "action": "performance_dashboard"
                },
                "use_case": "Monitor FastMCP tool performance, latency, and success rates in real-time"
            },
            {
                "title": "Performance Dashboard with Alerting", 
                "description": "Generate dashboard including performance alerts and threshold violations",
                "action": "performance_dashboard",
                "parameters": {},
                "example_request": {
                    "action": "performance_dashboard"
                },
                "use_case": "Monitor system health and get alerted to performance issues or SLA violations"
            },
            {
                "title": "Tool-Specific Performance Analysis",
                "description": "View performance breakdown by individual MCP tools and actions", 
                "action": "performance_dashboard",
                "parameters": {},
                "example_request": {
                    "action": "performance_dashboard"
                },
                "use_case": "Identify slow or failing tools for optimization and troubleshooting"
            },
            {
                "title": "Enterprise Performance Compliance",
                "description": "Monitor compliance with enterprise performance targets and SLAs",
                "action": "performance_dashboard", 
                "parameters": {},
                "example_request": {
                    "action": "performance_dashboard"
                },
                "use_case": "Ensure FastMCP meets enterprise performance standards and compliance requirements"
            }
        ]
    
    def _format_examples_response(self, examples: List[Dict[str, Any]]) -> str:
        """Format examples into readable response text.
        
        Args:
            examples: List of example dictionaries
            
        Returns:
            Formatted examples text
        """
        if not examples:
            return "No examples available for this tool."
        
        text = "# **FastMCP Performance Dashboard - Usage Examples**\n\n"
        
        for i, example in enumerate(examples, 1):
            text += f"## **{i}. {example['title']}**\n\n"
            text += f"**Description**: {example['description']}\n\n"
            text += f"**Use Case**: {example['use_case']}\n\n"
            text += "**Request Example:**\n"
            text += "```json\n"
            text += str(example['example_request']).replace("'", '"')
            text += "\n```\n\n"
            text += "---\n\n"
        
        return text
    
    def _format_capabilities_response(self, capabilities: List[Any]) -> str:
        """Format capabilities into readable response text.
        
        Args:
            capabilities: List of tool capabilities
            
        Returns:
            Formatted capabilities text
        """
        return f"""
# **FastMCP Performance Dashboard - Tool Capabilities**

## **Tool Information**
- **Name**: {self.tool_name}
- **Description**: {self.tool_description}
- **Type**: {self.tool_type.value}
- **Version**: {self.tool_version}

## **Supported Actions**
- `performance_dashboard`: Generate comprehensive performance monitoring dashboard
- `get_examples`: Get tool-specific usage examples
- `get_capabilities`: Get detailed tool capabilities

## **Key Features**
- Real-time FastMCP performance monitoring
- Tool-specific latency and success rate tracking  
- Performance alert detection and reporting
- Enterprise compliance monitoring
- Historical performance trend analysis
- Automated performance threshold checking

## **Performance Metrics Tracked**
- Tool execution latency (avg, 50th, 95th, 99th percentiles)
- Success/failure rates by tool and action
- Throughput metrics (operations per second)
- Cache hit rates and efficiency
- Resource utilization patterns
- Alert triggering and resolution

## **Enterprise Compliance**
- SLA monitoring and reporting
- Performance threshold validation
- Automated alerting on violations
- Historical compliance tracking
"""