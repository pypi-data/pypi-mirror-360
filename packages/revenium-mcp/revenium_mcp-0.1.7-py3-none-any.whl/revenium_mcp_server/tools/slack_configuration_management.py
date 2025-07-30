"""Slack Configuration Management Tool - Extracted from enhanced_server.py

This module contains the slack_configuration_management tool for managing
Slack configurations for alert notifications.
"""

from typing import Optional
from loguru import logger

# Import tool execution utilities
from ..tools_decomposed.slack_configuration_management import SlackConfigurationManagement


def safe_extract_text(result):
    """Safely extract text from MCP content objects."""
    if not result:
        return "No result"
    
    # Handle list of content objects
    if isinstance(result, list) and len(result) > 0:
        first_item = result[0]
        if hasattr(first_item, 'text'):
            return first_item.text
        else:
            return str(first_item)
    
    # Handle single content object
    if hasattr(result, 'text'):
        return result.text
    
    return str(result)


async def slack_configuration_management(
    action: str,
    config_id: Optional[str] = None,
    page: int = 0,
    size: int = 20
) -> str:
    """Manage Slack configurations for alert notifications.

    Actions:
        list_configurations: List all available Slack configurations
        get_configuration: Get details of specific configuration (requires config_id)
        set_default_configuration: Set default Slack configuration for alerts (requires config_id)
        get_default_configuration: Get current default Slack configuration
        get_app_oauth_url: Get Revenium app OAuth URL for Slack setup

    Parameters:
        config_id: Slack configuration ID (required for get_configuration and set_default_configuration)
        page: Page number for listing configurations (default: 0)
        size: Number of configurations per page (default: 20)
    """
    arguments = {
        "action": action,
        "config_id": config_id,
        "page": page,
        "size": size
    }

    # Remove None values to avoid validation issues
    arguments = {k: v for k, v in arguments.items() if v is not None}

    # Use standardized execution path
    logger.info(f"🚀 ENHANCED SERVER: Using standardized execution for Slack configuration management action '{action}'")

    # Import standardized_tool_execution from the parent module
    from ..enhanced_server import standardized_tool_execution

    try:
        result = await standardized_tool_execution(
            tool_name="slack_configuration_management",
            action=action,
            arguments=arguments,
            tool_class=SlackConfigurationManagement
        )
        return safe_extract_text(result)
    except Exception as e:
        logger.error(f"Slack configuration management execution failed: {str(e)}")
        # Return formatted error response
        from ..common.error_handling import format_error_response
        error_result = format_error_response(e, f"Slack configuration management action '{action}'")
        return safe_extract_text(error_result)