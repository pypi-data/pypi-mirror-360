"""Debug Auto-Discovery Tool

Diagnostic tool to debug auto-discovery issues.
Extracted from enhanced_server.py as part of the refactoring effort.
"""

import os
import json
from datetime import datetime
from typing import Optional

from loguru import logger

# Import FastMCP for MCP tool integration
try:
    from fastmcp import FastMCP
    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False
    logger.warning("FastMCP not available, MCP tool integration disabled")
    
    # Create dummy decorator for when FastMCP is not available
    class FastMCP:
        def tool(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

# Initialize FastMCP instance for tool decorators
mcp = FastMCP("debug_auto_discovery") if FASTMCP_AVAILABLE else FastMCP()


@mcp.tool()
async def debug_auto_discovery() -> str:
    """Diagnostic tool to debug auto-discovery issues.

    Shows current environment variables and tests direct API connectivity
    to isolate the root cause of auto-discovery failures.
    """
    try:
        import httpx

        # Collect environment variable status
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

        # Test direct API call
        api_key = os.getenv("REVENIUM_API_KEY")
        base_url = os.getenv("REVENIUM_BASE_URL", "https://api.revenium.io/meter")

        api_result = {"status": "not_attempted", "error": None, "response": None}

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

        # Test discovered configuration values
        discovered_result = {"status": "not_attempted", "error": None, "values": None}
        try:
            from revenium_mcp_server.config_store import get_config_value
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

        # Test auth config loading with new utility function
        auth_result = {"status": "not_attempted", "error": None, "config": None}
        try:
            from revenium_mcp_server.config_store import get_config_value

            # Test the same pattern as auth.py
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
        except Exception as e:
            auth_result = {
                "status": "error",
                "error": str(e)
            }

        # Compile diagnostic report
        report = {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": env_vars,
            "direct_api_test": api_result,
            "auth_config_test": auth_result,
            "context": "MCP Tool Execution"
        }

        # Check auto-discovery status
        discovered_count = discovered_result.get('discovered_count', 0)
        discovered_count = discovered_count if isinstance(discovered_count, int) else 0
        auto_discovery_works = discovered_result.get('status') == 'success' and discovered_count >= 4
        auth_config_works = auth_result.get('status') == 'success'

        # Get discovered values safely
        discovered_values = discovered_result.get('values', {})
        if not isinstance(discovered_values, dict):
            discovered_values = {}

        return f"""# **Auto-Discovery Diagnostic Report**

## **Environment Variables in MCP Context**
```json
{json.dumps(env_vars, indent=2)}
```

## **Auto-Discovered Configuration Values**
```json
{json.dumps(discovered_result, indent=2)}
```

## **Direct API Test (/users/me)**
```json
{json.dumps(api_result, indent=2)}
```

## **Auth Config Loading Test**
```json
{json.dumps(auth_result, indent=2)}
```

## **Summary**
- **API Key Available**: {'✅ YES' if env_vars.get('REVENIUM_API_KEY') != 'NOT SET' else '❌ NO'}
- **Auto-Discovery Works**: {'✅ YES' if auto_discovery_works else '❌ NO'}
- **Required Fields Discovered**: {'✅ YES' if discovered_count >= 4 else '❌ NO'}
- **Optional Email Discovered**: {'✅ YES' if discovered_values.get('default_email') else '❌ NO'}
- **Direct API Works**: {'✅ YES' if api_result.get('status') == 'success' else '❌ NO'}
- **Auth Config Works**: {'✅ YES' if auth_config_works else '❌ NO'}
- **Overall Status**: {'✅ WORKING' if auto_discovery_works and auth_config_works else '❌ NEEDS ATTENTION'}

**Configuration Method**: {'Auto-Discovery (Simplified)' if auto_discovery_works else 'Environment Variables (Explicit)'}
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    except Exception as e:
        return f"""# **Diagnostic Tool Error**

**Error**: {str(e)}

**Context**: Failed to run diagnostic analysis

**Timestamp**: {datetime.now().isoformat()}
"""