"""Setup Checklist Tool Module.

Extracted from enhanced_server.py as part of pragmatic refactoring initiative.
Maintains exact functionality and MCP protocol compatibility.

Agent: 2
Extraction Date: 2025-06-25
Original Location: enhanced_server.py lines 2254-2284
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Initialize MCP server instance for tool registration
mcp = FastMCP("setup_checklist")

@dataclass
class SetupChecklistArgs:
    """Arguments for setup checklist tool following enterprise standards."""
    show_completion_percentage: Optional[bool] = None
    highlight_priority_items: Optional[bool] = None
    include_next_steps: Optional[bool] = None
    group_by_category: Optional[bool] = None


# Feature flag for rollback capability
def use_extracted_tool() -> bool:
    """Check if extracted tool should be used vs original implementation."""
    return os.getenv("USE_EXTRACTED_SETUP_CHECKLIST", "false").lower() == "true"

def _create_setup_args(**kwargs) -> SetupChecklistArgs:
    """Create setup checklist arguments dataclass.
    
    Args:
        **kwargs: Keyword arguments for SetupChecklistArgs
        
    Returns:
        SetupChecklistArgs: Configured arguments dataclass
    """
    return SetupChecklistArgs(**kwargs)


def _prepare_arguments_dict(action: str, args: SetupChecklistArgs) -> Dict[str, Any]:
    """Prepare arguments dictionary for tool execution.
    
    Args:
        action: Action to perform
        args: Setup checklist arguments
        
    Returns:
        Dict with non-None arguments for tool execution
    """
    arguments = {"action": action}
    
    # Add non-None values from dataclass
    if args.show_completion_percentage is not None:
        arguments["show_completion_percentage"] = args.show_completion_percentage
    if args.highlight_priority_items is not None:
        arguments["highlight_priority_items"] = args.highlight_priority_items
    if args.include_next_steps is not None:
        arguments["include_next_steps"] = args.include_next_steps
    if args.group_by_category is not None:
        arguments["group_by_category"] = args.group_by_category
        
    return arguments


async def _execute_tool_with_standardized_path(
    arguments: Dict[str, Any]
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """Execute tool using standardized execution path.
    
    Args:
        arguments: Prepared arguments dictionary
        
    Returns:
        Tool execution result
    """
    action = arguments["action"]
    logger.info(f"🚀 ENHANCED SERVER: Using standardized execution for setup checklist action '{action}'")
    
    from ..tools_decomposed.setup_checklist import SetupChecklist
    tool_instance = SetupChecklist()
    result = await tool_instance.handle_action(action, arguments)
    return result


@mcp.tool()
async def setup_checklist(
    action: str,
    setup_args: Optional[SetupChecklistArgs] = None
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """🚀 RECOMMENDED FOR SETUP: Show comprehensive setup completion status and detailed configuration checklist.
    
    EXTRACTED: This tool has been extracted from enhanced_server.py
    FEATURE_FLAG: USE_EXTRACTED_SETUP_CHECKLIST
    ROLLBACK: Set environment variable to 'false' to use original implementation
    
    Args:
        action: Action to perform
        setup_args: Optional dataclass containing setup checklist arguments
        
    Returns:
        Tool execution result
    """
    try:
        # Handle None case
        if setup_args is None:
            setup_args = SetupChecklistArgs()
        
        # Use provided arguments dataclass
        args = setup_args
        
        # Prepare arguments dictionary
        arguments = _prepare_arguments_dict(action, args)
        
        # Execute using standardized path
        return await _execute_tool_with_standardized_path(arguments)
        
    except Exception as e:
        logger.error(f"Error in extracted setup_checklist: {e}")
        # Maintain exact same error handling as original
        raise