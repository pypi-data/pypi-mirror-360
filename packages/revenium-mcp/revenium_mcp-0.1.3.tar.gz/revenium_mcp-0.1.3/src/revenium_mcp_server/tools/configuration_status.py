"""Configuration Status Tool Module.

Extracted from enhanced_server.py as part of pragmatic refactoring initiative.
Maintains exact functionality and MCP protocol compatibility.

Agent: 2
Extraction Date: 2025-06-25
Original Location: enhanced_server.py lines 2317-2347
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Initialize MCP server instance for tool registration
mcp = FastMCP("configuration_status")

@dataclass
class ConfigurationStatusArgs:
    """Arguments for configuration status tool following enterprise standards."""
    include_sensitive: Optional[bool] = None
    show_detailed_analysis: Optional[bool] = None
    include_recommendations: Optional[bool] = None
    format_output: Optional[str] = None


# Feature flag for rollback capability
def use_extracted_tool() -> bool:
    """Check if extracted tool should be used vs original implementation."""
    return os.getenv("USE_EXTRACTED_CONFIGURATION_STATUS", "false").lower() == "true"

def _create_configuration_args(**kwargs) -> ConfigurationStatusArgs:
    """Create configuration status arguments dataclass.
    
    Args:
        **kwargs: Keyword arguments for ConfigurationStatusArgs
        
    Returns:
        ConfigurationStatusArgs: Configured arguments dataclass
    """
    return ConfigurationStatusArgs(**kwargs)


def _prepare_config_arguments_dict(action: str, args: ConfigurationStatusArgs) -> Dict[str, Any]:
    """Prepare arguments dictionary for configuration status tool execution.
    
    Args:
        action: Action to perform
        args: Configuration status arguments
        
    Returns:
        Dict with non-None arguments for tool execution
    """
    arguments = {"action": action}
    
    # Add non-None values from dataclass
    if args.include_sensitive is not None:
        arguments["include_sensitive"] = args.include_sensitive
    if args.show_detailed_analysis is not None:
        arguments["show_detailed_analysis"] = args.show_detailed_analysis
    if args.include_recommendations is not None:
        arguments["include_recommendations"] = args.include_recommendations
    if args.format_output is not None:
        arguments["format_output"] = args.format_output
        
    return arguments


async def _execute_config_tool_with_standardized_path(
    arguments: Dict[str, Any]
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Execute configuration status tool using standardized execution path.
    
    Args:
        arguments: Prepared arguments dictionary
        
    Returns:
        Tool execution result
    """
    action = arguments["action"]
    logger.info(f"🚀 ENHANCED SERVER: Using standardized execution for configuration status action '{action}'")
    
    from ..tools_decomposed.configuration_status import ConfigurationStatus
    tool_instance = ConfigurationStatus()
    result = await tool_instance.handle_action(action, arguments)
    return result


@mcp.tool()
async def configuration_status(
    action: str,
    config_args: Optional[ConfigurationStatusArgs] = None
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """🔧 DIAGNOSTIC: Comprehensive configuration status and diagnostic display with detailed analysis.
    
    EXTRACTED: This tool has been extracted from enhanced_server.py
    FEATURE_FLAG: USE_EXTRACTED_CONFIGURATION_STATUS
    ROLLBACK: Set environment variable to 'false' to use original implementation
    
    Args:
        action: Action to perform
        config_args: Optional dataclass containing configuration status arguments
        
    Returns:
        Tool execution result
    """
    try:
        # Handle None case
        if config_args is None:
            config_args = ConfigurationStatusArgs()
        
        # Use provided arguments dataclass
        args = config_args
        
        # Prepare arguments dictionary
        arguments = _prepare_config_arguments_dict(action, args)
        
        # Execute using standardized path
        return await _execute_config_tool_with_standardized_path(arguments)
        
    except Exception as e:
        logger.error(f"Error in extracted configuration_status: {e}")
        # Maintain exact same error handling as original
        raise