"""MCP Tools Package.

This package contains all MCP tool implementations organized by functionality.
Each tool module handles a specific domain (products, subscriptions, sources, etc.).
"""

# Import unified tool base class (legacy base classes removed)
from .unified_tool_base import ToolBase
# Legacy base classes removed - use ToolBase only

# Import source tools - UPDATED to use consolidated source management
from .source_management import SourceManagement

# Import product tools - UPDATED to use consolidated product management
from .product_management import ProductManagement

# Import subscription tools - UPDATED to use consolidated subscription management
from .subscription_management import SubscriptionManagement

# Import consolidated management tools
from .alert_management import AlertManagement
from .customer_management import CustomerManagement
from .metering_management import MeteringManagement
from .metering_elements_management import MeteringElementsManagement
from .workflow_management import WorkflowManagement

# Performance monitoring tools removed - infrastructure monitoring handled externally

# Temporary backward compatibility import during decomposition
# Note: Removed circular import from ..tools to avoid import issues
# from ..tools import ReveniumTools

__all__ = [
    # Unified tool base class (recommended)
    "ToolBase",
    # Consolidated management tools
    "SourceManagement",
    "ProductManagement",
    "SubscriptionManagement",
    "AlertManagement",
    "CustomerManagement",
    "MeteringManagement",
    "MeteringElementsManagement",
    "WorkflowManagement",
    # Performance monitoring tools removed - infrastructure monitoring handled externally
]
