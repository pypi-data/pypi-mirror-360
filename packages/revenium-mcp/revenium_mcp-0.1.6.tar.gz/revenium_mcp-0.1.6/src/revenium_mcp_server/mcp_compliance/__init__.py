"""MCP Compliance Package.

This package provides Model Context Protocol (MCP) compliance features including:
- JSON-RPC 2.0 compliant error handling
- MCP lifecycle management
- Resource discovery and access
- Prompt template system
- Session management
- Enterprise reliability patterns

The package ensures full MCP protocol compliance while maintaining backward
compatibility with existing functionality.
"""

from .error_handling import (
    MCPError,
    JSONRPCErrorCode,
    MCPErrorData,
    create_invalid_params_error,
    create_method_not_found_error,
    create_tool_execution_error,
    create_resource_not_found_error,
    create_internal_error
)

from .error_translator import (
    MCPErrorTranslator,
    error_translator,
    translate_to_mcp_error,
    format_mcp_error_response,
    with_mcp_error_handling
)

from .lifecycle import (
    MCPLifecycleManager,
    lifecycle_manager
)

from .protocol_handler import (
    MCPProtocolHandler,
    protocol_handler,
    with_mcp_protocol_validation
)

from .resources import (
    MCPResource,
    ResourceType,
    ResourceMimeType,
    MCPResourceManager,
    ResourceSubscription,
    resource_manager
)

from .resource_discovery import (
    MCPResourceDiscoveryEngine,
    resource_discovery_engine
)

from .capability_manager import (
    CapabilityInfo,
    ServerInfo,
    MCPCapabilityManager,
    capability_manager
)

from .notifications import (
    NotificationMessage,
    NotificationType,
    MCPNotificationManager,
    notification_manager
)

from .session_manager import (
    SessionInfo,
    MCPSessionManager,
    session_manager
)

__all__ = [
    # Error handling classes
    "MCPError",
    "JSONRPCErrorCode", 
    "MCPErrorData",
    
    # Error creation functions
    "create_invalid_params_error",
    "create_method_not_found_error",
    "create_tool_execution_error",
    "create_resource_not_found_error",
    "create_internal_error",
    
    # Error translation
    "MCPErrorTranslator",
    "error_translator",
    "translate_to_mcp_error",
    "format_mcp_error_response",
    "with_mcp_error_handling",

    # Lifecycle management
    "MCPLifecycleManager",
    "lifecycle_manager",

    # Protocol handling
    "MCPProtocolHandler",
    "protocol_handler",
    "with_mcp_protocol_validation",

    # Resource management
    "MCPResource",
    "ResourceType",
    "ResourceMimeType",
    "MCPResourceManager",
    "ResourceSubscription",
    "resource_manager",

    # Resource discovery
    "MCPResourceDiscoveryEngine",
    "resource_discovery_engine",

    # Capability management
    "CapabilityInfo",
    "ServerInfo",
    "MCPCapabilityManager",
    "capability_manager",

    # Notifications
    "NotificationMessage",
    "NotificationType",
    "MCPNotificationManager",
    "notification_manager",

    # Session management
    "SessionInfo",
    "MCPSessionManager",
    "session_manager"
]
