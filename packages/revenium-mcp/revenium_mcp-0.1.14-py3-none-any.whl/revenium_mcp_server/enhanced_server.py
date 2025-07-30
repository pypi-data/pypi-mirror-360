"""Enhanced MCP server with tool introspection capabilities.

This module contains the enhanced FastMCP server implementation that provides
comprehensive tool introspection and metadata capabilities alongside the
standard Revenium platform API functionality.

Copyright (c) 2024 Revenium
Licensed under the MIT License. See LICENSE file for details.
"""

import os
import asyncio
from typing import List, Union, AsyncGenerator
from contextlib import asynccontextmanager

# Core MCP dependencies
from fastmcp import FastMCP
from loguru import logger
from dotenv import load_dotenv

# Import enhanced introspection
from .introspection.integration import introspection_integration

# Import UCM integration
from .capability_manager.integration_service import ucm_integration_service

# Import MCP types for type checking
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Import dynamic tool description system
from .tools_decomposed.tool_registry import get_tool_description

# Import version information
from .version import get_package_version


def dynamic_mcp_tool(tool_name: str):
    """Decorator factory that creates @mcp.tool with dynamic description.
    
    This decorator factory creates an @mcp.tool decorator that automatically
    retrieves the tool description from the tool class registry, ensuring
    consistency across the codebase.
    
    Args:
        tool_name: Name of the tool to get description for
        
    Returns:
        Decorator function that applies @mcp.tool with dynamic description
    """
    def decorator(func):
        """Apply @mcp.tool with dynamic description to function."""
        try:
            # Get description from tool class registry
            description = get_tool_description(tool_name)
            
            # Set function docstring for MCP protocol compliance
            func.__doc__ = description
            
            logger.debug(f"Dynamic description set for {tool_name}: {description}")
            
        except Exception as e:
            # Graceful fallback - don't break tool registration
            fallback_description = f"Tool: {tool_name} (description unavailable)"
            func.__doc__ = fallback_description
            
            logger.warning(f"Could not get dynamic description for {tool_name}: {e}")
            logger.warning(f"Using fallback description: {fallback_description}")
        
        # Return function with @mcp.tool applied (will be done by mcp instance)
        return func
    
    return decorator


def safe_extract_text(result: List[Union[TextContent, ImageContent, EmbeddedResource]]) -> str:
    """Safely extract text from MCP content objects."""
    if not result:
        return "No result"

    first_item = result[0]
    if isinstance(first_item, TextContent):
        return first_item.text
    else:
        return "No result"


# REMOVED: Unused functions to fix linting errors


@asynccontextmanager
async def lifespan_manager() -> AsyncGenerator[None, None]:
    """Manage server lifespan with proper initialization and cleanup."""
    # Initialize introspection integration
    await introspection_integration.initialize()
    logger.info("Enhanced MCP server initialized with introspection capabilities")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down enhanced MCP server")


