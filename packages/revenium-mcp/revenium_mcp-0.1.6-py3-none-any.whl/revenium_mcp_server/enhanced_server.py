"""Enhanced MCP server with tool introspection capabilities.

This module contains the enhanced FastMCP server implementation that provides
comprehensive tool introspection and metadata capabilities alongside the
standard Revenium platform API functionality.

Copyright (c) 2024 Revenium
Licensed under the MIT License. See LICENSE file for details.
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
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


def _check_for_old_subscriber_format(arguments: Dict[str, Any]) -> Optional[str]:
    """Check for old subscriber format usage and provide structured migration guidance.

    Following Phase 2 error handling guidelines for validation errors with
    structured error responses and actionable migration guidance.
    """
    import json
    from .common.error_handling import (
        create_structured_validation_error,
        format_structured_error
    )

    old_fields = []
    migration_guidance = []

    # Check for old subscriber fields
    if "subscriber_email" in arguments and arguments["subscriber_email"] is not None:
        old_fields.append("subscriber_email")
        migration_guidance.append(f"subscriber_email: '{arguments['subscriber_email']}' → subscriber.email: '{arguments['subscriber_email']}'")

    if "subscriber_id" in arguments and arguments["subscriber_id"] is not None:
        old_fields.append("subscriber_id")
        migration_guidance.append(f"subscriber_id: '{arguments['subscriber_id']}' → subscriber.id: '{arguments['subscriber_id']}'")

    if "subscriber_credential_name" in arguments and arguments["subscriber_credential_name"] is not None:
        old_fields.append("subscriber_credential_name")
        migration_guidance.append(f"subscriber_credential_name: '{arguments['subscriber_credential_name']}' → subscriber.credential.name: '{arguments['subscriber_credential_name']}'")

    if "subscriber_credential" in arguments and arguments["subscriber_credential"] is not None:
        old_fields.append("subscriber_credential")
        migration_guidance.append(f"subscriber_credential: '{arguments['subscriber_credential']}' → subscriber.credential.value: '{arguments['subscriber_credential']}'")

    if old_fields:
        # Build new subscriber object example
        new_subscriber = {}
        if "subscriber_id" in arguments and arguments["subscriber_id"] is not None:
            new_subscriber["id"] = arguments["subscriber_id"]
        if "subscriber_email" in arguments and arguments["subscriber_email"] is not None:
            new_subscriber["email"] = arguments["subscriber_email"]
        if ("subscriber_credential_name" in arguments and arguments["subscriber_credential_name"] is not None) or \
           ("subscriber_credential" in arguments and arguments["subscriber_credential"] is not None):
            credential = {}
            if "subscriber_credential_name" in arguments and arguments["subscriber_credential_name"] is not None:
                credential["name"] = arguments["subscriber_credential_name"]
            if "subscriber_credential" in arguments and arguments["subscriber_credential"] is not None:
                credential["value"] = arguments["subscriber_credential"]
            if credential:
                new_subscriber["credential"] = credential

        # Create structured validation error following Phase 2 guidelines
        error = create_structured_validation_error(
            message="🚨 **SUBSCRIBER FORMAT CHANGED** - Old individual fields no longer supported",
            field="subscriber_format",
            value=f"old_fields: {', '.join(old_fields)}",
            suggestions=[
                "🔄 **IMMEDIATE ACTION**: Replace old subscriber fields with new subscriber object structure",
                "📖 **MIGRATION GUIDE**: Use the provided field mapping to convert your data",
                "✅ **QUICK FIX**: Copy the corrected format example below",
                "🔍 **VALIDATION**: Use validate() action to test your new format before submission",
                "📚 **REFERENCE**: Use get_examples() to see more subscriber object examples"
            ],
            examples={
                "migration_mapping": {field: guidance for field, guidance in zip(old_fields, migration_guidance)},
                "new_subscriber_object": new_subscriber,
                "corrected_format": {
                    "action": "submit_ai_transaction",
                    "model": "your-model",
                    "provider": "your-provider",
                    "input_tokens": 1500,
                    "output_tokens": 800,
                    "duration_ms": 2500,
                    "subscriber": new_subscriber
                },
                "validation_command": f"validate(model='your-model', provider='your-provider', input_tokens=1500, output_tokens=800, duration_ms=2500, subscriber={json.dumps(new_subscriber)})"
            }
        )

        return format_structured_error(error)

    return None


# REMOVED: safe_check_text_content function - replaced with proper exception handling


# Import standardized tool execution from separate module to avoid circular imports
from .common.tool_execution import standardized_tool_execution


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

    # Configuration will be auto-discovered on-demand when first tool is used
    logger.info("Configuration will be auto-discovered on-demand when needed")

    # Configure logging - CRITICAL: Use stderr to comply with MCP stdio transport
    # MCP protocol requires stdout to contain ONLY valid JSON-RPC messages
    import sys
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.remove()
    logger.add(
        sink=sys.stderr,  # Use stderr instead of stdout for MCP compliance
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Configure UCM warning visibility (default: false for production)
    ucm_warnings_enabled = os.getenv('UCM_WARNINGS_ENABLED', 'false').lower() == 'true'
    logger.info(f"UCM warnings {'enabled' if ucm_warnings_enabled else 'disabled'} (UCM_WARNINGS_ENABLED={ucm_warnings_enabled})")

    # Initialize FastMCP server
    mcp = FastMCP(
        name="Revenium MCP Server",
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
        logger.info("UCM integration with MCP server completed")
    except Exception as e:
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
    logger.info("Starting Enhanced Revenium Platform API MCP Server with Onboarding Support")

    # Create server
    mcp = create_enhanced_server()

    # Initialize UCM integration FIRST
    try:
        await ucm_integration_service.initialize()
        logger.info("UCM integration initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize UCM integration: {e}")
        logger.warning("Continuing without UCM integration")

    # Initialize introspection with UCM integration
    introspection_integration.ucm_integration_service = ucm_integration_service
    await introspection_integration.initialize()

    # ONBOARDING INTEGRATION: Onboarding tools now registered directly in register_tools()
    # This ensures consistent @mcp.tool() registration pattern for all tools
    logger.info("✅ Onboarding tools registered with consistent @mcp.tool() pattern")

    # Register standard tools
    await register_tools(mcp)

    # Log server summary with onboarding status
    summary = await introspection_integration.get_server_summary()
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

    # Run the server - use logger instead of print for MCP compliance
    logger.info("Enhanced Revenium Platform API MCP Server starting...")
    await mcp.run_async()


def main_sync() -> None:
    """Synchronous entry point for the MCP server (used by package entry points)."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
