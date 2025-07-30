"""Tool Configuration Registry

Implements dynamic tool registration based on configuration profiles
following the ConditionalToolRegistry pattern from the architecture guide.

This registry conditionally registers tools based on the ToolConfig settings,
enabling profile-based tool loading (starter/business).
"""

from typing import Dict, Any, Optional, Callable, List, Union
from loguru import logger
from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

from .config import ToolConfig
from ..tools_decomposed.dynamic_decorators import dynamic_mcp_tool


# Tool registration priority order following logical user journey hierarchy
# This ensures tools are presented to AI agents in the optimal sequence:
# 1. Setup & Onboarding (first-time user experience)
# 2. Discovery & Capabilities (tool exploration)
# 3. Monitoring & Analytics (operational insights)
# 4. Usage-Based Billing Workflow (logical business sequence)
# 5. System Diagnostics (troubleshooting - last)
TOOL_REGISTRATION_PRIORITY_ORDER = [
    # Group 1: Setup & Onboarding (First-time user experience)
    "system_setup",                    # Initial setup and configuration
    "slack_management",                # Communication setup

    # Group 2: Discovery & Capabilities (Tool exploration)
    "tool_introspection",              # Tool discovery and metadata
    "manage_capabilities",             # System capabilities overview

    # Group 3: Monitoring & Analytics (Operational insights)
    "manage_alerts",                   # Cost monitoring and alerting
    "business_analytics_management",   # Analytics and reporting
    "manage_metering",                 # Transaction processing and metering

    # Group 4: Usage-Based Billing Workflow (Logical business sequence)
    "manage_customers",                # Customer management (start of UBB workflow)
    "manage_products",                 # Product definition
    "manage_sources",                  # Data sources configuration
    "manage_metering_elements",        # Metering configuration
    "manage_subscriptions",            # Subscription management
    "manage_subscriber_credentials",   # Billing identity management
    "manage_workflows",                # Automation and workflows

    # Group 5: System Diagnostics (Troubleshooting - last)
    "system_diagnostics"               # System health and troubleshooting
]


