"""Unified Capability Manager Package.

This package provides the Unified Capability Manager (UCM) architecture that serves as
the single source of truth for all API capabilities across the Revenium MCP server.

The UCM eliminates hardcoded validation layers and provides dynamic capability
verification against actual API endpoints.
"""

from .core import UnifiedCapabilityManager
from .verification import CapabilityVerifier
from .cache import CapabilityCache, CapabilityCacheManager
from .discovery import CapabilityDiscovery
from .mcp_integration import MCPCapabilityIntegration
from .factory import UCMFactory, UCMIntegrationHelper

__all__ = [
    "UnifiedCapabilityManager",
    "CapabilityVerifier",
    "CapabilityCache",
    "CapabilityCacheManager",
    "CapabilityDiscovery",
    "MCPCapabilityIntegration",
    "UCMFactory",
    "UCMIntegrationHelper"
]
