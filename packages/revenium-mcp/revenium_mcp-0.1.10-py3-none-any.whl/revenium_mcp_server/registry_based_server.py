"""Registry-based Enhanced MCP Server - Phase 6 Implementation.

This module implements the final phase of the enhanced_server.py refactoring,
replacing 43 individual tool registrations with 4 enterprise-compliant registries,
achieving the target line reduction from 2,237 to ~450 lines.
"""

import os
import asyncio
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

# Core MCP dependencies
from fastmcp import FastMCP  # type: ignore[import-untyped]
from loguru import logger  # type: ignore[import-untyped]
from dotenv import load_dotenv  # type: ignore[import-untyped]

# Import enhanced introspection
from .introspection.integration import introspection_integration

# Import UCM integration
from .capability_manager.integration_service import ucm_integration_service

# Import performance monitoring
# Performance monitoring removed - infrastructure monitoring handled externally

# Import all 4 enterprise registries
from .registries import (
    BusinessManagementRegistry,
    AnalyticsRegistry,
    CommunicationRegistry,
    InfrastructureRegistry
)

# Import MCP types
from mcp.types import TextContent, ImageContent, EmbeddedResource  # type: ignore[import-untyped]


class RegistryBasedServer:
    """Registry-based MCP server that replaces individual tool registrations.
    
    Manages 4 enterprise-compliant registries instead of 43 individual tools,
    achieving enterprise compliance and dramatic line reduction.
    """
    
    def __init__(self):
        """Initialize registry-based server with enterprise registries."""
        self.mcp: Optional[FastMCP] = None
        self.business_registry: Optional[BusinessManagementRegistry] = None
        self.analytics_registry: Optional[AnalyticsRegistry] = None
        self.communication_registry: Optional[CommunicationRegistry] = None
        self.infrastructure_registry: Optional[InfrastructureRegistry] = None
        
    async def initialize_registries(self, mcp: FastMCP) -> None:
        """Initialize all 4 enterprise registries (≤25 lines)."""
        self.mcp = mcp
        
        # Initialize registries with proper dependencies
        self.business_registry = BusinessManagementRegistry()
        self.analytics_registry = AnalyticsRegistry()
        self.communication_registry = CommunicationRegistry(mcp, logger, ucm_integration_service)
        self.infrastructure_registry = InfrastructureRegistry()
        
        logger.info("✅ All 4 enterprise registries initialized")
        
    async def register_all_tools(self) -> None:
        """Register all tools via 4 registries instead of 43 individual tools (≤25 lines)."""
        if not self.mcp:
            raise RuntimeError("Server not initialized")
            
        # Register Business Management tools (4 tools)
        await self._register_business_tools()
        
        # Register Analytics tools (3 tools + Builder Pattern)
        await self._register_analytics_tools()
        
        # Register Communication tools (4 tools + OAuth)
        await self._register_communication_tools()
        
        # Register Infrastructure tools (4 tools)
        await self._register_infrastructure_tools()
        
        logger.info("🎉 All registry tools registered - 43 individual tools → 4 registries")
        
    async def _register_business_tools(self) -> None:
        """Register business management tools via BusinessManagementRegistry (≤25 lines)."""
        if not self.business_registry:
            return
            
        business_tools = self.business_registry.get_supported_tools()
        logger.info(f"Registering {len(business_tools)} business tools: {business_tools}")
        
        # Register each business tool through the registry
        for tool_name in business_tools:
            await self._register_registry_tool(
                tool_name, 
                self.business_registry, 
                f"Business management tool: {tool_name}"
            )
            
    async def _register_analytics_tools(self) -> None:
        """Register analytics tools via AnalyticsRegistry with Builder Pattern (≤25 lines).""" 
        if not self.analytics_registry:
            return
            
        analytics_tools = self.analytics_registry.get_supported_tools()
        logger.info(f"Registering {len(analytics_tools)} analytics tools with Builder Pattern: {analytics_tools}")
        
        # Register each analytics tool through the registry
        for tool_name in analytics_tools:
            await self._register_registry_tool(
                tool_name,
                self.analytics_registry,
                f"Analytics tool with Builder Pattern: {tool_name}"
            )
            
    async def _register_communication_tools(self) -> None:
        """Register communication tools via CommunicationRegistry with OAuth (≤25 lines)."""
        if not self.communication_registry:
            return
            
        communication_tools = self.communication_registry.get_supported_tools()
        logger.info(f"Registering {len(communication_tools)} communication tools with OAuth: {communication_tools}")
        
        # Register each communication tool through the registry
        for tool_name in communication_tools:
            await self._register_registry_tool(
                tool_name,
                self.communication_registry, 
                f"Communication tool with OAuth: {tool_name}"
            )
            
    async def _register_infrastructure_tools(self) -> None:
        """Register infrastructure tools via InfrastructureRegistry (≤25 lines)."""
        if not self.infrastructure_registry:
            return
            
        infrastructure_tools = self.infrastructure_registry.get_supported_tools()
        logger.info(f"Registering {len(infrastructure_tools)} infrastructure tools: {infrastructure_tools}")
        
        # Register each infrastructure tool through the registry
        for tool_name in infrastructure_tools:
            await self._register_registry_tool(
                tool_name,
                self.infrastructure_registry,
                f"Infrastructure tool: {tool_name}"
            )
            
    async def _register_registry_tool(self, tool_name: str, registry: Any, description: str) -> None:
        """Register a single tool through its registry (≤25 lines, ≤3 params)."""
        if not self.mcp:
            return
            
        @self.mcp.tool()
        async def registry_tool(**kwargs: Any) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
            """Registry-based tool execution."""
            try:
                # Convert kwargs to request object
                request = kwargs
                result = await registry.execute_tool(tool_name, request)
                return result
            except Exception as e:
                logger.error(f"Registry tool {tool_name} failed: {e}")
                return [TextContent(type="text", text=f"Error executing {tool_name}: {str(e)}")]
                
        # Update function name for proper MCP registration
        registry_tool.__name__ = tool_name
        logger.debug(f"✅ Registered {tool_name} via registry")


