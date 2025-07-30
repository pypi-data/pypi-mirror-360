"""Integration module for tool introspection with the MCP server.

This module provides integration utilities to register tools with the introspection
engine and add introspection capabilities to the MCP server.
"""

import asyncio
from typing import Dict, Any, List, Union, Optional, cast
from loguru import logger

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .engine import introspection_engine
from .service import tool_introspection_service
from ..tools_decomposed.unified_tool_base import ToolBase
from ..common.error_handling import ToolError


class IntrospectionIntegration:
    """Integration manager for tool introspection capabilities."""
    
    def __init__(self, ucm_integration_service=None):
        """Initialize the integration manager.

        Args:
            ucm_integration_service: UCM integration service for enhanced tools
        """
        self.engine = introspection_engine
        self.service = tool_introspection_service
        self.ucm_integration_service = ucm_integration_service
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the introspection integration."""
        if self._initialized:
            return
        
        logger.info("Initializing tool introspection integration")
        
        # Register enhanced tools with introspection engine
        await self._register_enhanced_tools()
        
        self._initialized = True
        logger.info("Tool introspection integration initialized successfully")
    
    def _get_ucm_helper(self, tool_name: str) -> Optional[Any]:
        """Get UCM helper with consistent logging and error handling.

        Args:
            tool_name: Name of the tool for logging purposes

        Returns:
            UCM helper instance or None
        """
        if self.ucm_integration_service:
            logger.info(f"{tool_name}: UCM integration service available, creating enhanced instance")
            return self.ucm_integration_service.get_integration_helper()
        else:
            logger.warning(f"{tool_name}: UCM integration service not available, using static capabilities")
            return None

    async def _register_tool_with_ucm(self, tool_class, tool_name: str, registry_name: str) -> None:
        """Register a tool with standardized UCM integration.

        Args:
            tool_class: Tool class to instantiate
            tool_name: Human-readable tool name for logging
            registry_name: Registry name for the tool
        """
        ucm_helper = self._get_ucm_helper(tool_name)
        tool_instance = tool_class(ucm_helper=ucm_helper)
        await self.engine.register_tool(registry_name, tool_instance)
        logger.info(f"Registered {tool_name.lower()} for introspection {'with UCM integration' if ucm_helper else 'without UCM integration'}")

    async def _register_enhanced_tools(self) -> None:
        """Register enhanced tools with the introspection engine using standardized UCM injection."""
        try:
            # Register onboarding tools FIRST to ensure they appear at the top of the list
            try:
                # Register system_setup (the actual MCP tool name)
                from ..tools_decomposed.system_setup import SystemSetup
                await self._register_tool_with_ucm(SystemSetup, "System Setup", "system_setup")
                logger.info("Registered system_setup for introspection")
            except Exception as e:
                logger.error(f"❌ Could not register system_setup for introspection: {e}")
                # Continue without this tool rather than failing server startup

            try:
                # Register system_diagnostics (the actual MCP tool name)
                from ..tools_decomposed.system_diagnostics import SystemDiagnostics
                await self._register_tool_with_ucm(SystemDiagnostics, "System Diagnostics", "system_diagnostics")
                logger.info("Registered system_diagnostics for introspection")
            except Exception as e:
                logger.warning(f"Could not register system_diagnostics for introspection: {e}")
                # Continue without this tool rather than failing server startup

            # Note: verify_email_setup, setup_checklist, and configuration_status are not standalone MCP tools
            # They are integrated into system_setup and system_diagnostics consolidated tools

            # Register all other tools with standardized UCM integration pattern
            from ..tools_decomposed.alert_management import AlertManagement
            await self._register_tool_with_ucm(AlertManagement, "Alert Management", "manage_alerts")

            from ..tools_decomposed.product_management import ProductManagement
            await self._register_tool_with_ucm(ProductManagement, "Product Management", "manage_products")

            from ..tools_decomposed.subscription_management import SubscriptionManagement
            await self._register_tool_with_ucm(SubscriptionManagement, "Subscription Management", "manage_subscriptions")

            from ..tools_decomposed.workflow_management import WorkflowManagement
            await self._register_tool_with_ucm(WorkflowManagement, "Workflow Management", "manage_workflows")

            from ..tools_decomposed.metering_elements_management import MeteringElementsManagement
            await self._register_tool_with_ucm(MeteringElementsManagement, "Metering Elements Management", "manage_metering_elements")

            from ..tools_decomposed.metering_management import MeteringManagement
            await self._register_tool_with_ucm(MeteringManagement, "Metering Management", "manage_metering")

            from ..tools_decomposed.metering_field_validation import MeteringFieldValidationManagement
            await self._register_tool_with_ucm(MeteringFieldValidationManagement, "Metering Field Validation", "manage_metering_field_validation")

            from ..tools_decomposed.source_management import SourceManagement
            await self._register_tool_with_ucm(SourceManagement, "Source Management", "manage_sources")

            from ..tools_decomposed.business_analytics_management import BusinessAnalyticsManagement
            await self._register_tool_with_ucm(BusinessAnalyticsManagement, "Business Analytics Management", "business_analytics_management")

            from ..tools_decomposed.subscriber_credentials_management import SubscriberCredentialsManagement
            await self._register_tool_with_ucm(SubscriberCredentialsManagement, "Subscriber Credentials Management", "manage_subscriber_credentials")

            # Register Slack tools
            try:
                from ..tools_decomposed.slack_configuration_management import SlackConfigurationManagement
                await self._register_tool_with_ucm(SlackConfigurationManagement, "Slack Configuration Management", "slack_configuration_management")
                logger.info("Registered slack_configuration_management for introspection")
            except Exception as e:
                logger.warning(f"Could not register slack_configuration_management for introspection: {e}")

            try:
                from ..tools_decomposed.slack_oauth_workflow import SlackOAuthWorkflow
                await self._register_tool_with_ucm(SlackOAuthWorkflow, "Slack OAuth Workflow", "slack_oauth_workflow")
                logger.info("Registered slack_oauth_workflow for introspection")
            except Exception as e:
                logger.warning(f"Could not register slack_oauth_workflow for introspection: {e}")

            try:
                from ..tools_decomposed.slack_setup_assistant import SlackSetupAssistant
                await self._register_tool_with_ucm(SlackSetupAssistant, "Slack Setup Assistant", "slack_setup_assistant")
                logger.info("Registered slack_setup_assistant for introspection")
            except Exception as e:
                logger.warning(f"Could not register slack_setup_assistant for introspection: {e}")

            # Register customer management with UCM integration
            try:
                from ..tools_decomposed.customer_management import CustomerManagement
                await self._register_tool_with_ucm(CustomerManagement, "Customer Management", "manage_customers")
                logger.info("Registered customer management for introspection")
            except Exception as e:
                logger.warning(f"Could not register customer management for introspection: {e}")

            # Register Group 5 tools for introspection
            # Note: performance_dashboard removed - infrastructure monitoring handled externally



            # Register tool_introspection with introspection engine
            try:
                from ..tools_decomposed.tool_introspection import ToolIntrospection
                await self._register_tool_with_ucm(ToolIntrospection, "Tool Introspection", "tool_introspection")
                logger.info("Registered tool_introspection for introspection")
            except Exception as e:
                logger.warning(f"Could not register tool_introspection for introspection: {e}")

            # REMOVED: simple_chart_test - caused mcptools deadlock, chart features not used in production

        except Exception as e:
            logger.error(f"Error registering enhanced tools: {e}")
            raise
    
    async def handle_tool_execution(
        self,
        tool_name: str,
        action: str,
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle tool execution with optimized performance tracking.

        Args:
            tool_name: Name of the tool
            action: Action to perform
            arguments: Action arguments

        Returns:
            Tool response
        """
        import time
        start_time = time.time()
        success = False

        try:
            # OPTIMIZATION: Cache provider lookup to avoid repeated registry access
            provider = await self.engine.registry.get_provider(tool_name)

            # Check if this is an introspection action (optimized check)
            if action == "get_tool_metadata" and provider:
                metadata = await self.engine.get_tool_metadata(tool_name)
                if metadata:
                    success = True
                    return [TextContent(
                        type="text",
                        text=f"🔍 **Tool Metadata: {metadata.name}**\n\n{metadata.agent_summary}"
                    )]

            # Handle regular tool execution (optimized path)
            # Cast provider to ToolBase since all registered providers are ToolBase instances
            if provider and hasattr(provider, 'handle_action'):
                tool_provider = cast(ToolBase, provider)
                result = await tool_provider.handle_action(action, arguments)
                success = True
                return result

            # Fallback to regular tool handling - use proper exception
            from ..common.error_handling import ToolNotFoundError
            raise ToolNotFoundError(
                f"Tool '{tool_name}' not found in introspection registry",
                tool_name=tool_name,
                action=action
            )

        except ToolError:
            # Re-raise ToolError exceptions without modification
            # This preserves helpful error messages with specific suggestions
            raise
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}.{action}: {e}")
            from ..common.error_handling import ToolExecutionError, format_error_response

            # Only wrap non-ToolError exceptions
            execution_error = ToolExecutionError(
                f"Tool execution failed",
                tool_name=tool_name,
                action=action
            )
            return format_error_response(execution_error, f"executing {tool_name}.{action}")
        finally:
            # OPTIMIZATION: Async performance tracking to avoid blocking
            execution_time_ms = (time.time() - start_time) * 1000
            # Fire-and-forget performance update to avoid blocking tool execution
            asyncio.create_task(
                self.engine.update_tool_performance(tool_name, execution_time_ms, success)
            )
    
    async def add_introspection_tool_to_server(self, server_instance) -> None:
        """Add introspection tool to the MCP server using dynamic description system.
        
        Args:
            server_instance: FastMCP server instance
        """
        # Import dynamic description system
        from ..tools_decomposed.tool_registry import get_tool_description
        
        # Get dynamic description from single source of truth BEFORE creating function
        dynamic_description = get_tool_description("tool_introspection")
        
        # Create function with dynamic docstring set BEFORE decoration
        async def tool_introspection(
            action: str = "get_capabilities",  # Context7: Smart default for zero-knowledge agents
            tool_name: Optional[str] = None,
            tool_type: Optional[str] = None
        ) -> str:
            arguments = {
                "action": action,
                "tool_name": tool_name,
                "tool_type": tool_type
            }
            
            # Use the tool class following single source of truth architecture
            from ..tools_decomposed.tool_introspection import ToolIntrospection
            tool_instance = ToolIntrospection()
            result = await tool_instance.handle_action(action, arguments)
            if result and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, TextContent):
                    return first_result.text
            return "No result"
        
        # Set dynamic description BEFORE applying decorator
        tool_introspection.__doc__ = dynamic_description
        
        # Now apply the decorator to the function with correct docstring and name
        server_instance.tool()(tool_introspection)
        
        logger.info(f"Added tool_introspection tool to MCP server with dynamic description: {dynamic_description}")
    
    async def get_server_summary(self) -> Dict[str, Any]:
        """Get a summary of the server's introspection capabilities.
        
        Returns:
            Summary dictionary
        """
        tools = await self.engine.list_tools()

        return {
            "introspection_enabled": True,
            "registered_tools": len(tools),
            "total_executions": 0,
            "average_success_rate": 100.0,
            "dependency_relationships": 0,
            "available_actions": [
                "list_tools", "get_tool_metadata", "get_all_metadata"
            ]
        }
    
    async def validate_tool_health(self) -> Dict[str, Any]:
        """Validate the health of registered tools.
        
        Returns:
            Health validation results
        """
        tools = await self.engine.list_tools()
        health_results = {
            "healthy_tools": [],
            "unhealthy_tools": [],
            "missing_metadata": [],
            "circular_dependencies": []
        }
        
        # Check tool metadata availability
        for tool_name in tools:
            metadata = await self.engine.get_tool_metadata(tool_name)
            if metadata:
                # Check if tool has reasonable performance metrics
                if metadata.performance_metrics.success_rate >= 0.8:
                    health_results["healthy_tools"].append(tool_name)
                else:
                    health_results["unhealthy_tools"].append({
                        "tool": tool_name,
                        "success_rate": metadata.performance_metrics.success_rate,
                        "error_count": metadata.performance_metrics.error_count
                    })
            else:
                health_results["missing_metadata"].append(tool_name)
        
        # Circular dependency checking removed (internal debugging utility)
        health_results["circular_dependencies"] = []
        
        return health_results
    
    async def generate_tool_documentation(self) -> str:
        """Generate comprehensive documentation for all tools.
        
        Returns:
            Formatted documentation string
        """
        all_metadata = await self.engine.get_all_metadata()
        
        doc = "# MCP Server Tool Documentation\n\n"
        doc += f"Generated on: {asyncio.get_event_loop().time()}\n"
        doc += f"Total tools: {len(all_metadata)}\n\n"
        
        for tool_name, metadata in sorted(all_metadata.items()):
            doc += f"## {metadata.name}\n\n"
            doc += f"**Description**: {metadata.description}\n"
            doc += f"**Version**: {metadata.version}\n"
            doc += f"**Type**: {metadata.tool_type.value}\n\n"
            
            if metadata.agent_summary:
                doc += f"**Summary**: {metadata.agent_summary}\n\n"
            
            if metadata.capabilities:
                doc += "**Capabilities**:\n"
                for cap in metadata.capabilities:
                    doc += f"- **{cap.name}**: {cap.description}\n"
                doc += "\n"
            
            if metadata.supported_actions:
                doc += f"**Actions**: {', '.join(metadata.supported_actions)}\n\n"
            
            if metadata.quick_start_guide:
                doc += "**Quick Start**:\n"
                for i, step in enumerate(metadata.quick_start_guide, 1):
                    doc += f"{i}. {step}\n"
                doc += "\n"
            
            doc += "---\n\n"
        
        return doc


# Global integration instance
introspection_integration = IntrospectionIntegration()
