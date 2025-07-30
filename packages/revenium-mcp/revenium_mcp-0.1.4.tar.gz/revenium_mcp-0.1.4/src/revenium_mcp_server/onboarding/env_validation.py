"""Environment Variable Validation Utility for Revenium MCP Server.

This module DIRECTLY EXTRACTS and reuses the exact validation logic from the
debug_auto_discovery tool (enhanced_server.py lines 442-454) to ensure 100% consistency.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from loguru import logger

# Import existing configuration infrastructure - REUSE EXISTING
from ..config_store import get_config_value


@dataclass
class EnvironmentVariableStatus:
    """Status information for an environment variable."""
    name: str
    value: Optional[str]
    is_set: bool
    is_sensitive: bool
    display_value: str
    category: str
    description: str
    required: bool
    auto_discoverable: bool


@dataclass
class ValidationResult:
    """Result of environment variable validation."""
    variables: Dict[str, EnvironmentVariableStatus]
    api_connectivity: Dict[str, Any]
    auth_config: Dict[str, Any]
    discovered_config: Dict[str, Any]
    summary: Dict[str, Any]
    timestamp: datetime


class EnvironmentVariableValidator:
    """Validates environment variables using EXACT SAME logic as debug_auto_discovery.

    This class directly extracts and reuses the validation logic from enhanced_server.py
    lines 442-454 to ensure 100% consistency with the existing diagnostic tool.
    """

    # EXACT REUSE: Use the same variable list as debug_auto_discovery (lines 442-445)
    # This is the core list from the existing tool - we extend it but keep the base
    DEBUG_AUTO_DISCOVERY_VARS = [
        "REVENIUM_API_KEY", "REVENIUM_TEAM_ID", "REVENIUM_TENANT_ID",
        "REVENIUM_OWNER_ID", "REVENIUM_DEFAULT_EMAIL", "REVENIUM_BASE_URL"
    ]

    # Extended list for comprehensive onboarding (includes all variables we found)
    EXTENDED_VARS = [
        "REVENIUM_APP_BASE_URL",
        "REVENIUM_DEFAULT_SLACK_CONFIG_ID",
        "REVENIUM_DEFAULT_CURRENCY",
        "REVENIUM_DEFAULT_TIMEZONE",
        "REVENIUM_DEFAULT_PAGE_SIZE",
        "REVENIUM_HTTP_MAX_KEEPALIVE",
        "REVENIUM_HTTP_MAX_CONNECTIONS",
        "REVENIUM_HTTP_KEEPALIVE_EXPIRY",
        "REVENIUM_HTTP_TIMEOUT",
        "REVENIUM_TIMEOUT",
        "REVENIUM_ENV",
        "REVENIUM_MAX_RETRIES",
        "REVENIUM_CONFIG_FILE",
        "REVENIUM_TENANT_NAME",
        "LOG_LEVEL",
        "REQUEST_TIMEOUT",
        "UCM_WARNINGS_ENABLED"
    ]

    # Complete list = debug_auto_discovery base + extensions
    ALL_VARIABLES = DEBUG_AUTO_DISCOVERY_VARS + EXTENDED_VARS

    def __init__(self):
        """Initialize the environment variable validator."""
        pass
    
    def get_debug_auto_discovery_env_vars(self) -> Dict[str, str]:
        """EXACT REUSE: Get environment variables using identical logic from debug_auto_discovery.

        This directly reuses lines 447-454 from enhanced_server.py debug_auto_discovery tool.

        Returns:
            Dictionary with same format as debug_auto_discovery tool
        """
        # EXACT COPY from enhanced_server.py lines 447-454
        env_vars = {}
        revenium_vars = [
            "REVENIUM_API_KEY", "REVENIUM_TEAM_ID", "REVENIUM_TENANT_ID",
            "REVENIUM_OWNER_ID", "REVENIUM_DEFAULT_EMAIL", "REVENIUM_BASE_URL"
        ]

        for var in revenium_vars:
            value = os.getenv(var)
            if "API_KEY" in var and value:
                env_vars[var] = "SET (hidden)"
            elif value:
                env_vars[var] = value
            else:
                env_vars[var] = "NOT SET"

        return env_vars

    def get_extended_env_vars(self) -> Dict[str, str]:
        """Get extended environment variables using same logic pattern.

        Returns:
            Dictionary with extended variables using same format
        """
        env_vars = {}

        # Apply same logic pattern to extended variables
        for var in self.EXTENDED_VARS:
            value = os.getenv(var)
            if "API_KEY" in var and value:
                env_vars[var] = "SET (hidden)"
            elif value:
                env_vars[var] = value
            else:
                env_vars[var] = "NOT SET"

        return env_vars

    def get_all_environment_variables_dict(self) -> Dict[str, str]:
        """Get all environment variables using debug_auto_discovery format.

        Returns:
            Dictionary mapping variable names to display values (same format as debug_auto_discovery)
        """
        # Start with exact debug_auto_discovery variables
        env_vars = self.get_debug_auto_discovery_env_vars()

        # Add extended variables using same logic
        extended_vars = self.get_extended_env_vars()
        env_vars.update(extended_vars)

        return env_vars
    
    def get_all_environment_variables(self) -> Dict[str, EnvironmentVariableStatus]:
        """Get status for all environment variables.
        
        Returns:
            Dictionary mapping variable names to their status
        """
        variables = {}
        
        for var_name in self._var_definitions.keys():
            variables[var_name] = self.get_environment_variable_status(var_name)
        
        return variables
    
    async def test_api_connectivity_debug_auto_discovery(self) -> Dict[str, Any]:
        """EXACT REUSE: Test API connectivity using identical logic from debug_auto_discovery.

        This directly reuses lines 456-483 from enhanced_server.py debug_auto_discovery tool.

        Returns:
            Dictionary with API test results (same format as debug_auto_discovery)
        """
        try:
            import httpx

            # EXACT COPY from enhanced_server.py lines 457-458
            api_key = os.getenv("REVENIUM_API_KEY")
            base_url = os.getenv("REVENIUM_BASE_URL", "https://api.revenium.io/meter")

            # EXACT COPY from enhanced_server.py line 460
            api_result = {"status": "not_attempted", "error": None, "response": None}

            # EXACT COPY from enhanced_server.py lines 462-483
            if api_key:
                try:
                    url = f"{base_url}/profitstream/v2/api/users/me"
                    headers = {"x-api-key": api_key}

                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, headers=headers)

                    api_result = {
                        "status": "success" if response.status_code == 200 else "failed",
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else response.text,
                        "url": url
                    }
                except Exception as e:
                    api_result = {
                        "status": "error",
                        "error": str(e),
                        "url": url if 'url' in locals() else "unknown"
                    }
            else:
                api_result["error"] = "No API key available"

            return api_result

        except Exception as e:
            logger.error(f"Error testing API connectivity: {e}")
            return {
                "status": "error",
                "error": f"Failed to test API connectivity: {str(e)}"
            }
    
    async def test_discovered_configuration_debug_auto_discovery(self) -> Dict[str, Any]:
        """EXACT REUSE: Test discovered configuration using identical logic from debug_auto_discovery.

        This directly reuses lines 485-505 from enhanced_server.py debug_auto_discovery tool.

        Returns:
            Dictionary with discovered configuration test results (same format as debug_auto_discovery)
        """
        # EXACT COPY from enhanced_server.py lines 486-505
        discovered_result = {"status": "not_attempted", "error": None, "values": None}
        try:
            from ..config_store import get_config_value
            discovered_values = {
                "team_id": get_config_value("REVENIUM_TEAM_ID"),
                "tenant_id": get_config_value("REVENIUM_TENANT_ID"),
                "owner_id": get_config_value("REVENIUM_OWNER_ID"),
                "default_email": get_config_value("REVENIUM_DEFAULT_EMAIL"),
                "base_url": get_config_value("REVENIUM_BASE_URL")
            }
            discovered_result = {
                "status": "success",
                "values": discovered_values,
                "discovered_count": len([v for v in discovered_values.values() if v])
            }
        except Exception as e:
            discovered_result = {
                "status": "error",
                "error": str(e)
            }

        return discovered_result

    async def test_discovered_configuration_extended(self) -> Dict[str, Any]:
        """Extended discovered configuration test including additional variables.

        Returns:
            Dictionary with extended discovered configuration test results
        """
        try:
            # Start with debug_auto_discovery base
            base_result = await self.test_discovered_configuration_debug_auto_discovery()

            # Add extended variables
            from ..config_store import get_config_value
            extended_values = {
                "app_base_url": get_config_value("REVENIUM_APP_BASE_URL"),
                "slack_config_id": get_config_value("REVENIUM_DEFAULT_SLACK_CONFIG_ID")
            }

            # Merge with base values
            if base_result.get("status") == "success":
                all_values = base_result.get("values", {})
                all_values.update(extended_values)

                return {
                    "status": "success",
                    "values": all_values,
                    "discovered_count": len([v for v in all_values.values() if v])
                }
            else:
                return base_result

        except Exception as e:
            logger.error(f"Error testing extended discovered configuration: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def test_auth_config(self) -> Dict[str, Any]:
        """Test auth configuration using the same logic as debug_auto_discovery.
        
        Returns:
            Dictionary with auth configuration test results
        """
        try:
            # Use same logic as debug_auto_discovery
            from ..config_store import get_config_value
            api_key = get_config_value("REVENIUM_API_KEY")
            team_id = get_config_value("REVENIUM_TEAM_ID")
            tenant_id = get_config_value("REVENIUM_TENANT_ID")
            base_url = get_config_value("REVENIUM_BASE_URL") or "https://api.revenium.io"
            
            if api_key and team_id:
                auth_result = {
                    "status": "success",
                    "config": {
                        "team_id": team_id,
                        "tenant_id": tenant_id,
                        "base_url": base_url,
                        "has_api_key": bool(api_key),
                        "api_key_preview": f"SET ({api_key[:4]}...{api_key[-4:]})" if len(api_key) > 8 else "SET"
                    }
                }
            else:
                missing = []
                if not api_key:
                    missing.append("API_KEY")
                if not team_id:
                    missing.append("TEAM_ID")
                auth_result = {
                    "status": "error",
                    "error": f"Missing required configuration: {', '.join(missing)}"
                }
            
            return auth_result
            
        except Exception as e:
            logger.error(f"Error testing auth configuration: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def test_auth_config_debug_auto_discovery(self) -> Dict[str, Any]:
        """EXACT REUSE: Test auth configuration using identical logic from debug_auto_discovery.

        This directly reuses lines 507-530 from enhanced_server.py debug_auto_discovery tool.

        Returns:
            Dictionary with auth configuration test results (same format as debug_auto_discovery)
        """
        # EXACT COPY from enhanced_server.py lines 508-530
        auth_result = {"status": "not_attempted", "error": None, "config": None}
        try:
            from ..auth import ConfigManager
            manager = ConfigManager()
            auth_config = manager.load_from_env()
            auth_result = {
                "status": "success",
                "config": {
                    "team_id": auth_config.team_id,
                    "tenant_id": auth_config.tenant_id,
                    "base_url": auth_config.base_url,
                    "has_api_key": bool(auth_config.api_key),
                    "api_key_preview": f"SET ({auth_config.api_key[:4]}...{auth_config.api_key[-4:]})" if len(auth_config.api_key) > 8 else "SET"
                }
            }
        except Exception as e:
            auth_result = {
                "status": "error",
                "error": str(e)
            }

        return auth_result

    async def validate_all_debug_auto_discovery_format(self) -> ValidationResult:
        """EXACT REUSE: Perform complete validation using identical logic from debug_auto_discovery.

        This directly reuses the validation logic from enhanced_server.py debug_auto_discovery tool
        to ensure 100% consistency with the existing diagnostic functionality.

        Returns:
            ValidationResult with all validation information (same format as debug_auto_discovery)
        """
        logger.debug("🔍 Performing complete environment variable validation using debug_auto_discovery logic...")

        # EXACT REUSE: Get environment variables using debug_auto_discovery format
        env_vars_dict = self.get_debug_auto_discovery_env_vars()

        # EXACT REUSE: Test API connectivity using debug_auto_discovery logic
        api_connectivity = await self.test_api_connectivity_debug_auto_discovery()

        # EXACT REUSE: Test discovered configuration using debug_auto_discovery logic
        discovered_config = await self.test_discovered_configuration_debug_auto_discovery()

        # EXACT REUSE: Test auth configuration using debug_auto_discovery logic
        auth_config = await self.test_auth_config_debug_auto_discovery()

        # EXACT REUSE: Generate summary using same logic as debug_auto_discovery
        # This follows the exact same logic pattern from the original tool
        discovered_count = discovered_config.get('discovered_count', 0)
        discovered_count = discovered_count if isinstance(discovered_count, int) else 0
        auto_discovery_works = discovered_config.get('status') == 'success' and discovered_count >= 4
        auth_config_works = auth_config.get('status') == 'success'
        api_works = api_connectivity.get('status') == 'success'

        # Convert env_vars_dict to variables format with proper EnvironmentVariableStatus objects
        variables = {}
        for var_name, display_value in env_vars_dict.items():
            # Determine category based on variable name
            if var_name.startswith("REVENIUM_"):
                if "API_KEY" in var_name or "TEAM_ID" in var_name:
                    category = "Core Required"
                elif "EMAIL" in var_name or "SLACK" in var_name:
                    category = "Notifications"  
                elif "URL" in var_name:
                    category = "URLs and Endpoints"
                else:
                    category = "Optional Configuration"
            elif var_name in ["LOG_LEVEL", "REQUEST_TIMEOUT", "UCM_WARNINGS_ENABLED"]:
                category = "System Configuration"
            else:
                category = "Configuration"
            
            # Determine if variable is required
            required = var_name in ["REVENIUM_API_KEY", "REVENIUM_TEAM_ID"]
            
            # Determine if auto-discoverable
            auto_discoverable = var_name in ["REVENIUM_TEAM_ID", "REVENIUM_TENANT_ID", "REVENIUM_OWNER_ID", "REVENIUM_DEFAULT_EMAIL"]
            
            # Get description
            descriptions = {
                "REVENIUM_API_KEY": "API authentication key for Revenium platform access",
                "REVENIUM_TEAM_ID": "Team identifier for API access and team operations",
                "REVENIUM_TENANT_ID": "Tenant identifier for multi-tenant operations",
                "REVENIUM_OWNER_ID": "Owner identifier for ownership and permissions",
                "REVENIUM_DEFAULT_EMAIL": "Default email address for notifications and alerts",
                "REVENIUM_BASE_URL": "Base URL for Revenium API endpoints",
                "REVENIUM_APP_BASE_URL": "Base URL for Revenium application interface",
                "REVENIUM_DEFAULT_SLACK_CONFIG_ID": "Default Slack configuration ID for notifications",
                "LOG_LEVEL": "Logging level for application output",
                "REQUEST_TIMEOUT": "Timeout for API requests in seconds",
                "UCM_WARNINGS_ENABLED": "Enable/disable UCM integration warnings"
            }
            description = descriptions.get(var_name, f"Configuration variable: {var_name}")
            
            is_set = display_value != "NOT SET"
            is_sensitive = "API_KEY" in var_name
            
            variables[var_name] = EnvironmentVariableStatus(
                name=var_name,
                value=os.getenv(var_name) if is_set else None,
                is_set=is_set,
                is_sensitive=is_sensitive,
                display_value=display_value,
                category=category,
                description=description,
                required=required,
                auto_discoverable=auto_discoverable
            )

        summary = {
            "api_key_available": env_vars_dict.get('REVENIUM_API_KEY', 'NOT SET') != 'NOT SET',
            "auto_discovery_works": auto_discovery_works,
            "required_fields_discovered": discovered_count >= 4,
            "email_discovered": bool(discovered_config.get('values', {}).get('default_email')),
            "direct_api_works": api_works,
            "auth_config_works": auth_config_works,
            "overall_status": auto_discovery_works and auth_config_works,
            "configuration_method": "Auto-Discovery (Simplified)" if auto_discovery_works else "Environment Variables (Explicit)"
        }

        result = ValidationResult(
            variables=variables,
            api_connectivity=api_connectivity,
            auth_config=auth_config,
            discovered_config=discovered_config,
            summary=summary,
            timestamp=datetime.now(timezone.utc)
        )

        logger.debug(f"✅ Validation complete using debug_auto_discovery logic: overall_status={summary['overall_status']}")

        return result


# Global instance for easy access
_validator = EnvironmentVariableValidator()


async def validate_environment_variables() -> ValidationResult:
    """Convenience function to validate all environment variables using debug_auto_discovery logic.

    Returns:
        ValidationResult with complete validation information (same format as debug_auto_discovery)
    """
    return await _validator.validate_all_debug_auto_discovery_format()


def get_debug_auto_discovery_env_vars() -> Dict[str, str]:
    """Convenience function to get environment variables in debug_auto_discovery format.

    Returns:
        Dictionary with same format as debug_auto_discovery tool
    """
    return _validator.get_debug_auto_discovery_env_vars()


def get_all_env_vars_dict() -> Dict[str, str]:
    """Convenience function to get all environment variables in debug_auto_discovery format.

    Returns:
        Dictionary mapping variable names to display values
    """
    return _validator.get_all_environment_variables_dict()


def get_validator() -> EnvironmentVariableValidator:
    """Get the global validator instance.
    
    Returns:
        EnvironmentVariableValidator instance
    """
    return _validator
