"""Verify Email Setup Tool - Extracted from enhanced_server.py

This module contains the verify_email_setup tool for guiding email configuration
and verification for notification setup.
"""

import os
from typing import Any, Dict, List, Optional, Union
from loguru import logger

# Import MCP types
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Import tool execution utilities
from ..tools_decomposed.email_verification import EmailVerification


async def verify_email_setup(
    action: str,
    email: Optional[str] = None,
    validate_format: Optional[bool] = None,
    suggest_smart_defaults: Optional[bool] = None,
    include_setup_guidance: Optional[bool] = None,
    test_configuration: Optional[bool] = None
) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
    """🚀 RECOMMENDED FOR SETUP: Guide email configuration and verification for notification setup."""

    arguments = {
        "action": action,
        "email": email,
        "validate_format": validate_format,
        "suggest_smart_defaults": suggest_smart_defaults,
        "include_setup_guidance": include_setup_guidance,
        "test_configuration": test_configuration
    }

    # Remove None values
    arguments = {k: v for k, v in arguments.items() if v is not None}

    # Use standardized execution path (same pattern as main tools)
    logger.info(f"🚀 ENHANCED SERVER: Using standardized execution for email verification action '{action}'")

    # Import standardized_tool_execution from the parent module
    from ..enhanced_server import standardized_tool_execution
    
    result = await standardized_tool_execution(
        tool_name="verify_email_setup",
        action=action,
        arguments=arguments,
        tool_class=EmailVerification
    )
    return result