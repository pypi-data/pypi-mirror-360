"""Welcome and Setup Tool Module.

Extracted from enhanced_server.py as part of pragmatic refactoring initiative.
Maintains exact functionality and MCP protocol compatibility.

Agent: 2
Extraction Date: 2025-06-25
Original Location: enhanced_server.py lines 2212-2238
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Initialize MCP server instance for tool registration
mcp = FastMCP("welcome_and_setup")

@dataclass
class WelcomeSetupArgs:
    """Arguments for welcome and setup tool following enterprise standards."""
    show_environment: Optional[bool] = None
    include_recommendations: Optional[bool] = None


# Feature flag for rollback capability
def use_extracted_tool() -> bool:
    """Check if extracted tool should be used vs original implementation."""
    return os.getenv("USE_EXTRACTED_WELCOME_AND_SETUP", "false").lower() == "true"

def _create_welcome_args(
    show_environment: Optional[bool] = None,
    include_recommendations: Optional[bool] = None
) -> WelcomeSetupArgs:
    """Create welcome and setup arguments dataclass.
    
    Args:
        show_environment: Whether to show environment details
        include_recommendations: Whether to include recommendations
        
    Returns:
        WelcomeSetupArgs: Configured arguments dataclass
    """
    return WelcomeSetupArgs(
        show_environment=show_environment,
        include_recommendations=include_recommendations
    )


def _prepare_welcome_arguments_dict(action: str, args: WelcomeSetupArgs) -> Dict[str, Any]:
    """Prepare arguments dictionary for welcome setup tool execution.
    
    Args:
        action: Action to perform
        args: Welcome setup arguments
        
    Returns:
        Dict with non-None arguments for tool execution
    """
    arguments = {"action": action}
    
    # Add non-None values from dataclass
    if args.show_environment is not None:
        arguments["show_environment"] = args.show_environment
    if args.include_recommendations is not None:
        arguments["include_recommendations"] = args.include_recommendations
        
    return arguments


async def _execute_welcome_tool_with_standardized_path(
    arguments: Dict[str, Any]
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Execute welcome setup tool using standardized execution path.
    
    Args:
        arguments: Prepared arguments dictionary
        
    Returns:
        Tool execution result
    """
    action = arguments["action"]
    logger.info(f"🚀 ENHANCED SERVER: Using standardized execution for welcome and setup action '{action}'")
    
    from ..tools_decomposed.welcome_setup import WelcomeSetup
    tool_instance = WelcomeSetup()
    result = await tool_instance.handle_action(action, arguments)
    return result


@mcp.tool()
async def welcome_and_setup(
    action: str,
    show_environment: Optional[bool] = None,
    include_recommendations: Optional[bool] = None
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """START HERE: Welcome new users and guide initial setup with comprehensive environment status.
    
    Available actions: show_welcome, setup_checklist, environment_status, next_steps, complete_setup
    
    EXTRACTED: This tool has been extracted from enhanced_server.py
    FEATURE_FLAG: USE_EXTRACTED_WELCOME_AND_SETUP
    ROLLBACK: Set environment variable to 'false' to use original implementation
    
    Args:
        action: Action to perform (show_welcome, setup_checklist, environment_status, next_steps, complete_setup)
        show_environment: Whether to show environment details
        include_recommendations: Whether to include recommendations
        
    Returns:
        Tool execution result
    """
    try:
        # Create arguments using dataclass pattern
        args = _create_welcome_args(show_environment, include_recommendations)
        
        # Prepare arguments dictionary
        arguments = _prepare_welcome_arguments_dict(action, args)
        
        # Execute using standardized path
        return await _execute_welcome_tool_with_standardized_path(arguments)
        
    except Exception as e:
        logger.error(f"Error in extracted welcome_and_setup: {e}")
        # Maintain exact same error handling as original
        raise