class ToolConfigurationRegistry:
    """Registry for configuration-based tool registration.
    
    Follows the ConditionalToolRegistry pattern from the MCP Tool Architecture Guide.
    Provides dynamic tool registration without code duplication by using the
    established @mcp.tool() + @dynamic_mcp_tool + standardized_tool_execution pattern.
    """
    
    def __init__(self, tool_config: Optional[ToolConfig] = None):
        """Initialize tool configuration registry.
        
        Args:
            tool_config: Tool configuration instance. If None, creates default config.
        """
        self.tool_config = tool_config or ToolConfig()
        self.tool_instances: Dict[str, Any] = {}
        self._registered_tools: set = set()
        
        # Initialize tool instances for all possible tools
        self._initialize_tool_instances()
    
    def _initialize_tool_instances(self) -> None:
        """Initialize all tool instances for lazy loading."""
        # This will be populated as we implement consolidated tools
        # For now, we'll prepare the structure for existing tools
        self.tool_instances = {}
        
        logger.debug(f"Tool configuration registry initialized for profile: {self.tool_config.profile}")
    
    async def register_tools_conditionally(self, mcp: FastMCP) -> None:
        """Register tools based on configuration profile in priority order.

        Tools are registered following the logical user journey hierarchy defined in
        TOOL_REGISTRATION_PRIORITY_ORDER, ensuring optimal presentation to AI agents.

        Args:
            mcp: FastMCP server instance for tool registration
        """
        enabled_tools = self.tool_config.get_enabled_tools()
        logger.info(f"Registering {len(enabled_tools)} tools for profile '{self.tool_config.profile}' in priority order")

        # Register tools in priority order, but only if they're enabled for the current profile
        registered_count = 0
        for tool_name in TOOL_REGISTRATION_PRIORITY_ORDER:
            if self.tool_config.is_tool_enabled(tool_name):
                await self._register_single_tool(mcp, tool_name)
                registered_count += 1

        # Log any enabled tools that weren't in the priority order (for debugging)
        priority_set = set(TOOL_REGISTRATION_PRIORITY_ORDER)
        missing_tools = enabled_tools - priority_set
        if missing_tools:
            logger.warning(f"Tools enabled but not in priority order: {missing_tools}")
            # Register missing tools at the end to ensure they're not lost
            for tool_name in sorted(missing_tools):
                await self._register_single_tool(mcp, tool_name)
                registered_count += 1

        logger.info(f"Successfully registered {registered_count} tools in priority order")
    
    async def _register_single_tool(self, mcp: FastMCP, tool_name: str) -> None:
        """Register a single tool following architecture guide patterns.
        
        Args:
            mcp: FastMCP server instance
            tool_name: Name of the tool to register
        """
        try:
            # Use dedicated registration functions for each tool
            if tool_name == "business_analytics_management":
                await self._register_business_analytics_management(mcp)
            elif tool_name == "manage_alerts":
                await self._register_manage_alerts(mcp)
            elif tool_name == "slack_management":
                await self._register_slack_management(mcp)
            elif tool_name == "manage_metering":
                await self._register_manage_metering(mcp)
            elif tool_name == "system_setup":
                await self._register_system_setup(mcp)
            elif tool_name == "system_diagnostics":
                await self._register_system_diagnostics(mcp)

            elif tool_name == "manage_sources":
                await self._register_manage_sources(mcp)
            elif tool_name == "manage_workflows":
                await self._register_manage_workflows(mcp)
            elif tool_name == "manage_subscriber_credentials":
                await self._register_manage_subscriber_credentials(mcp)
            elif tool_name == "manage_products":
                await self._register_manage_products(mcp)
            elif tool_name == "manage_customers":
                await self._register_manage_customers(mcp)
            elif tool_name == "manage_subscriptions":
                await self._register_manage_subscriptions(mcp)
            elif tool_name == "manage_metering_elements":
                await self._register_manage_metering_elements(mcp)
            elif tool_name == "manage_capabilities":
                await self._register_manage_capabilities(mcp)
            elif tool_name == "tool_introspection":
                await self._register_tool_introspection(mcp)
            else:
                logger.warning(f"Unknown tool for registration: {tool_name}")
                return
            
            self._registered_tools.add(tool_name)
            logger.debug(f"Registered tool: {tool_name}")
            
        except Exception as e:
            logger.error(f"Failed to register tool {tool_name}: {e}")
    
    async def _register_business_analytics_management(self, mcp: FastMCP) -> None:
        """Register business analytics management tool."""
        @mcp.tool()
        @dynamic_mcp_tool("business_analytics_management")
        async def business_analytics_management(
            action: str = "get_capabilities",
            breakdown_by: Optional[str] = None,
            period: Optional[str] = None,
            group: Optional[str] = None,
            filters: Optional[dict] = None,
            page: int = 0,
            size: int = 20,
            threshold: Optional[float] = None,
            min_impact_threshold: Optional[float] = None,
            include_dimensions: Optional[Union[List[str], str]] = None,
            sensitivity: Optional[str] = None,
            dry_run: Optional[bool] = None,
            example_type: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            
            arguments = {
                "action": action,
                "breakdown_by": breakdown_by,
                "period": period,
                "group": group,
                "filters": filters,
                "page": page,
                "size": size,
                "threshold": threshold,
                "min_impact_threshold": min_impact_threshold,
                "include_dimensions": include_dimensions,
                "sensitivity": sensitivity,
                "dry_run": dry_run,
                "example_type": example_type
            }
            
            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}
            
            # Import tool class
            from ..tools_decomposed.business_analytics_management import BusinessAnalyticsManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="business_analytics_management",
                action=action,
                arguments=arguments,
                tool_class=BusinessAnalyticsManagement
            )
            return result
    
    async def _register_manage_alerts(self, mcp: FastMCP) -> None:
        """Register manage alerts tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_alerts")
        async def manage_alerts(
            action: str,
            alert_id: Optional[str] = None,
            name: Optional[str] = None,
            metric: Optional[str] = None,
            threshold: Optional[float] = None,
            period: Optional[str] = None,
            period_minutes: Optional[float] = None,
            email: Optional[str] = None,
            slack_config_id: Optional[str] = None,
            triggerAfterPersistsDuration: Optional[str] = None,
            filters: Optional[dict] = None,
            page: int = 0,
            size: int = 20,
            dry_run: Optional[bool] = None,
            confirm: Optional[bool] = None,
            alert_type: Optional[str] = None,
            text: Optional[str] = None,
            query: Optional[str] = None,
            resource_type: str = "anomalies",
            anomaly_id: Optional[str] = None,
            anomaly_ids: Optional[List[str]] = None,
            anomaly_data: Optional[dict] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            
            arguments = {
                "action": action,
                "alert_id": alert_id,
                "name": name,
                "metric": metric,
                "threshold": threshold,
                "period": period,
                "period_minutes": period_minutes,
                "email": email,
                "slack_config_id": slack_config_id,
                "triggerAfterPersistsDuration": triggerAfterPersistsDuration,
                "filters": filters,
                "page": page,
                "size": size,
                "dry_run": dry_run,
                "confirm": confirm,
                "alert_type": alert_type,
                "text": text,
                "query": query,
                "resource_type": resource_type,
                "anomaly_id": anomaly_id,
                "anomaly_ids": anomaly_ids,
                "anomaly_data": anomaly_data
            }
            
            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}
            
            # Import tool class
            from ..tools_decomposed.alert_management import AlertManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_alerts",
                action=action,
                arguments=arguments,
                tool_class=AlertManagement
            )
            return result
    
    async def _register_slack_management(self, mcp: FastMCP) -> None:
        """Register consolidated slack management tool."""
        @mcp.tool()
        @dynamic_mcp_tool("slack_management")
        async def slack_management(
            action: str = "get_capabilities",
            config_id: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            return_to: Optional[str] = None,
            dry_run: Optional[bool] = None,
            skip_prompts: bool = False
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:

            arguments = {
                "action": action,
                "config_id": config_id,
                "page": page,
                "size": size,
                "return_to": return_to,
                "dry_run": dry_run,
                "skip_prompts": skip_prompts
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import consolidated tool class
            from ..tools_decomposed.slack_management import SlackManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="slack_management",
                action=action,
                arguments=arguments,
                tool_class=SlackManagement
            )
            return result

    async def _register_system_setup(self, mcp: FastMCP) -> None:
        """Register consolidated system setup tool."""
        @mcp.tool()
        @dynamic_mcp_tool("system_setup")
        async def system_setup(
            action: str = "show_welcome",
            show_environment: Optional[bool] = None,
            include_recommendations: Optional[bool] = None,
            confirm_completion: Optional[bool] = None,
            email: Optional[str] = None,
            validate_format: Optional[bool] = None,
            suggest_smart_defaults: Optional[bool] = None,
            include_setup_guidance: Optional[bool] = None,
            test_configuration: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:

            arguments = {
                "action": action,
                "show_environment": show_environment,
                "include_recommendations": include_recommendations,
                "confirm_completion": confirm_completion,
                "email": email,
                "validate_format": validate_format,
                "suggest_smart_defaults": suggest_smart_defaults,
                "include_setup_guidance": include_setup_guidance,
                "test_configuration": test_configuration
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import consolidated tool class
            from ..tools_decomposed.system_setup import SystemSetup
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="system_setup",
                action=action,
                arguments=arguments,
                tool_class=SystemSetup
            )
            return result

    async def _register_system_diagnostics(self, mcp: FastMCP) -> None:
        """Register consolidated system diagnostics tool."""
        @mcp.tool()
        @dynamic_mcp_tool("system_diagnostics")
        async def system_diagnostics(
            action: str = "system_health",
            format_output: Optional[str] = None,
            include_recommendations: Optional[bool] = None,
            include_sensitive: Optional[bool] = None,
            show_detailed_analysis: Optional[bool] = None,
            log_type: Optional[str] = None,
            operation_filter: Optional[str] = None,
            page: int = 0,
            size: int = 200,
            pages: Optional[int] = None,
            search_all_pages: Optional[bool] = None,
            search_term: Optional[str] = None,
            status_filter: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:

            arguments = {
                "action": action,
                "format_output": format_output,
                "include_recommendations": include_recommendations,
                "include_sensitive": include_sensitive,
                "show_detailed_analysis": show_detailed_analysis,
                "log_type": log_type,
                "operation_filter": operation_filter,
                "page": page,
                "size": size,
                "pages": pages,
                "search_all_pages": search_all_pages,
                "search_term": search_term,
                "status_filter": status_filter
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import consolidated tool class
            from ..tools_decomposed.system_diagnostics import SystemDiagnostics
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="system_diagnostics",
                action=action,
                arguments=arguments,
                tool_class=SystemDiagnostics
            )
            return result



    async def _register_manage_metering(self, mcp: FastMCP) -> None:
        """Register manage metering tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_metering")
        async def manage_metering(
            action: str = "get_capabilities",
            model: Optional[str] = None,
            provider: Optional[str] = None,
            input_tokens: Optional[int] = None,
            output_tokens: Optional[int] = None,
            duration_ms: Optional[int] = None,
            organization_id: Optional[str] = None,
            subscription_id: Optional[str] = None,
            product_id: Optional[str] = None,
            page: Optional[int] = None,
            size: Optional[int] = None,
            query: Optional[str] = None,
            dry_run: Optional[bool] = None,
            example_type: Optional[str] = None,
            language: Optional[str] = None,
            use_case: Optional[str] = None,
            text: Optional[str] = None,
            description: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "model": model,
                "provider": provider,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "duration_ms": duration_ms,
                "organization_id": organization_id,
                "subscription_id": subscription_id,
                "product_id": product_id,
                "page": page,
                "size": size,
                "query": query,
                "dry_run": dry_run,
                "example_type": example_type,
                "language": language,
                "use_case": use_case,
                "text": text,
                "description": description
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.metering_management import MeteringManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_metering",
                action=action,
                arguments=arguments,
                tool_class=MeteringManagement
            )
            return result
    
    # Placeholder methods for business profile tools
    async def _register_manage_sources(self, mcp: FastMCP) -> None:
        """Register manage sources tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_sources")
        async def manage_sources(
            action: str = "get_capabilities",
            source_id: Optional[str] = None,
            source_data: Optional[Union[dict, str]] = None,
            page: int = 0,
            size: int = 20,
            filters: Optional[dict] = None,
            auto_generate: bool = True,
            dry_run: Optional[bool] = None,
            example_type: Optional[str] = None,
            text: Optional[str] = None,
            name: Optional[str] = None,
            type: Optional[str] = None,
            url: Optional[str] = None,
            stream_url: Optional[str] = None,
            model_endpoint: Optional[str] = None,
            connection_string: Optional[str] = None,
            description: Optional[str] = None,
            version: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "source_id": source_id,
                "source_data": source_data,
                "page": page,
                "size": size,
                "filters": filters or {},
                "auto_generate": auto_generate,
                "dry_run": dry_run,
                "example_type": example_type,
                "text": text,
                "name": name,
                "type": type,
                "url": url,
                "stream_url": stream_url,
                "model_endpoint": model_endpoint,
                "connection_string": connection_string,
                "description": description,
                "version": version
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.source_management import SourceManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_sources",
                action=action,
                arguments=arguments,
                tool_class=SourceManagement
            )
            return result
    
    async def _register_manage_workflows(self, mcp: FastMCP) -> None:
        """Register manage workflows tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_workflows")
        async def manage_workflows(
            action: str = "get_capabilities",
            workflow_id: Optional[str] = None,
            workflow_data: Optional[dict] = None,
            workflow_type: Optional[str] = None,
            context: Optional[dict] = None,
            dry_run: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "workflow_id": workflow_id,
                "workflow_data": workflow_data,
                "workflow_type": workflow_type,
                "context": context,
                "dry_run": dry_run
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.workflow_management import WorkflowManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_workflows",
                action=action,
                arguments=arguments,
                tool_class=WorkflowManagement
            )
            return result

    async def _register_manage_subscriber_credentials(self, mcp: FastMCP) -> None:
        """Register manage subscriber credentials tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_subscriber_credentials")
        async def manage_subscriber_credentials(
            action: str = "get_capabilities",
            credential_id: Optional[str] = None,
            credential_data: Optional[dict] = None,
            subscriberId: Optional[str] = None,
            organizationId: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            dry_run: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "credential_id": credential_id,
                "credential_data": credential_data,
                "subscriberId": subscriberId,
                "organizationId": organizationId,
                "page": page,
                "size": size,
                "dry_run": dry_run
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.subscriber_credentials_management import SubscriberCredentialsManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_subscriber_credentials",
                action=action,
                arguments=arguments,
                tool_class=SubscriberCredentialsManagement
            )
            return result

    async def _register_manage_products(self, mcp: FastMCP) -> None:
        """Register manage products tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_products")
        async def manage_products(
            action: str = "get_capabilities",
            product_id: Optional[str] = None,
            resource_data: Optional[Union[dict, str]] = None,
            product_data: Optional[Union[dict, str]] = None,
            page: int = 0,
            size: int = 20,
            filters: Optional[dict] = None,
            auto_generate: bool = True,
            dry_run: Optional[bool] = None,
            example_type: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "product_id": product_id,
                "resource_data": resource_data,
                "product_data": product_data,
                "page": page,
                "size": size,
                "filters": filters or {},
                "auto_generate": auto_generate,
                "dry_run": dry_run,
                "example_type": example_type
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.product_management import ProductManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_products",
                action=action,
                arguments=arguments,
                tool_class=ProductManagement
            )
            return result
    
    async def _register_manage_customers(self, mcp: FastMCP) -> None:
        """Register manage customers tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_customers")
        async def manage_customers(
            action: str = "get_capabilities",
            resource_type: Optional[str] = None,
            resource_id: Optional[str] = None,
            resource_data: Optional[Union[dict, str]] = None,
            email: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            filters: Optional[dict] = None,
            auto_generate: bool = True,
            dry_run: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_data": resource_data,
                "email": email,
                "page": page,
                "size": size,
                "filters": filters or {},
                "auto_generate": auto_generate,
                "dry_run": dry_run
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.customer_management import CustomerManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_customers",
                action=action,
                arguments=arguments,
                tool_class=CustomerManagement
            )
            return result

    async def _register_manage_subscriptions(self, mcp: FastMCP) -> None:
        """Register manage subscriptions tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_subscriptions")
        async def manage_subscriptions(
            action: str = "get_capabilities",
            subscription_id: Optional[str] = None,
            subscription_data: Optional[Union[dict, str]] = None,
            product_id: Optional[str] = None,
            customer_name: Optional[str] = None,
            subscriber_email: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            filters: Optional[dict] = None,
            auto_generate: bool = True,
            dry_run: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "subscription_id": subscription_id,
                "subscription_data": subscription_data,
                "product_id": product_id,
                "customer_name": customer_name,
                "subscriber_email": subscriber_email,
                "page": page,
                "size": size,
                "filters": filters or {},
                "auto_generate": auto_generate,
                "dry_run": dry_run
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.subscription_management import SubscriptionManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_subscriptions",
                action=action,
                arguments=arguments,
                tool_class=SubscriptionManagement
            )
            return result

    async def _register_manage_metering_elements(self, mcp: FastMCP) -> None:
        """Register manage metering elements tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_metering_elements")
        async def manage_metering_elements(
            action: str = "get_capabilities",
            element_id: Optional[str] = None,
            element_data: Optional[dict] = None,
            name: Optional[str] = None,
            page: int = 0,
            size: int = 20,
            filters: Optional[dict] = None,
            dry_run: Optional[bool] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "element_id": element_id,
                "element_data": element_data,
                "name": name,
                "page": page,
                "size": size,
                "filters": filters or {},
                "dry_run": dry_run
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.metering_elements_management import MeteringElementsManagement
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_metering_elements",
                action=action,
                arguments=arguments,
                tool_class=MeteringElementsManagement
            )
            return result

    async def _register_manage_capabilities(self, mcp: FastMCP) -> None:
        """Register manage capabilities tool."""
        @mcp.tool()
        @dynamic_mcp_tool("manage_capabilities")
        async def manage_capabilities(
            action: str = "get_capabilities",
            capability_name: Optional[str] = None,
            resource_type: Optional[str] = None,
            value: Optional[str] = None
        ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            # Map arguments
            arguments = {
                "action": action,
                "capability_name": capability_name,
                "resource_type": resource_type,
                "value": value
            }

            # Remove None values
            arguments = {k: v for k, v in arguments.items() if v is not None}

            # Import tool class
            from ..tools_decomposed.manage_capabilities import ManageCapabilities
            from ..common.tool_execution import standardized_tool_execution

            # Use standardized execution path
            result = await standardized_tool_execution(
                tool_name="manage_capabilities",
                action=action,
                arguments=arguments,
                tool_class=ManageCapabilities
            )
            return result
    
    def get_registered_tools(self) -> set:
        """Get set of registered tool names.
        
        Returns:
            Set of registered tool names
        """
        return self._registered_tools.copy()
    
    def is_tool_registered(self, tool_name: str) -> bool:
        """Check if a tool is registered.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            bool: True if tool is registered
        """
        return tool_name in self._registered_tools

    async def _register_tool_introspection(self, mcp: FastMCP) -> None:
        """Register tool introspection tool."""
        # Import the introspection integration to register the tool
        from ..introspection.integration import introspection_integration
        await introspection_integration.add_introspection_tool_to_server(mcp)
        logger.debug("Registered tool_introspection via introspection integration")
