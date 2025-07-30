"""Tool Introspection and Metadata Framework.

This package provides comprehensive tool introspection capabilities for the MCP server,
including metadata collection, dependency mapping, and usage analytics.
"""

from .metadata import ToolMetadata, MetadataProvider, PerformanceMetrics, UsagePattern
from .engine import ToolIntrospectionEngine
from .registry import IntrospectionRegistry

__all__ = [
    "ToolMetadata",
    "MetadataProvider", 
    "PerformanceMetrics",
    "UsagePattern",
    "ToolIntrospectionEngine",
    "IntrospectionRegistry"
]