@asynccontextmanager
async def lifespan_manager():  # type: ignore[misc]
    """Manage server lifespan with registry initialization."""
    logger.info("🚀 Starting registry-based MCP server lifespan")
    
    # Initialize UCM integration service
    try:
        await ucm_integration_service.initialize()
        logger.info("✅ UCM integration service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize UCM integration service: {e}")
        logger.warning("Continuing without UCM integration")
    
    yield
    
    logger.info("🛑 Registry-based MCP server lifespan ended")


def create_registry_based_server() -> FastMCP:
    """Create enhanced MCP server with registry-based architecture (≤25 lines)."""
    # Load environment variables
    load_dotenv()
    
    # Create FastMCP server
    mcp = FastMCP(
        name="revenium-platformapi-registry-based", 
        lifespan=lifespan_manager
    )
    
    logger.info("✅ Registry-based MCP server created")
    return mcp


async def register_core_tools(mcp: FastMCP) -> None:
    """Register core infrastructure tools (introspection, UCM) (≤25 lines)."""
    logger.info("Registering core infrastructure tools")
    
    # Integrate UCM with MCP server
    try:
        await ucm_integration_service.integrate_with_mcp_server(mcp)
        logger.info("✅ UCM integration with MCP server completed")
    except Exception as e:
        logger.error(f"Failed to integrate UCM with MCP server: {e}")
        logger.warning("Continuing without UCM integration")
    
    # Add introspection tool
    await introspection_integration.add_introspection_tool_to_server(mcp)
    logger.info("✅ Core tools registered")


async def main() -> None:
    """Main function - Registry-based server with ~450 lines total (≤25 lines)."""
    logger.info("🚀 Starting Registry-Based Enhanced Revenium Platform API MCP Server")
    
    # Create registry-based server
    mcp = create_registry_based_server()
    server = RegistryBasedServer()
    
    # Initialize registries and tools
    await server.initialize_registries(mcp)
    await register_core_tools(mcp)
    await server.register_all_tools()
    
    # Run server
    await mcp.run()
    logger.info("✅ Registry-based server completed successfully")


if __name__ == "__main__":
    asyncio.run(main())