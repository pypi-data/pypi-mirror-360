"""Welcome and Setup Tool for Revenium MCP Server.

This tool provides comprehensive onboarding and setup guidance for new users,
using the existing validation infrastructure to ensure consistency with the
debug_auto_discovery tool.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, Union, ClassVar
from datetime import datetime
from loguru import logger

from mcp.types import TextContent, ImageContent, EmbeddedResource

from .unified_tool_base import ToolBase
from ..introspection.metadata import ToolType, ToolCapability
from ..onboarding.detection_service import get_onboarding_state, detect_first_time_user
from ..onboarding.env_validation import validate_environment_variables
from ..config_store import get_config_value
from ..agent_friendly import UnifiedResponseFormatter
from ..common.error_handling import (
    ErrorCodes, ToolError,
    create_structured_validation_error,
    format_structured_error
)


class WelcomeSetup(ToolBase):
    """Welcome and setup tool for new user onboarding.
    
    This tool provides comprehensive onboarding guidance using the existing
    validation infrastructure to ensure consistency with the system.
    """
    
    tool_name: ClassVar[str] = "welcome_and_setup"
    tool_description: ClassVar[str] = "Welcome and initial setup guidance with comprehensive onboarding. Key actions: show_welcome, setup_checklist, next_steps, complete_setup. Use get_examples() for setup guidance and get_capabilities() for complete action list."
    business_category: ClassVar[str] = "Setup and Configuration Tools"
    tool_type = ToolType.UTILITY
    tool_version = "1.0.0"
    
    def __init__(self, ucm_helper=None):
        """Initialize welcome and setup tool.
        
        Args:
            ucm_helper: UCM integration helper for capability management
        """
        super().__init__(ucm_helper)
        self.formatter = UnifiedResponseFormatter("welcome_and_setup")
    
    async def _get_input_schema(self) -> Dict[str, Any]:
        """Context7 single source of truth for welcome_and_setup schema."""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": await self._get_supported_actions(),
                    "description": "Action to perform - show_welcome for main onboarding, setup_checklist for status details, complete_setup to finish"
                },
                # Optional display configuration parameters
                "show_environment": {
                    "type": "boolean",
                    "description": "Include environment variables in status display (optional for environment_status action)"
                },
                "include_recommendations": {
                    "type": "boolean", 
                    "description": "Include personalized recommendations in output (optional for show_welcome and next_steps actions)"
                },
                # Completion confirmation parameter
                "confirm_completion": {
                    "type": "boolean",
                    "description": "Confirm completion of setup process (required for complete_setup action)"
                }
            },
            "required": [],  # Context7: User-centric - no required fields, defaults to show_welcome
            "additionalProperties": True  # Context7: Allow all supported fields for maximum flexibility
        }
    
    async def handle_action(
        self, 
        action: str, 
        arguments: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle welcome and setup actions.
        
        Args:
            action: Action to perform
            arguments: Action arguments
            
        Returns:
            Tool response
        """
        try:
            # Context7 default action pattern: If no action provided, default to show_welcome
            if not action:
                action = "show_welcome"
            
            if action == "show_welcome":
                return await self._handle_show_welcome(arguments)
            elif action == "setup_checklist":
                return await self._handle_setup_checklist(arguments)
            elif action == "environment_status":
                return await self._handle_environment_status(arguments)
            elif action == "next_steps":
                return await self._handle_next_steps(arguments)
            elif action == "complete_setup":
                return await self._handle_complete_setup(arguments)
            elif action == "help" or action == "get_actions":
                return await self._handle_help(arguments)
            elif action == "get_examples":
                return await self._handle_get_examples(arguments)
            elif action == "get_capabilities":
                return await self._handle_get_capabilities(arguments)
            else:
                error = create_structured_validation_error(
                    field="action",
                    value=action,
                    message=f"Unknown welcome setup action: {action}",
                    examples={
                        "valid_actions": [
                            "show_welcome",
                            "setup_checklist",
                            "environment_status",
                            "next_steps",
                            "complete_setup",
                            "help",
                            "get_actions",
                            "get_examples",
                            "get_capabilities"
                        ],
                        "example_usage": {
                            "show_welcome": "Display welcome message and overview",
                            "setup_checklist": "Show detailed setup completion status",
                            "environment_status": "Display all environment variables",
                            "next_steps": "Get personalized next steps",
                            "help": "Show available actions and usage examples"
                        }
                    }
                )
                return [TextContent(type="text", text=format_structured_error(error))]
                
        except Exception as e:
            logger.error(f"Error in welcome_and_setup action {action}: {e}")
            error = ToolError(
                message=f"Failed to execute welcome setup action: {action}",
                error_code=ErrorCodes.TOOL_ERROR,
                field="welcome_setup",
                value=str(e),
                suggestions=[
                    "Try again with a valid action",
                    "Check the action name and parameters",
                    "Use setup_checklist to see current status"
                ]
            )
            return [TextContent(type="text", text=format_structured_error(error))]
    
    async def _handle_show_welcome(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle show_welcome action - main welcome message and overview."""
        logger.debug("🎉 Showing welcome message and setup overview")
        
        # Get onboarding state using existing infrastructure
        onboarding_state = await get_onboarding_state()
        
        # Get environment validation using existing infrastructure
        validation_result = await validate_environment_variables()
        
        # Build welcome message
        welcome_text = self._build_welcome_message(onboarding_state, validation_result)
        
        return [TextContent(type="text", text=welcome_text)]
    
    async def _handle_setup_checklist(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle setup_checklist action - detailed setup status."""
        logger.debug("📋 Showing detailed setup checklist")
        
        # Get onboarding state
        onboarding_state = await get_onboarding_state()
        
        # Get environment validation
        validation_result = await validate_environment_variables()
        
        # Build checklist
        checklist_text = self._build_setup_checklist(onboarding_state, validation_result)
        
        return [TextContent(type="text", text=checklist_text)]
    
    async def _handle_environment_status(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle environment_status action - complete environment variable display."""
        logger.debug("🔍 Showing complete environment variable status")
        
        # Get validation result using existing infrastructure
        validation_result = await validate_environment_variables()
        
        # Build environment status display
        env_status_text = self._build_environment_status(validation_result)
        
        return [TextContent(type="text", text=env_status_text)]
    
    async def _handle_next_steps(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle next_steps action - personalized recommendations."""
        logger.debug("🎯 Generating personalized next steps")
        
        # Get onboarding state
        onboarding_state = await get_onboarding_state()
        
        # Build next steps
        next_steps_text = self._build_next_steps(onboarding_state)
        
        return [TextContent(type="text", text=next_steps_text)]
    
    async def _handle_complete_setup(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle complete_setup action - mark onboarding as complete."""
        logger.debug("✅ Marking onboarding as complete")

        # CRITICAL: Validate setup completion parameters
        confirmation = arguments.get("confirm_completion")
        if confirmation != True:
            error = create_structured_validation_error(
                field="confirm_completion",
                value=confirmation,
                message="Setup completion requires explicit confirmation",
                examples={
                    "required_parameter": "confirm_completion must be True",
                    "usage": "complete_setup(confirm_completion=True)",
                    "purpose": "Prevents accidental setup completion without proper validation"
                }
            )
            return [TextContent(type="text", text=format_structured_error(error))]

        debug_info = []
        debug_info.append("🔍 **DEBUG: Starting complete_setup process**")

        try:
            # ROBUST APPROACH: Ensure auto-discovery completes with retry logic
            from ..config_store import get_config_store, get_config_value
            config_store = get_config_store()
            debug_info.append(f"✅ ConfigurationStore instance: {id(config_store)}")

            # Force auto-discovery completion with retry
            max_retries = 3
            debug_info.append(f"🔄 Starting auto-discovery with {max_retries} retries")

            for attempt in range(max_retries):
                debug_info.append(f"🔄 Attempt {attempt + 1}/{max_retries}")
                await config_store.get_configuration()

                debug_info.append(f"   - Discovery attempted: {config_store._discovery_attempted}")
                debug_info.append(f"   - Discovered config exists: {config_store._discovered_config is not None}")

                # Verify auto-discovery actually completed by checking discovered config
                if config_store._discovered_config and config_store._discovered_config.has_required_fields():
                    debug_info.append(f"✅ Auto-discovery completed successfully on attempt {attempt + 1}")
                    logger.info(f"✅ Auto-discovery completed successfully on attempt {attempt + 1}")
                    break

                if attempt < max_retries - 1:
                    debug_info.append(f"⚠️ Auto-discovery incomplete on attempt {attempt + 1}, retrying...")
                    logger.warning(f"⚠️ Auto-discovery incomplete on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(0.5)  # Brief delay before retry
                else:
                    debug_info.append("❌ Auto-discovery failed after all retries")
                    logger.error("❌ Auto-discovery failed after all retries")

            # First check if we have the required configuration
            required_fields = ["REVENIUM_API_KEY", "REVENIUM_TEAM_ID", "REVENIUM_TENANT_ID", "REVENIUM_OWNER_ID"]
            missing_fields = []

            debug_info.append("🔍 Checking required configuration fields:")
            for field in required_fields:
                value = get_config_value(field)
                if not value:
                    missing_fields.append(field)
                    debug_info.append(f"   - ❌ {field}: MISSING")
                else:
                    debug_info.append(f"   - ✅ {field}: {'SET (hidden)' if field == 'REVENIUM_API_KEY' else value}")
                logger.debug(f"Field {field}: {'SET (hidden)' if field == 'REVENIUM_API_KEY' and value else value or 'NONE'}")

            if missing_fields:
                debug_output = "\n".join(debug_info)
                return [TextContent(type="text", text=f"""# ⚠️ **Setup Incomplete**

Cannot complete setup because the following required configuration values are missing:

{chr(10).join(f'- **{field}**' for field in missing_fields)}

## 🔧 **How to Fix**

1. **Check Auto-Discovery**: Use `configuration_status(action='auto_discovery')` to verify auto-discovery is working
2. **Check API Connectivity**: Use `configuration_status(action='api_connectivity')` to test your API connection
3. **Manual Configuration**: Set missing environment variables if auto-discovery isn't working

**Auto-discovery should provide these values automatically.** If it's not working, there may be an issue with your API key or network connectivity.

**Try Again**: Once the missing values are available, run `complete_setup()` again.

---
## 🔍 **Debug Information**

{debug_output}
""")]

            debug_info.append("✅ All required fields available, proceeding with cache creation")

            from ..onboarding.detection_service import get_detection_service
            detection_service = get_detection_service()
            debug_info.append(f"✅ Detection service instance: {id(detection_service)}")

            debug_info.append("🔄 Calling mark_onboarding_completed()...")
            success = await detection_service.mark_onboarding_completed()
            debug_info.append(f"📝 Cache creation result: {success}")

            debug_output = "\n".join(debug_info)

            if success:
                return [TextContent(type="text", text=f"""# 🎉 **Setup Complete!**

✅ **Congratulations!** Your Revenium MCP server setup is now complete.

## **What's Next?**

You can now use all the powerful features of the Revenium MCP server:

- **📊 Product Management**: Create and manage your API products
- **👥 Customer Management**: Manage users, subscribers, and organizations
- **🔔 Alert Management**: Set up monitoring and notifications
- **📈 Metering Management**: Submit and track AI transaction data
- **🔗 Slack Integration**: Get real-time notifications in Slack

## **Getting Started**

Try these commands to explore your capabilities:
- `manage_alerts(action='create')` - Set up AI spending alerts to avoid surprise costs
- `verify_email_setup(action='update_email')` - Configure default email address to receive AI spending alerts
- `slack_setup_assistant(action='setup_status')` - Configure default Slack channel to receive AI spending alerts

**Welcome to Revenium!** 🚀

---
## 🔍 **Debug Information**

{debug_output}
""")]
            else:
                return [TextContent(type="text", text=f"""# ⚠️ **Setup Completion Issue**

There was an issue marking your setup as complete. This might be due to:

- Missing required configuration values
- Cache write permissions
- Network connectivity issues

**Recommendation**: Use `setup_checklist()` to verify all required components are configured properly.

---
## 🔍 **Debug Information**

{debug_output}
""")]
                
        except Exception as e:
            logger.error(f"Error completing setup: {e}")
            debug_info.append(f"❌ Exception occurred: {str(e)}")
            debug_output = "\n".join(debug_info)
            return [TextContent(type="text", text=f"""# **Setup Completion Error**

**Error**: {str(e)}

**Recommendation**: Try running `setup_checklist()` to diagnose any remaining configuration issues.

---
## **Debug Information**

{debug_output}
""")]
    
    async def _handle_help(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle help action - show available actions and usage examples."""
        logger.debug("Showing welcome setup help and available actions")
        
        help_text = """# Welcome and Setup Tool Help

## Available Actions

**show_welcome**
- Display welcome message and setup overview
- Usage: `welcome_and_setup(action="show_welcome")`
- Best for: First-time users or getting an overview

**setup_checklist**
- Show detailed setup completion status
- Usage: `welcome_and_setup(action="setup_checklist")`
- Best for: Checking what configuration items are completed

**environment_status**
- Display all environment variables with status
- Usage: `welcome_and_setup(action="environment_status")`
- Best for: Troubleshooting configuration issues

**next_steps**
- Get personalized recommendations based on current setup
- Usage: `welcome_and_setup(action="next_steps")`
- Best for: Finding out what to do next

**complete_setup**
- Mark onboarding as complete (requires confirmation)
- Usage: `welcome_and_setup(action="complete_setup", confirm_completion=True)`
- Best for: Finishing the setup process

**help**
- Show this help message
- Usage: `welcome_and_setup(action="help")`
- Best for: Learning about available actions

## Getting Started

1. Start with `show_welcome` for an overview
2. Use `setup_checklist` to see what needs configuration
3. Use `next_steps` for personalized guidance
4. Use `complete_setup` when ready to finish

## Optional Parameters

- `show_environment`: Whether to show environment details (true/false)
- `include_recommendations`: Whether to include recommendations (true/false)
"""
        
        return [TextContent(type="text", text=help_text)]
    
    def _build_welcome_message(self, onboarding_state, validation_result) -> str:
        """Build the main welcome message with streamlined experience when auto-discovery works."""
        is_first_time = onboarding_state.is_first_time
        setup_completion = onboarding_state.setup_completion

        # Check if auto-discovery has configured all required items
        auto_discovery_complete = (
            setup_completion.get('api_key_configured', False) and
            setup_completion.get('team_id_configured', False) and
            setup_completion.get('email_configured', False) and
            setup_completion.get('auto_discovery_working', False)
        )

        slack_configured = setup_completion.get('slack_configured', False)

        if is_first_time:
            welcome_header = "# **Welcome to Revenium MCP Server!**\n\n"

            if auto_discovery_complete:
                # STREAMLINED EXPERIENCE: Auto-discovery worked, focus on Slack only
                if slack_configured:
                    welcome_intro = """**Perfect!** Auto-discovery has configured everything automatically.

✅ **Your setup is complete and ready to use!**

"""
                    status_section = """## **Ready to Go!**

Auto-discovery found all your configuration:
- ✅ **API Key**: Configured automatically
- ✅ **Team ID**: Configured automatically
- ✅ **Email**: Configured automatically
- ✅ **Slack**: Configured and ready

**You're all set!** Your Revenium MCP server is fully configured.

"""
                    next_steps_section = """## 🎯 **What's Next?**

Start using your fully configured Revenium MCP server:
- `manage_products(action='list')` - View your products
- `manage_alerts(action='list')` - Check your alerts
- `manage_metering(action='get_capabilities')` - Explore AI transaction tracking

**Ready to complete onboarding?** Use `complete_setup()` to finish!
"""
                else:
                    welcome_intro = """👋 **Excellent!** Auto-discovery has configured everything automatically.

✅ **Almost ready!** Just one optional step remaining.

"""
                    status_section = """## 🎯 **One Step to Complete Setup**

Auto-discovery found all your required configuration:
- ✅ **API Key**: Configured automatically
- ✅ **Team ID**: Configured automatically
- ✅ **Email**: Configured automatically
- 📱 **Slack**: Optional - for real-time notifications

"""
                    next_steps_section = """## 🚀 **Choose Your Path**

**Option 1: Add Slack Notifications (Recommended)**
- `slack_setup_assistant(action='quick_setup')` - Set up real-time alerts

**Option 2: Skip Slack and Finish Setup**
- `complete_setup()` - Start using Revenium immediately

**Why Slack?** Get instant notifications when alerts trigger, perfect for team collaboration and mobile monitoring.
"""

                return welcome_header + welcome_intro + status_section + next_steps_section

            else:
                # TRADITIONAL EXPERIENCE: Auto-discovery didn't work, show detailed setup
                welcome_intro = """👋 **Hello!** This appears to be your first time using the Revenium MCP server.

Let's get you set up quickly and efficiently!

"""
        else:
            welcome_header = "# 🔧 **Revenium MCP Server Setup**\n\n"
            welcome_intro = """👋 **Welcome back!** Let's check your current setup status.

"""

        # Traditional detailed setup experience (fallback when auto-discovery doesn't work)
        overall_status = validation_result.summary.get('overall_status', False)

        # Configuration status
        if overall_status:
            status_section = """## ✅ **Configuration Status: READY**

Your Revenium MCP server is properly configured and ready to use!

"""
        else:
            status_section = """## ⚠️ **Configuration Status: NEEDS ATTENTION**

Some configuration items need your attention to ensure optimal functionality.

"""

        # Quick setup summary
        required_items = [
            ("API Key", setup_completion.get('api_key_configured', False)),
            ("Team ID", setup_completion.get('team_id_configured', False)),
            ("Email", setup_completion.get('email_configured', False)),
            ("Slack", setup_completion.get('slack_configured', False))
        ]

        setup_summary = "## 📋 **Quick Setup Summary**\n\n"
        for item, configured in required_items:
            status_icon = "✅" if configured else "⚠️"
            setup_summary += f"- {status_icon} **{item}**: {'Configured' if configured else 'Needs Setup'}\n"

        setup_summary += "\n"

        # Recommendations
        recommendations_section = "## 🎯 **Recommendations**\n\n"
        for i, rec in enumerate(onboarding_state.recommendations[:3], 1):
            recommendations_section += f"{i}. {rec}\n"

        recommendations_section += "\n"

        # Next steps
        next_steps_section = """## 🚀 **Quick Actions**

- `setup_checklist()` - See detailed setup status
- `environment_status()` - View all environment variables
- `slack_setup_assistant(action='quick_setup')` - Set up Slack notifications
- `next_steps()` - Get personalized recommendations

**Ready to get started?** Use any of the commands above!
"""

        return (welcome_header + welcome_intro + status_section +
                setup_summary + recommendations_section + next_steps_section)
    
    def _build_setup_checklist(self, onboarding_state, validation_result) -> str:
        """Build detailed setup checklist."""
        checklist = "# 📋 **Detailed Setup Checklist**\n\n"
        
        # Core requirements
        checklist += "## 🔑 **Core Requirements**\n\n"

        api_key_set = bool(get_config_value("REVENIUM_API_KEY"))
        team_id_set = bool(get_config_value("REVENIUM_TEAM_ID"))

        checklist += f"{'✅' if api_key_set else '❌'} **API Key**: {'Configured' if api_key_set else 'Required - Set REVENIUM_API_KEY'}\n"
        checklist += f"{'✅' if team_id_set else '❌'} **Team ID**: {'Configured' if team_id_set else 'Required - Set REVENIUM_TEAM_ID or use auto-discovery'}\n\n"

        # Optional but recommended
        checklist += "## 📧 **Recommended Setup**\n\n"

        email_set = bool(get_config_value("REVENIUM_DEFAULT_EMAIL"))
        slack_set = bool(get_config_value("REVENIUM_DEFAULT_SLACK_CONFIG_ID"))
        
        checklist += f"{'✅' if email_set else '📧'} **Email Notifications**: {'Configured' if email_set else 'Use verify_email_setup() to configure'}\n"
        slack_action = 'slack_setup_assistant(action="quick_setup") to configure'
        checklist += f"{'✅' if slack_set else '📱'} **Slack Integration**: {'Configured' if slack_set else f'Use {slack_action}'}\n\n"
        
        # System status
        checklist += "## 🔧 **System Status**\n\n"
        
        api_works = validation_result.api_connectivity.get('status') == 'success'
        auto_discovery_works = validation_result.summary.get('auto_discovery_works', False)
        
        checklist += f"{'✅' if api_works else '❌'} **API Connectivity**: {'Working' if api_works else 'Check API key and network'}\n"
        checklist += f"{'✅' if auto_discovery_works else '⚠️'} **Auto-Discovery**: {'Working' if auto_discovery_works else 'Manual configuration required'}\n\n"
        
        # Next steps
        if not api_key_set or not team_id_set:
            checklist += "## 🎯 **Next Steps**\n\n"
            checklist += "1. Configure required environment variables\n"
            checklist += "2. Use `environment_status()` to see all variables\n"
            checklist += "3. Run `setup_checklist()` again to verify\n"
        elif not email_set or not slack_set:
            checklist += "## 🎯 **Next Steps**\n\n"
            step_num = 1
            if not email_set:
                checklist += f"{step_num}. Set up email notifications for alerts\n"
                step_num += 1
            if not slack_set:
                checklist += f"{step_num}. Configure Slack integration for real-time updates\n"
                step_num += 1
            checklist += f"{step_num}. Use `complete_setup()` when ready\n"
        else:
            checklist += "## 🎉 **Ready to Go!**\n\n"
            checklist += "Your setup looks complete! Use `complete_setup()` to finish onboarding.\n"
        
        return checklist

    def _build_environment_status(self, validation_result) -> str:
        """Build complete environment variable status display."""
        env_status = "# 🔍 **Complete Environment Variable Status**\n\n"
        env_status += f"**Generated**: {validation_result.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"

        # Group variables by category
        variables_by_category = {}
        for var_name, var_status in validation_result.variables.items():
            category = var_status.category
            if category not in variables_by_category:
                variables_by_category[category] = []
            variables_by_category[category].append((var_name, var_status))

        # Display each category
        for category, vars_list in variables_by_category.items():
            env_status += f"## 📂 **{category}**\n\n"

            for var_name, var_status in vars_list:
                status_icon = "✅" if var_status.is_set else "❌"
                required_text = " (Required)" if var_status.required else ""
                auto_disc_text = " (Auto-discoverable)" if var_status.auto_discoverable else ""

                env_status += f"**{var_name}**{required_text}{auto_disc_text}\n"
                env_status += f"- Status: {status_icon} {var_status.display_value}\n"
                env_status += f"- Description: {var_status.description}\n\n"

        # Add summary section using same logic as debug_auto_discovery
        env_status += "## 📊 **Summary**\n\n"
        summary = validation_result.summary

        env_status += f"- **API Key Available**: {'✅ YES' if summary.get('api_key_available') else '❌ NO'}\n"
        env_status += f"- **Auto-Discovery Works**: {'✅ YES' if summary.get('auto_discovery_works') else '❌ NO'}\n"
        env_status += f"- **Required Fields Discovered**: {'✅ YES' if summary.get('required_fields_discovered') else '❌ NO'}\n"
        env_status += f"- **Email Discovered**: {'✅ YES' if summary.get('email_discovered') else '❌ NO'}\n"
        env_status += f"- **Direct API Works**: {'✅ YES' if summary.get('direct_api_works') else '❌ NO'}\n"
        env_status += f"- **Auth Config Works**: {'✅ YES' if summary.get('auth_config_works') else '❌ NO'}\n"
        env_status += f"- **Overall Status**: {'✅ WORKING' if summary.get('overall_status') else '❌ NEEDS ATTENTION'}\n\n"

        env_status += f"**Configuration Method**: {summary.get('configuration_method', 'Unknown')}\n"

        return env_status

    def _build_next_steps(self, onboarding_state) -> str:
        """Build personalized next steps recommendations with streamlined experience."""
        setup_completion = onboarding_state.setup_completion

        # Check if auto-discovery has configured all required items
        auto_discovery_complete = (
            setup_completion.get('api_key_configured', False) and
            setup_completion.get('team_id_configured', False) and
            setup_completion.get('email_configured', False) and
            setup_completion.get('auto_discovery_working', False)
        )

        slack_configured = setup_completion.get('slack_configured', False)

        if auto_discovery_complete:
            # STREAMLINED EXPERIENCE: Auto-discovery worked
            if slack_configured:
                return """# 🎉 **Setup Complete!**

**Congratulations!** Auto-discovery has configured everything and Slack is ready.

## 🚀 **You're Ready to Go!**

Your Revenium MCP server is fully configured. Start using these powerful features:

- **📊 Product Management**: `manage_products(action='list')` - View and manage your API products
- **🔔 Alert Management**: `manage_alerts(action='list')` - Monitor usage and set up notifications
- **📈 Metering Management**: `manage_metering(action='get_capabilities')` - Track AI transactions
- **👥 Customer Management**: `manage_customers(action='list')` - Manage subscribers and organizations

## 🎯 **Finish Onboarding**

Ready to complete setup? Use `complete_setup()` to mark onboarding as complete!
"""
            else:
                return """# 🎯 **Almost Done!**

**Excellent!** Auto-discovery has configured all required settings automatically.

## 🚀 **Choose Your Path**

**Option 1: Add Slack Notifications (Recommended)**
```
slack_setup_assistant(action='quick_setup')
```
- Get real-time alerts delivered to your team
- Perfect for mobile monitoring and team collaboration
- Takes just 2 minutes to set up

**Option 2: Skip Slack and Finish Setup**
```
complete_setup()
```
- Start using Revenium immediately
- You can always add Slack later

## 💡 **Why Slack?**

Slack notifications provide instant alerts when:
- Usage thresholds are exceeded
- API errors spike
- New customers subscribe
- System issues need attention

**Recommended**: Set up Slack now for the best monitoring experience!
"""

        # TRADITIONAL EXPERIENCE: Auto-discovery didn't work, show detailed steps
        next_steps = "# 🎯 **Personalized Next Steps**\n\n"

        # Prioritized recommendations
        steps = []

        if not setup_completion.get('api_key_configured', False):
            steps.append({
                "priority": 1,
                "title": "Configure API Key",
                "description": "Set your REVENIUM_API_KEY environment variable",
                "action": "Set environment variable or use configuration file",
                "urgency": "🔴 Critical"
            })

        if not setup_completion.get('team_id_configured', False):
            steps.append({
                "priority": 1,
                "title": "Configure Team ID",
                "description": "Set REVENIUM_TEAM_ID or enable auto-discovery",
                "action": "Set environment variable or let system auto-discover",
                "urgency": "🔴 Critical"
            })

        if not setup_completion.get('email_configured', False):
            steps.append({
                "priority": 2,
                "title": "Set Up Email Notifications",
                "description": "Configure your notification email address",
                "action": "Use verify_email_setup() tool",
                "urgency": "🟡 Recommended"
            })

        if not setup_completion.get('slack_configured', False):
            steps.append({
                "priority": 2,
                "title": "Configure Slack Integration",
                "description": "Set up Slack for real-time notifications",
                "action": "Use slack_setup_assistant(action='quick_setup')",
                "urgency": "🟡 Recommended"
            })

        if not setup_completion.get('auto_discovery_working', False):
            steps.append({
                "priority": 3,
                "title": "Enable Auto-Discovery",
                "description": "Simplify configuration with automatic value discovery",
                "action": "Ensure API connectivity and run validation",
                "urgency": "🟢 Optional"
            })

        # Sort by priority
        steps.sort(key=lambda x: x['priority'])

        if not steps:
            next_steps += "🎉 **Congratulations!** Your setup is complete.\n\n"
            next_steps += "## 🚀 **Ready to Use**\n\n"
            next_steps += "You can now:\n"
            next_steps += "- Manage products with `manage_products()`\n"
            next_steps += "- Set up alerts with `manage_alerts()`\n"
            next_steps += "- Submit metering data with `manage_metering()`\n"
            next_steps += "- Explore all capabilities with tool discovery\n\n"
            next_steps += "Use `complete_setup()` to finish onboarding!"
        else:
            for i, step in enumerate(steps, 1):
                next_steps += f"## {i}. {step['urgency']} **{step['title']}**\n\n"
                next_steps += f"**Description**: {step['description']}\n\n"
                next_steps += f"**Action**: {step['action']}\n\n"

        return next_steps

    # Metadata Provider Implementation
    async def _get_tool_capabilities(self) -> List[ToolCapability]:
        """Get welcome setup tool capabilities."""
        return [
            ToolCapability(
                name="Welcome Message",
                description="Display welcome message and setup overview",
                parameters={"action": "show_welcome"}
            ),
            ToolCapability(
                name="Setup Checklist",
                description="Show detailed setup completion status",
                parameters={"action": "setup_checklist"}
            ),
            ToolCapability(
                name="Environment Status",
                description="Display all environment variables with complete status",
                parameters={"action": "environment_status"}
            ),
            ToolCapability(
                name="Next Steps",
                description="Get personalized setup recommendations",
                parameters={"action": "next_steps"}
            ),
            ToolCapability(
                name="Complete Setup",
                description="Mark onboarding as complete",
                parameters={"action": "complete_setup"}
            )
        ]

    async def _get_supported_actions(self) -> List[str]:
        """Get supported actions."""
        return [
            "show_welcome",
            "setup_checklist",
            "environment_status",
            "next_steps",
            "complete_setup",
            "help",
            "get_actions"
        ]

    async def _get_quick_start_guide(self) -> List[str]:
        """Get quick start guide."""
        return [
            "Start with show_welcome() to see your setup status",
            "Use setup_checklist() for detailed configuration status",
            "Check environment_status() to see all variables",
            "Get next_steps() for personalized recommendations",
            "Use complete_setup() when configuration is ready"
        ]

    async def _get_common_use_cases(self) -> List[str]:
        """Get common use cases."""
        return [
            "First-time user onboarding and welcome",
            "Configuration status checking and validation",
            "Environment variable troubleshooting",
            "Setup completion verification",
            "Personalized setup guidance"
        ]

    async def _handle_get_examples(self, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get_examples action - return usage examples."""
        examples = """# **Welcome and Setup Examples**

## **Show Welcome Message**
```json
{
  "action": "show_welcome"
}
```
**Purpose**: Display welcome message and setup overview with current status

## **Setup Checklist**
```json
{
  "action": "setup_checklist"
}
```
**Purpose**: Show detailed setup completion status and configuration items

## **Environment Status**
```json
{
  "action": "environment_status"
}
```
**Purpose**: Display all environment variables with complete status information

## **Next Steps**
```json
{
  "action": "next_steps"
}
```
**Purpose**: Get personalized setup recommendations based on current configuration

## **Complete Setup**
```json
{
  "action": "complete_setup",
  "confirm_completion": true
}
```
**Purpose**: Mark onboarding as complete (requires confirmation)

## **Help and Actions**
```json
{
  "action": "help"
}
```
**Purpose**: Show available actions and usage examples

## **Common Workflows**

### **First-Time User Experience**
1. Start with `show_welcome()` to see current setup status
2. Use `setup_checklist()` for detailed configuration review
3. Follow `next_steps()` for personalized guidance
4. Use `complete_setup()` when ready to finish onboarding

### **Configuration Troubleshooting**
1. Check `environment_status()` to see all variables
2. Use `setup_checklist()` to identify missing items
3. Follow `next_steps()` for specific recommendations
4. Return to `show_welcome()` to verify progress

### **Setup Verification**
1. Use `setup_checklist()` to verify all requirements
2. Check `next_steps()` for any remaining items
3. Use `complete_setup()` to finalize onboarding
"""
        return [TextContent(type="text", text=examples)]

    async def _handle_get_capabilities(self, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Handle get_capabilities action - return capabilities overview."""
        capabilities = """# **Welcome and Setup Capabilities**

## **Purpose**
Welcome and initial setup guidance with comprehensive onboarding integration.

## **Available Actions**

1. **show_welcome** - ✅ **MAIN ENTRY POINT**
   - Display welcome message and setup overview
   - Shows current configuration status and progress

2. **setup_checklist** - ✅ **DETAILED STATUS**
   - Show detailed setup completion status
   - Configuration item verification and validation

3. **environment_status** - ✅ **DIAGNOSTIC**
   - Display all environment variables with complete status
   - Comprehensive environment configuration review

4. **next_steps** - ✅ **GUIDANCE**
   - Get personalized setup recommendations
   - Context-aware guidance based on current state

5. **complete_setup** - ✅ **COMPLETION**
   - Mark onboarding as complete (requires confirmation)
   - Finalize setup process and transition to normal usage

6. **help** - ✅ **ASSISTANCE**
   - Show available actions and usage examples
   - Comprehensive action documentation

7. **get_capabilities** - ✅ **DISCOVERY**
   - Shows current implementation status and available actions

8. **get_examples** - ✅ **EXAMPLES**
   - Shows usage examples for all available actions

## **Key Features**
- **Comprehensive Onboarding** - Complete first-time user experience
- **Configuration Validation** - Real-time setup status checking
- **Environment Analysis** - Detailed environment variable review
- **Personalized Guidance** - Context-aware recommendations
- **Setup Completion** - Formal onboarding completion process
- **Troubleshooting Support** - Diagnostic and resolution guidance

## **Integration**
- Uses existing validation infrastructure for consistency
- Integrates with configuration status and environment checking
- Connects with Slack setup and email verification tools
- Provides foundation for complete system onboarding
"""
        return [TextContent(type="text", text=capabilities)]


# Create welcome setup instance
# Module-level instantiation removed to prevent UCM warnings during import
# welcome_setup = WelcomeSetup(ucm_helper=None)