def create_enhanced_server() -> FastMCP:
    """Create and configure the enhanced MCP server.

    Returns:
        Configured FastMCP server instance
    """
    # Load environment variables from .env file ONLY if not already set
    # This ensures Augment/MCP client environment variables take precedence
    load_dotenv(override=False)

    # Configure logging - CRITICAL: Use stderr to comply with MCP stdio transport
    # MCP protocol requires stdout to contain ONLY valid JSON-RPC messages
    import sys

    # Startup verbosity control: quiet by default, verbose with MCP_STARTUP_VERBOSE=true
    startup_verbose = os.getenv("MCP_STARTUP_VERBOSE", "false").lower() == "true"

    # Set log level based on startup verbosity and LOG_LEVEL override
    if "LOG_LEVEL" in os.environ:
        # Explicit LOG_LEVEL always takes precedence
        log_level = os.getenv("LOG_LEVEL", "WARNING")
    else:
        # Default behavior: quiet startup (WARNING) unless verbose mode requested
        log_level = "INFO" if startup_verbose else "WARNING"

    logger.remove()
    logger.add(
        sink=sys.stderr,  # Use stderr instead of stdout for MCP compliance
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Only show configuration messages in verbose mode
    if startup_verbose:
        logger.info("Configuration will be auto-discovered on-demand when needed")

        # Configure UCM warning visibility (default: false for production)
        ucm_warnings_enabled = os.getenv('UCM_WARNINGS_ENABLED', 'false').lower() == 'true'
        logger.info(f"UCM warnings {'enabled' if ucm_warnings_enabled else 'disabled'} (UCM_WARNINGS_ENABLED={ucm_warnings_enabled})")

    # Initialize FastMCP server with version in name
    server_version = get_package_version()
    mcp = FastMCP(
        name=f"Revenium MCP Server v{server_version}",
        instructions="""
# Enhanced Revenium Platform API MCP Server

This enhanced MCP server provides comprehensive tools for managing Revenium platform resources
with advanced introspection and metadata capabilities.

## Available Tools

### Core Management Tools
- **manage_products**: Comprehensive product management operations
- **manage_subscriptions**: Complete subscription lifecycle management
- **manage_sources**: Source configuration and management
- **manage_customers**: Customer lifecycle management (Users, Subscribers, Organizations, Teams)
- **manage_alerts**: AI anomaly detection and alert management
- **manage_workflows**: Cross-tool workflow guidance for complex operations
- **manage_metering**: AI transaction metering and usage tracking for billing and analytics
- **manage_metering_elements**: Comprehensive metering element definition management with CRUD operations, templates, and analytics
- **manage_subscriber_credentials**: Subscriber credentials management with CRUD operations, field validation, and NLP support

### Enhanced Introspection Tools
- **tool_introspection**: Comprehensive tool metadata and dependency analysis
  - Discover tool capabilities and relationships
  - View performance metrics and usage analytics
  - Analyze dependency graphs and detect circular dependencies
  - Get agent-friendly tool summaries and quick start guides

## Key Enhancements

### Tool Introspection
- Real-time tool discovery and metadata collection
- Performance metrics tracking and analysis
- Dependency relationship mapping and validation
- Usage pattern analysis and recommendations

### Agent-Friendly Features
- Comprehensive tool summaries and quick start guides
- Working examples and templates for all operations
- Intelligent error handling with actionable suggestions
- Smart defaults for rapid configuration

### Performance Monitoring
- Real-time execution metrics collection
- Success rate tracking and analysis
- Response time monitoring and optimization
- Tool health validation and reporting

## Authentication
Set REVENIUM_API_KEY environment variable with your Revenium API key.

## Quick Start with Introspection
1. Use `tool_introspection(action="list_tools")` to see all available tools
2. Use `tool_introspection(action="get_tool_metadata", tool_name="...")` for detailed tool info
3. Use `tool_introspection(action="get_all_metadata")` for comprehensive tool information
""",
        dependencies=[
            "fastmcp>=2.0.0",
            "httpx>=0.25.0",
            "pydantic>=2.0.0",
            "loguru>=0.7.0",
            "python-dotenv>=1.0.0",
        ]
    )

    return mcp


async def register_tools(mcp: FastMCP) -> None:
    """Register all tools with the MCP server using ToolConfigurationRegistry.

    Args:
        mcp: FastMCP server instance
    """
    logger.info("Registering tools with enhanced MCP server using ToolConfigurationRegistry")

    # Integrate UCM with MCP server (UCM already initialized in main())
    try:
        await ucm_integration_service.integrate_with_mcp_server(mcp)
        # Only log UCM integration success in verbose mode
        startup_verbose = os.getenv("MCP_STARTUP_VERBOSE", "false").lower() == "true"
        if startup_verbose:
            logger.info("UCM integration with MCP server completed")
    except Exception as e:
        # Only log UCM integration failures in verbose mode
        startup_verbose = os.getenv("MCP_STARTUP_VERBOSE", "false").lower() == "true"
        if startup_verbose:
            logger.error(f"Failed to integrate UCM with MCP server: {e}")
            logger.warning("Continuing without UCM integration")

    # Use ToolConfigurationRegistry for conditional tool registration
    # Note: tool_introspection is now registered through the registry in priority order
    from .tool_configuration.registry import ToolConfigurationRegistry
    from .tool_configuration.config import ToolConfig

    # Load tool configuration (will use environment variables or defaults)
    tool_config = ToolConfig()
    registry = ToolConfigurationRegistry(tool_config)

    # Register tools based on configuration profile (includes tool_introspection in priority order)
    await registry.register_tools_conditionally(mcp)

    logger.info("All tools registered successfully via ToolConfigurationRegistry")


async def main() -> None:
    """Run the enhanced MCP server with CLI argument support and onboarding integration."""
    # Check if we're in verbose startup mode
    startup_verbose = os.getenv("MCP_STARTUP_VERBOSE", "false").lower() == "true"

    if startup_verbose:
        logger.info("Starting Enhanced Revenium Platform API MCP Server with Onboarding Support")

    # Create server
    mcp = create_enhanced_server()

    # Initialize UCM integration FIRST
    ucm_api_key_missing = False

    try:
        await ucm_integration_service.initialize()
        if startup_verbose:
            logger.info("UCM integration initialized successfully")
    except Exception as e:
        # Check if this is a missing API key issue (we'll show this later)
        error_msg = str(e).lower()
        if ("api_key" in error_msg or "revenium_api_key" in error_msg or
            "failed to create revenium client" in error_msg or
            "none was provided" in error_msg):
            ucm_api_key_missing = True

        # Only log detailed UCM failures in verbose mode
        if startup_verbose:
            logger.error(f"Failed to initialize UCM integration: {e}")
            logger.warning("Continuing without UCM integration")

    # Initialize introspection with UCM integration
    introspection_integration.ucm_integration_service = ucm_integration_service
    await introspection_integration.initialize()

    # ONBOARDING INTEGRATION: Onboarding tools now registered directly in register_tools()
    # This ensures consistent @mcp.tool() registration pattern for all tools
    if startup_verbose:
        logger.info("✅ Onboarding tools registered with consistent @mcp.tool() pattern")

    # Register standard tools
    await register_tools(mcp)

    # Get server summary for final ready message
    summary = await introspection_integration.get_server_summary()
    server_version = get_package_version()

    # Log server summary with onboarding status (verbose mode only)
    if startup_verbose:
        logger.info(f"Server initialized with {summary['registered_tools']} tools")

        # Log onboarding status
        try:
            from .onboarding import get_onboarding_status
            onboarding_status = await get_onboarding_status()
            if onboarding_status["status"] == "initialized":
                is_first_time = onboarding_status["onboarding_state"]["is_first_time"]
                overall_ready = onboarding_status["environment_validation"]["overall_status"]
                logger.info(f"Onboarding: {'First-time user' if is_first_time else 'Returning user'}, System ready: {overall_ready}")
            else:
                logger.debug(f"Onboarding status: {onboarding_status['status']}")
        except Exception as e:
            logger.debug(f"Could not get onboarding status: {e}")

        logger.info("Enhanced Revenium Platform API MCP Server starting...")

    # Final ready message - always visible regardless of log level
    # This ensures users always see the version and status
    import sys
    print(f"Revenium MCP Server v{server_version} ready with {summary['registered_tools']} tools", file=sys.stderr)

    # Run the server with API key warning if needed
    if ucm_api_key_missing:
        # Monkey patch to show API key warning after FastMCP banner
        original_run_async = mcp.run_async

        async def run_with_api_key_warning():
            # Start the server in the background
            server_task = asyncio.create_task(original_run_async())

            # Wait for FastMCP to display its banner
            await asyncio.sleep(1.0)

            # Show the critical API key warning after the banner
            print("\n🚨 CRITICAL: REVENIUM_API_KEY not found - server will not work until this is set.", file=sys.stderr)
            print("   The key can be found within the Revenium web console on the API Keys page.\n", file=sys.stderr)

            # Wait for the server to complete
            await server_task

        await run_with_api_key_warning()
    else:
        await mcp.run_async()


def main_sync() -> None:
    """Synchronous entry point for the MCP server (used by package entry points)."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
