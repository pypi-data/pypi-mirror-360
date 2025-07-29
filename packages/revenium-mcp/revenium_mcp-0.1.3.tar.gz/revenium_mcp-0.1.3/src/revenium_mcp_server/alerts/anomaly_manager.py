"""Anomaly management functionality for Revenium MCP server.

This module provides CRUD operations and management functionality
for AI anomalies in the Revenium platform.
"""

import json
from typing import Any, Dict, List, Optional, Union
from loguru import logger

from mcp.types import TextContent, ImageContent, EmbeddedResource

from ..client import ReveniumClient
from ..error_handlers import (
    handle_alert_tool_errors, validate_anomaly_id, validate_pagination_params
)
from ..exceptions import ValidationError
from ..validators import InputValidator


class AnomalyManager:
    """Manages AI anomaly CRUD operations and related functionality."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the anomaly manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
    
    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for anomaly status."""
        # Return empty string - no decorative emojis for status
        return ""
    
    def _format_frequency_info(self, period_duration: str) -> str:
        """Format frequency information for display."""
        frequency_map = {
            "ONE_MINUTE": "Every minute",
            "FIVE_MINUTES": "Every 5 minutes",
            "TEN_MINUTES": "Every 10 minutes",
            "FIFTEEN_MINUTES": "Every 15 minutes",
            "THIRTY_MINUTES": "Every 30 minutes",
            "ONE_HOUR": "Every hour",
            "TWO_HOURS": "Every 2 hours",
            "SIX_HOURS": "Every 6 hours",
            "TWELVE_HOURS": "Every 12 hours",
            "ONE_DAY": "Daily",
            "THREE_DAYS": "Every 3 days",
            "SEVEN_DAYS": "Weekly",
            "FOURTEEN_DAYS": "Every 2 weeks",
            "THIRTY_DAYS": "Monthly"
        }
        return frequency_map.get(period_duration, period_duration)
    
    def _format_trigger_duration_info(self, trigger_duration: str) -> str:
        """Format trigger duration information for display."""
        duration_map = {
            "FIVE_MINUTES": "5 minutes",
            "TEN_MINUTES": "10 minutes",
            "FIFTEEN_MINUTES": "15 minutes",
            "THIRTY_MINUTES": "30 minutes",
            "ONE_HOUR": "1 hour",
            "TWO_HOURS": "2 hours",
            "SIX_HOURS": "6 hours",
            "TWELVE_HOURS": "12 hours",
            "ONE_DAY": "1 day",
            "THREE_DAYS": "3 days",
            "SEVEN_DAYS": "1 week",
            "FOURTEEN_DAYS": "2 weeks",
            "THIRTY_DAYS": "1 month"
        }
        return duration_map.get(trigger_duration, trigger_duration)
    
    def _process_advanced_configuration(self, anomaly_data: Dict[str, Any], validated_data: Dict[str, Any]) -> None:
        """Process advanced configuration fields."""
        # Handle notification addresses
        if "notification_addresses" in anomaly_data:
            addresses = anomaly_data["notification_addresses"]
            if addresses and isinstance(addresses, list):
                validated_data["notification_addresses"] = addresses

        # Handle filters
        if "filters" in anomaly_data:
            filters = anomaly_data["filters"]
            if filters and isinstance(filters, list):
                validated_data["filters"] = filters

        # Handle alert type
        if "alert_type" in anomaly_data:
            validated_data["alert_type"] = str(anomaly_data["alert_type"])
        elif "alertType" in anomaly_data:
            validated_data["alert_type"] = str(anomaly_data["alertType"])
    
    @handle_alert_tool_errors("list_anomalies")
    async def list_anomalies(
        self, 
        client: ReveniumClient, 
        page: int = 0, 
        size: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """List AI anomalies with pagination.
        
        Args:
            client: Revenium API client
            page: Page number (0-based)
            size: Page size
            filters: Optional filters
            
        Returns:
            Formatted response with anomaly list
        """
        logger.info(f"Listing anomalies: page={page}, size={size}")
        
        # Call the client method directly
        response = await client.get_anomalies(page=page, size=size, **(filters or {}))
        
        # Extract anomalies from response
        anomalies = client._extract_embedded_data(response)
        page_info = client._extract_pagination_info(response)

        # Handle empty results with proper pagination context
        if not anomalies:
            total_elements = page_info.get('totalElements', 0)
            total_pages = page_info.get('totalPages', 1)
            current_page = page + 1

            if total_elements == 0:
                # No anomalies exist in the system
                return [TextContent(
                    type="text",
                    text="📋 **No AI anomalies found**\n\nNo anomalies match your criteria."
                )]
            elif current_page > total_pages:
                # Page is beyond available results
                return [TextContent(
                    type="text",
                    text=(
                        f"📋 **Page {current_page} is beyond available results**\n\n"
                        f"**Total anomalies:** {total_elements}\n"
                        f"**Available pages:** 1-{total_pages}\n"
                        f"**Requested page:** {current_page}\n\n"
                        f"Please use a page number between 1 and {total_pages}."
                    )
                )]
            else:
                # This shouldn't happen, but handle gracefully
                return [TextContent(
                    type="text",
                    text=(
                        f"📋 **No results on page {current_page}**\n\n"
                        f"**Total anomalies:** {total_elements}\n"
                        f"**Total pages:** {total_pages}\n\n"
                        f"This page appears to be empty. Please try a different page."
                    )
                )]
        
        # Format the response
        anomaly_list = []
        for anomaly in anomalies:
            status_emoji = "🟢" if anomaly.get("enabled", True) else "🔴"
            enabled_status = "✅ Enabled" if anomaly.get("enabled", True) else "❌ Disabled"

            # Generate notification summary
            notification_summary = self._format_notification_summary(anomaly)

            # Always show filter information - either specific filters or "No filters"
            filters = anomaly.get('filters', [])
            filter_summary = ""
            if filters:
                filter_count = len(filters)
                if filter_count == 1:
                    filter_item = filters[0]
                    dimension = filter_item.get('dimension', 'N/A')
                    operator = filter_item.get('operator', 'CONTAINS')
                    value = filter_item.get('value', 'N/A')
                    filter_summary = f"\n  • Filter: {dimension} {operator} '{value}'"
                else:
                    filter_summary = f"\n  • Filters: {filter_count} applied"
            else:
                filter_summary = "\n  • Scope: Global (no filters)"

            anomaly_text = (
                f"**{anomaly.get('name', 'Unnamed')}** {status_emoji}\n"
                f"  • ID: `{anomaly.get('id', 'N/A')}`\n"
                f"  • Type: {anomaly.get('alertType', 'N/A')}\n"
                f"  • Metric: {anomaly.get('metricType', 'N/A')}\n"
                f"  • {enabled_status}\n"
                f"  • Threshold: {anomaly.get('threshold', 'N/A')}\n"
                f"  • Created: {(anomaly.get('createdAt') or anomaly.get('created', 'N/A'))[:10] if (anomaly.get('createdAt') or anomaly.get('created')) else 'N/A'}"
                f"{filter_summary}\n"
                f"  • Notifications: {notification_summary}"
            )
            anomaly_list.append(anomaly_text)
        
        # Create pagination info
        total_pages = page_info.get('totalPages', 1)
        current_page = page + 1
        total_elements = page_info.get('totalElements', len(anomalies))
        
        result_text = (
            f"📋 **AI Anomalies** (Page {current_page} of {total_pages})\n\n"
            f"💡 **Note**: These are alert definitions/rules. To see triggered alert events, use `resource_type=\"alerts\"` with `action=\"list\"`\n\n"
            f"Found {len(anomalies)} anomalies (Total: {total_elements})\n\n" +
            "\n\n".join(anomaly_list)
        )
        
        return [TextContent(type="text", text=result_text)]
    
    @handle_alert_tool_errors("get_anomaly")
    async def get_anomaly(
        self, 
        client: ReveniumClient, 
        anomaly_id: str
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get a specific AI anomaly by ID.
        
        Args:
            client: Revenium API client
            anomaly_id: ID of the anomaly to retrieve
            
        Returns:
            Formatted response with anomaly details
        """
        # Validate anomaly ID
        anomaly_id = validate_anomaly_id(anomaly_id)
        
        logger.info(f"Getting anomaly: {anomaly_id}")
        
        # Call the API client method
        anomaly = await client.get_anomaly_by_id(anomaly_id)
        
        # Format the response
        status_emoji = "🟢" if anomaly.get("status") == "active" else "🔴"
        enabled_status = "✅ Enabled" if anomaly.get("enabled", True) else "❌ Disabled"
        
        detection_rules = anomaly.get("detection_rules", [])
        rules_text = ""
        if detection_rules:
            rules_list = []
            for i, rule in enumerate(detection_rules, 1):
                rules_list.append(
                    f"  {i}. **{rule.get('rule_type', 'unknown')}** rule\n"
                    f"     • Metric: {rule.get('metric', 'N/A')}\n"
                    f"     • Operator: {rule.get('operator', 'N/A')}\n"
                    f"     • Value: {rule.get('value', 'N/A')}"
                )
            rules_text = "\n\n**Detection Rules:**\n" + "\n\n".join(rules_list)
        
        thresholds = anomaly.get("thresholds", {})
        thresholds_text = ""
        if thresholds:
            threshold_list = [f"  • {k}: {v}" for k, v in thresholds.items()]
            thresholds_text = "\n\n**Thresholds:**\n" + "\n".join(threshold_list)
        
        # Add filter information if available
        filters = anomaly.get('filters', [])
        filters_text = ""
        if filters:
            filter_list = []
            for filter_item in filters:
                dimension = filter_item.get('dimension', 'N/A')
                operator = filter_item.get('operator', 'N/A')
                value = filter_item.get('value', 'N/A')
                filter_list.append(f"  • {dimension} {operator} '{value}'")
            filters_text = "\n\n**Filters Applied:**\n" + "\n".join(filter_list)

        result_text = (
            f"🔍 **AI Anomaly Details** {status_emoji}\n\n"
            f"**Name:** {anomaly.get('name', 'Unnamed')}\n"
            f"**ID:** `{anomaly.get('id', 'N/A')}`\n"
            f"**Status:** {anomaly.get('enabled', True) and 'Enabled' or 'Disabled'}\n"
            f"**State:** {enabled_status}\n"
            f"**Description:** {anomaly.get('description', 'No description')}\n"
            f"**Created:** {anomaly.get('createdAt', anomaly.get('created', 'N/A'))}\n"
            f"**Updated:** {anomaly.get('updatedAt', anomaly.get('updated', 'N/A'))}"
            f"{rules_text}"
            f"{thresholds_text}"
            f"{filters_text}"
        )

        # Add notification configuration display
        notification_text = await self._format_notification_configuration(client, anomaly)
        result_text += notification_text

        return [TextContent(type="text", text=result_text)]
    
    @handle_alert_tool_errors("create_anomaly")
    async def create_anomaly(
        self, 
        client: ReveniumClient, 
        anomaly_data: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Create a new AI anomaly with comprehensive validation.
        
        Args:
            client: Revenium API client
            anomaly_data: Anomaly configuration data
            
        Returns:
            Formatted response with created anomaly details
        """
        if not isinstance(anomaly_data, dict):
            raise ValidationError(
                message="anomaly_data must be a dictionary",
                field="anomaly_data",
                value=type(anomaly_data).__name__,
                expected="Dictionary with anomaly fields"
            )
        
        logger.info(f"Creating anomaly: {anomaly_data.get('name', 'Unnamed')}")
        
        # Apply comprehensive validation and sanitization
        validated_data = {}
        
        # Validate and sanitize each field
        if "name" in anomaly_data:
            validated_data["name"] = InputValidator.validate_anomaly_name(anomaly_data["name"])
        else:
            raise ValidationError(
                message="Anomaly name is required",
                field="name",
                expected="Non-empty string"
            )
        
        if "description" in anomaly_data:
            validated_data["description"] = InputValidator.validate_description(anomaly_data["description"])
        
        if "tags" in anomaly_data:
            validated_data["tags"] = InputValidator.validate_tags(anomaly_data["tags"])
        
        # Handle both detection_rules format AND direct API format
        if "detection_rules" in anomaly_data:
            # User provided detection_rules format - validate and convert
            if not anomaly_data["detection_rules"]:
                raise ValidationError(
                    message="At least one detection rule is required",
                    field="detection_rules",
                    expected="List with at least one detection rule"
                )
            validated_data["detection_rules"] = [
                InputValidator.validate_detection_rule(rule)
                for rule in anomaly_data["detection_rules"]
            ]
        elif self._has_direct_api_format(anomaly_data):
            # User provided direct API format - validate and use as-is
            validated_data.update(self._validate_direct_api_format(anomaly_data))
        else:
            raise ValidationError(
                message="Either detection_rules or direct API format (alertType, metricType, operatorType, threshold) is required",
                field="anomaly_data",
                expected="Detection rules list OR direct API format fields",
                suggestion="Use detection_rules for complex rules, or provide alertType, metricType, operatorType, threshold for simple alerts"
            )
        
        # Thresholds are optional in the new API format (extracted from detection rules)
        if "thresholds" in anomaly_data:
            validated_data["thresholds"] = InputValidator.validate_thresholds(anomaly_data["thresholds"])
        
        # Handle advanced configuration fields
        self._process_advanced_configuration(anomaly_data, validated_data)
        
        # Copy other basic fields with validation
        for field in ["status", "enabled", "team_id", "notification_settings", "metadata"]:
            if field in anomaly_data:
                if field == "team_id" and not anomaly_data[field]:
                    raise ValidationError(
                        message="Team ID is required",
                        field="team_id",
                        expected="Non-empty string"
                    )
                validated_data[field] = anomaly_data[field]
        
        # Convert to API format (only if we have detection_rules, otherwise use direct format)
        if "detection_rules" in validated_data:
            try:
                api_data = InputValidator.convert_to_api_format(validated_data)
            except Exception as e:
                raise ValidationError(
                    message=f"Failed to convert to API format: {str(e)}",
                    field="anomaly_data",
                    expected="Valid anomaly data structure"
                )
        else:
            # Direct API format - use validated data as-is, just add required fields
            api_data = validated_data.copy()

            # Ensure required API fields are present
            if "label" not in api_data and "name" in validated_data:
                api_data["label"] = validated_data["name"]
            if "teamId" not in api_data:
                api_data["teamId"] = client.team_id

            # Set defaults for optional fields if not provided
            api_data.setdefault("enabled", True)
            api_data.setdefault("isPercentage", False)
            api_data.setdefault("notificationAddresses", [])
            api_data.setdefault("slackConfigurations", [])
            api_data.setdefault("triggerAfterPersistsDuration", "")
            api_data.setdefault("filters", [])
        
        # Call the API client method
        created_anomaly = await client.create_anomaly(api_data)
        
        # Format the enhanced response
        result_text = (
            f"✅ **AI Anomaly Created Successfully**\n\n"
            f"**Name:** {created_anomaly.get('name', 'Unnamed')}\n"
            f"**ID:** `{created_anomaly.get('id', 'N/A')}`\n"
            f"**Alert Type:** {created_anomaly.get('alertType', 'N/A')}\n"
            f"**Metric Type:** {created_anomaly.get('metricType', 'N/A')}\n"
            f"**Operator:** {created_anomaly.get('operatorType', 'N/A')}\n"
            f"**Threshold:** {created_anomaly.get('threshold', 'N/A')}\n"
            f"**Check Frequency:** {created_anomaly.get('periodDuration', 'N/A')}\n"
            f"**Enabled:** {'Yes' if created_anomaly.get('enabled', True) else 'No'}\n"
            f"**Created:** {created_anomaly.get('createdAt', created_anomaly.get('created', 'N/A'))}"
        )
        
        # Add frequency information if available
        period_duration = created_anomaly.get('periodDuration')
        if period_duration:
            frequency_info = self._format_frequency_info(str(period_duration))
            result_text += f"\n\n**Frequency Details:**\n{frequency_info}"
        
        # Add trigger duration if available
        trigger_duration = created_anomaly.get('triggerAfterPersistsDuration')
        if trigger_duration:
            trigger_info = self._format_trigger_duration_info(str(trigger_duration))
            result_text += f"\n**Trigger Duration:** {trigger_info}"

        # Add complete notification configuration display
        notification_text = await self._format_notification_configuration(client, created_anomaly)
        result_text += notification_text

        # Add filter information if available
        filters = created_anomaly.get('filters', [])
        if filters:
            result_text += f"\n\n**Filters Applied:**"
            for filter_item in filters:
                dimension = filter_item.get('dimension', 'N/A')
                operator = filter_item.get('operator', 'N/A')
                value = filter_item.get('value', 'N/A')
                result_text += f"\n  • {dimension} {operator} '{value}'"

        return [TextContent(type="text", text=result_text)]

    @handle_alert_tool_errors("update_anomaly")
    async def update_anomaly(
        self,
        client: ReveniumClient,
        anomaly_id: str,
        update_data: Dict[str, Any]
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Update an existing AI anomaly.

        Args:
            client: Revenium API client
            anomaly_id: ID of the anomaly to update
            update_data: Data to update

        Returns:
            Formatted response with updated anomaly details
        """
        # Validate anomaly ID
        anomaly_id = validate_anomaly_id(anomaly_id)

        if not isinstance(update_data, dict):
            raise ValidationError(
                message="update_data must be a dictionary",
                field="update_data",
                value=type(update_data).__name__,
                expected="Dictionary with update fields"
            )

        logger.info(f"Updating anomaly: {anomaly_id}")

        # Get current anomaly data first (like enable/disable operations do)
        current_anomaly = await client.get_anomaly_by_id(str(anomaly_id))

        # Start with current data and apply updates
        merged_data = current_anomaly.copy()

        # Handle field name conversions for user-friendly field names
        converted_updates = {}
        for key, value in update_data.items():
            if key == "email":
                # Convert 'email' to 'notificationAddresses'
                if isinstance(value, str):
                    converted_updates["notificationAddresses"] = [value]
                elif isinstance(value, list):
                    converted_updates["notificationAddresses"] = value
                else:
                    converted_updates["notificationAddresses"] = [str(value)]
            elif key == "notification_addresses":
                # Convert 'notification_addresses' to 'notificationAddresses'
                converted_updates["notificationAddresses"] = value
            elif key == "slackConfigId" or key == "slack_config_id":
                # Convert 'slackConfigId' or 'slack_config_id' to 'slackConfigurations' array
                if isinstance(value, str):
                    converted_updates["slackConfigurations"] = [value]
                elif isinstance(value, list):
                    converted_updates["slackConfigurations"] = value
                else:
                    converted_updates["slackConfigurations"] = [str(value)]
            elif key == "slack_configurations":
                # Convert 'slack_configurations' to 'slackConfigurations'
                converted_updates["slackConfigurations"] = value
            else:
                # Pass through other fields as-is
                converted_updates[key] = value

        # Apply the converted updates to the current data
        merged_data.update(converted_updates)

        # Call the API client method with merged data
        updated_anomaly = await client.update_anomaly(anomaly_id, merged_data)

        result_text = (
            f"✅ **AI Anomaly Updated Successfully**\n\n"
            f"**Name:** {updated_anomaly.get('name', 'Unnamed')}\n"
            f"**ID:** `{updated_anomaly.get('id', 'N/A')}`\n"
            f"**Status:** {updated_anomaly.get('enabled', True) and 'Enabled' or 'Disabled'}\n"
            f"**Updated:** {updated_anomaly.get('updatedAt', updated_anomaly.get('updated', 'N/A'))}"
        )

        # Always show current notification configuration (not conditional)
        notification_text = await self._format_notification_configuration(client, updated_anomaly)
        result_text += notification_text

        return [TextContent(type="text", text=result_text)]

    @handle_alert_tool_errors("delete_anomaly")
    async def delete_anomaly(
        self,
        client: ReveniumClient,
        anomaly_id: str
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Delete an AI anomaly.

        Args:
            client: Revenium API client
            anomaly_id: ID of the anomaly to delete

        Returns:
            Formatted response confirming deletion
        """
        # Validate anomaly ID
        anomaly_id = validate_anomaly_id(anomaly_id)

        logger.info(f"Deleting anomaly: {anomaly_id}")

        # Call the API client method
        await client.delete_anomaly(anomaly_id)

        result_text = (
            f"✅ **AI Anomaly Deleted Successfully**\n\n"
            f"**ID:** `{anomaly_id}`\n"
            f"The anomaly has been permanently removed."
        )

        return [TextContent(type="text", text=result_text)]

    @handle_alert_tool_errors("clear_all_anomalies")
    async def clear_all_anomalies(
        self,
        client: ReveniumClient
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Clear all AI anomalies.

        Args:
            client: Revenium API client

        Returns:
            Formatted response confirming clearing
        """
        logger.info("Clearing all anomalies")

        # Get all anomalies first
        response = await client.get_anomalies(page=0, size=1000)
        anomalies = client._extract_embedded_data(response)

        if not anomalies:
            return [TextContent(
                type="text",
                text="📋 **No anomalies to clear**\n\nThere are no anomalies in the system."
            )]

        # Delete each anomaly
        deleted_count = 0
        for anomaly in anomalies:
            try:
                anomaly_id = anomaly.get('id')
                if anomaly_id:
                    await client.delete_anomaly(anomaly_id)
                    deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete anomaly {anomaly.get('id')}: {e}")

        result_text = (
            f"✅ **Anomalies Cleared Successfully**\n\n"
            f"**Deleted:** {deleted_count} anomalies\n"
            f"**Total Found:** {len(anomalies)}"
        )

        if deleted_count < len(anomalies):
            result_text += f"\n\n⚠️ **Warning:** {len(anomalies) - deleted_count} anomalies could not be deleted."

        return [TextContent(type="text", text=result_text)]

    @handle_alert_tool_errors("get_anomaly_metrics")
    async def get_anomaly_metrics(
        self,
        client: ReveniumClient,
        anomaly_id: str
    ) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Get metrics for a specific anomaly.

        Args:
            client: Revenium API client
            anomaly_id: ID of the anomaly

        Returns:
            Formatted response with anomaly metrics
        """
        # Validate anomaly ID
        anomaly_id = validate_anomaly_id(anomaly_id)

        logger.info(f"Getting metrics for anomaly: {anomaly_id}")

        # Call the API client method
        metrics = await client.get_anomaly_metrics(anomaly_id)

        result_text = (
            f"📊 **Anomaly Metrics**\n\n"
            f"**Anomaly ID:** `{anomaly_id}`\n"
            f"**Metrics:** {json.dumps(metrics, indent=2) if metrics else 'No metrics available'}"
        )

        return [TextContent(type="text", text=result_text)]

    def _format_notification_summary(self, anomaly_data: Dict[str, Any]) -> str:
        """Format a concise notification summary for list views.

        Args:
            anomaly_data: Anomaly data containing notification configuration

        Returns:
            Concise notification summary string
        """
        summary_parts = []

        # Count email notifications
        email_addresses = anomaly_data.get('notificationAddresses', [])
        if email_addresses:
            email_count = len(email_addresses)
            summary_parts.append(f"{email_count} email{'s' if email_count != 1 else ''}")

        # Count Slack configurations
        slack_config_ids = anomaly_data.get('slackConfigurations', [])
        if slack_config_ids:
            slack_count = len(slack_config_ids)
            summary_parts.append(f"{slack_count} Slack")

        # Return summary or "No notifications"
        if summary_parts:
            return ", ".join(summary_parts)
        else:
            return "No notifications"

    async def _format_notification_configuration(
        self,
        client: ReveniumClient,
        anomaly_data: Dict[str, Any]
    ) -> str:
        """Format notification configuration display for anomaly responses.

        Args:
            client: Revenium API client for fetching Slack configuration details
            anomaly_data: Anomaly data containing notification configuration

        Returns:
            Formatted notification configuration text
        """
        notification_parts = []

        # Extract email notifications
        email_addresses = anomaly_data.get('notificationAddresses', [])
        if email_addresses:
            email_list = ', '.join(email_addresses)
            notification_parts.append(f"• **Email Notifications:** {email_list}")

        # Extract and format Slack configurations
        slack_config_ids = anomaly_data.get('slackConfigurations', [])
        if slack_config_ids:
            slack_details = []
            for config_id in slack_config_ids:
                try:
                    # Fetch detailed Slack configuration information
                    slack_config = await client.get_slack_configuration_by_id(config_id)

                    # Extract human-readable details
                    name = slack_config.get('name', 'Unnamed Configuration')
                    channel_name = slack_config.get('channelName', 'N/A')
                    team_name = slack_config.get('teamName') or slack_config.get('team', {}).get('label', 'Unknown Workspace')

                    # Format as: "Name (#channel) - Workspace: Team"
                    slack_detail = f"  - {name} (#{channel_name}) - Workspace: {team_name}"
                    slack_details.append(slack_detail)

                except Exception as e:
                    # Handle cases where Slack configuration might not exist or API call fails
                    logger.warning(f"Failed to fetch Slack configuration {config_id}: {e}")
                    slack_details.append(f"  - Configuration ID: {config_id} (Details unavailable)")

            if slack_details:
                notification_parts.append("• **Slack Notifications:**")
                notification_parts.extend(slack_details)

        # Handle case where no notifications are configured
        if not notification_parts:
            return "\n\n**Notification Configuration:** No notifications configured"

        # Combine all notification information
        notification_text = "\n\n**Notification Configuration:**\n" + "\n".join(notification_parts)
        return notification_text

    def _has_direct_api_format(self, anomaly_data: Dict[str, Any]) -> bool:
        """Check if anomaly data is in direct API format."""
        required_api_fields = ["alertType", "metricType", "operatorType", "threshold"]
        return all(field in anomaly_data for field in required_api_fields)

    def _validate_direct_api_format(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize direct API format data."""
        validated_data = {}

        # Validate required API fields - CORRECTED: Only 3 supported alert types
        required_fields = {
            "alertType": ["THRESHOLD", "CUMULATIVE_USAGE", "RELATIVE_CHANGE"],
            "metricType": ["TOTAL_COST", "COST_PER_TRANSACTION", "TOKEN_COUNT", "INPUT_TOKEN_COUNT",
                          "OUTPUT_TOKEN_COUNT", "ERROR_RATE", "REQUESTS_PER_MINUTE", "TOKENS_PER_MINUTE"],
            "operatorType": ["GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL",
                           "EQUAL", "NOT_EQUAL"],
            "threshold": "numeric"
        }

        for field, valid_values in required_fields.items():
            if field not in anomaly_data:
                raise ValidationError(
                    message=f"Required field '{field}' is missing",
                    field=field,
                    expected=f"One of: {valid_values}" if isinstance(valid_values, list) else "Numeric value"
                )

            value = anomaly_data[field]

            if field == "threshold":
                # Validate numeric threshold
                try:
                    validated_data[field] = float(value)
                except (ValueError, TypeError):
                    raise ValidationError(
                        message=f"Invalid threshold value",
                        field=field,
                        value=value,
                        expected="Numeric value"
                    )
            elif isinstance(valid_values, list):
                # Validate enum values
                if value not in valid_values:
                    raise ValidationError(
                        message=f"Invalid {field} value",
                        field=field,
                        value=value,
                        expected=f"One of: {', '.join(valid_values)}"
                    )
                validated_data[field] = value
            else:
                validated_data[field] = value

        # Validate optional fields
        optional_fields = {
            "periodDuration": ["ONE_MINUTE", "FIVE_MINUTES", "FIFTEEN_MINUTES", "THIRTY_MINUTES",
                             "ONE_HOUR", "TWELVE_HOURS", "TWENTY_FOUR_HOURS", "DAILY", "WEEKLY",
                             "MONTHLY", "QUARTERLY"],
            "isPercentage": "boolean",
            "enabled": "boolean",
            "notificationAddresses": "list",
            "slackConfigurations": "list",
            "triggerAfterPersistsDuration": "string",
            "filters": "list"
        }

        for field, field_type in optional_fields.items():
            if field in anomaly_data:
                value = anomaly_data[field]

                if field == "periodDuration" and isinstance(field_type, list) and value not in field_type:
                    raise ValidationError(
                        message=f"Invalid periodDuration value",
                        field=field,
                        value=value,
                        expected=f"One of: {', '.join(field_type)}"
                    )
                elif field_type == "boolean" and not isinstance(value, bool):
                    raise ValidationError(
                        message=f"Invalid {field} value",
                        field=field,
                        value=value,
                        expected="Boolean (true/false)"
                    )
                elif field_type == "list" and not isinstance(value, list):
                    raise ValidationError(
                        message=f"Invalid {field} value",
                        field=field,
                        value=type(value).__name__,
                        expected="List/array"
                    )

                validated_data[field] = value

        return validated_data
