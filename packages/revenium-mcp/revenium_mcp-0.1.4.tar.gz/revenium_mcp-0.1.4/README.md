# Revenium Platform API MCP Server

**Transform your AI assistant into a powerful business management tool**

Connect Claude, OpenAI, or any MCP-compatible AI assistant to Revenium's comprehensive platform API. 

## AI Cost Tracking & Alerting
- Configure development agents to set up AI cost alerts for newly implemented AI-backed features to avoid unexpected costs
- Ask AI agents to track their own costs with Revenium as they carry out actions within your application
- Ask AI agents to develop AI cost & usage trends over time and set up alerts to immediately send slack or email notifications when anomalies occur
- Help AI agents to integrate Revenium metering into your applications if not using Revenium's pre-built SDKs


## Usage-based Billing & Chargebacks
- Manage all elements of usage-based billing & cost chargebacks
- Manage products, customers, subscriptions, and subscriber credentials

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/revenium/revenium-mcp)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple)](https://modelcontextprotocol.io)

---

## 🛠️ Available Tools

The MCP provides **up to 15 tools** (depending on your chosen profile):

### **Setup & Onboarding**
Get started quickly with guided setup and configuration validation.
- Setup guidance to ensure the required environment variables are properly configured
- Configure email notifications for alert delivery
- *Example: "Show me my setup status and what needs to be configured"*
- *Example: "Help me set up email notifications for alerts"*
- *Example: "Check if my MCP server is properly configured"*
- *Example: "Guide me through the initial setup process"*

### 📱 **Slack Integration**
Set up Slack notifications for alerts and system updates.
- OAuth workflow for connecting new Slack workspaces 
- Manage Slack channel configurations for notifications

- *Example: "Set up Slack notifications for Revenium alerts"*
- *Example: "Show me my current Slack configurations"*
- *Example: "Add a new slack channel for all customer spending alerts"*
- *Example: "Send all product spending anaomalies to the Slack channel #product-spend-alerts."*

### 🚨 **Alert Management**
Set up intelligent monitoring for costs, usage, and performance metrics.
- Create budget threshold and spike detection alerts 
- Get notified when patterns change
- *Example: "Alert me when monthly costs for Anthropic exceed $500"*
- *Example: "Create a spike detection alert when token use exceeds 1,500,000 tokens per hour"*
- *Example: "Alert when error rate exceeds 5% every 5 minutes"*
- *Example: "Set up cost per transaction monitoring so any single AI call costing more than $1.50 triggers an immediate Slack alert"*

### 📈 **Business Analytics**
Analyze costs, usage patterns, and business performance with optional visual charts.
- Cost trend analysis and breakdowns
- *Example: "Summarize my costs for the last day/week/month and highlight any anomalies"*
- *Example: "Show me a breakdown of AI costs last month by provider/customer/product/agent"*

#### Common Use Cases

**"Why did my costs spike yesterday?"**
- *"Analyze cost anomalies in the last 7 days focusing on abnormal spending by provider or API key"*
- *"Detect what caused my cost increase yesterday. Only focus on anomalies larger than $20 vs. the norm"*

**"Find anomalies across all dimensions"**  
- *"Show me cost anomalies in the last month across all providers, models, agents, API keys, and customers"*
- *"Analyze all dimensions for cost spikes above $150 in the past 30 days"*

**"Detect small but significant anomalies to identify early changes in behavior before they become large issues"**
- *"Find API key anomalies in the last week with aggressive sensitivity, even small ones above $1"*
- *"Show me highly sensitive anomaly detection for all my API keys this week"*

#### Parameter Reference for Agentic Cost Analysis
- **period**: `HOUR`, `EIGHT_HOURS`, `TWENTY_FOUR_HOURS`, `SEVEN_DAYS`, `THIRTY_DAYS`, `TWELVE_MONTHS`
- **sensitivity**: `conservative` (3 standard deviations), `normal` (2 standard deviations), `aggressive` (1.5 standard deviations)
- **min_impact_threshold**: Minimum dollar amount to report (e.g., 10.0 for $10+)
- **include_dimensions**: Array of `["providers", "models", "agents", "api_keys", "customers"]`

#### Output Structure
- **temporal_anomalies**: Detailed anomaly list with z-scores, severity scores, and context
- **time_period_summary**: Mathematical aggregations by time period with cost multipliers
- **entity_summary**: Per-entity analysis with pattern detection (consecutive days, weekend spikes)
- **recommendations**: Intelligent suggestions based on detected patterns

#### Sample Anomaly Detection Output

```json
{
  "period_analyzed": "SEVEN_DAYS",
  "sensitivity_used": "normal",
  "total_anomalies_detected": 3,
  "temporal_anomalies": [
    {
      "entity_name": "OpenAI",
      "entity_type": "provider",
      "time_group_label": "Wednesday",
      "anomaly_value": 970.20,
      "z_score": 2.8,
      "severity_score": 87.3,
      "context": "OpenAI costs on Wednesday ($970.20) were 2.8 standard deviations above the average value in the evaluated period",
      "percentage_above_normal": 505.4
    },
    {
      "entity_name": "engineering-API-key",
      "entity_type": "api_key",
      "time_group_label": "Wednesday", 
      "anomaly_value": 970.04,
      "z_score": 2.9,
      "severity_score": 90.6,
      "context": "Engineerings API key costs on Wednesday ($970.04) were 2.9 standard deviations above the average value in the evaluated period",
      "percentage_above_normal": 762.0
    }
  ],
  "entity_summary": {
    "OpenAI": {
      "anomalous_time_periods": ["Wednesday"],
      "total_anomalous_cost": 970.20,
      "anomaly_pattern": "Single period anomaly (this entity only)"
    },
    "ANONYMOUS-API-KEY": {
      "anomalous_time_periods": ["Wednesday", "Tuesday"],
      "total_anomalous_cost": 1574.75,
      "anomaly_pattern": "Consecutive day pattern for this entity (2 consecutive periods)"
    }
  },
  "recommendations": [
    "Add subscriber credential tagging to usage metadata when submitting transactions to enable attribution of API Key spending to specific users or projects."
  ]
}
```

### 📈 **Metering Management**
Track AI usage, token consumption, and transaction data with comprehensive integration guidance.
- Develop new custom integration to Revenium AI cost tracking
- Get comprehensive implementation guidance with working code examples for Python and JavaScript
- Submit AI transaction data and verify processing
- Validate transactions and troubleshoot integration issues
- *Example: "Send 5 test transactions using the GPT-4o model with randomized tokens for customer Acme Corp, task doc-summarization, agent content-creator"*
- *Example: "Get Python integration guide with working code examples for AI transaction metering"*
- *Example: "Get JavaScript integration guide with official npm package references"*
- *Example: "Record a GPT-4 transaction with 1500 input tokens and 800 output tokens"*
- *Example: "Check the status of transaction tx_12345"*
- *Example: "Help me integrate this python AI function with Revenium's AI metering API"*
- *Example: "Generate test transaction data for financial services industry"*

### 📊 **Product Management**
Create and manage your API products, pricing tiers, and billing models.
- Design usage-based or subscription pricing
- Design chargeback models so that all AI spending is invoiced to the correct internal department
- Set up free tiers and graduated pricing for SaaS products
- *Example: "Create a Gold Tier AI product with $199 per month base fee plus usage-based pricing that charges 1.10x the actual AI costs"*
- *Example: "Create a new AI API product called 'Smart Analytics' with usage-based pricing"*
- *Example: "Set up a free tier with 1000 API calls, then $0.02 per call after that"*
- *Example: "Show me all my products and their current subscription counts"*

### 🔑 **Subscriber Credentials Management**
Manage billing credentials and authentication for customer subscriptions.
- Create and manage subscriber API keys and credentials
- Handle billing relationship authentication
- Comprehensive credential lifecycle management
- Business context and billing impact analysis
- *Example: "Create API credentials for customer billing integration"*
- *Example: "Update subscriber credentials for automated billing"*
- *Example: "Show me all subscriber credentials and their status"*
- *Example: "Analyze billing impact of credential changes"*

### �👥 **Customer Management**
Handle customer relationships, organizations, and user hierarchies.
- Manage customer or internal organizations used for cost attribution
- Create & manage subscribers (internal or external)
- Track customer usage

- *Example: "List all customer organizations and their subscription status"*
- *Example: "Show me all subscribers and their organization details"*
- *Example: "List customer organizations with their creation dates"*
- *Example: "Show me all subscribers and their associated organizations"*

### 📋 **Subscription Management**
Control customer subscriptions, billing cycles, and plan changes.
- Create and modify customer subscriptions
- Track subscription analytics
- *Example: "Create a monthly subscription for customer ABC Corp to the product 'analytics-suite'"*
- *Example: "Show me all active subscriptions to the AI Analytics product"*
- *Example: "List subscriptions that are about to expire this month"*

### 🔗 **Source Management**
Configure data sources for usage tracking and integration. 

**Note: all AI related costs are automatically associated with the correct source.  New sources are only needed for non-AI data sources.**

- Set up API, database, and webhook sources
- Configure authentication and endpoints
- Validate source configurations
- *Example: "Create a new API source called inventory_management with the URL https://api.example.com/inventory/v2"*
- *Example: "Set up a streaming data source for real-time analytics"*
- *Example: "Configure an AI service source for OpenAI API integration"*

### 🏷️ **Metering Elements**
**Note: all AI related metering elements are automatically associated with the correct source.  New elements are only needed for non-AI data sources.**
Define custom metrics and identifiers for usage tracking.
- Create custom usage identifiers
- Set up cost tracking elements
- Configure billing dimensions
- *Example: "Add a new metering element to track shipping weight from all packages in our application"*
  - *This would be used so that shipping weights could be sent to Revenium's metering API and used to create usage-based pricing based on weight*
- *Example: "Show me all existing metering elements and their configurations"*
- *Example: "Get examples of metering element creation from templates"*

### 🔄 **Workflow Management**
Orchestrate complex multi-step business processes.
- Customer onboarding workflows
- Product launch procedures
- Alert setup automation
- *Example: "Start the customer onboarding workflow for new enterprise client"*
- *Example: "Set up a complete product launch workflow with monitoring"*
- *Example: "Show me available workflow templates"*
- *Example: "Begin product setup workflow for Enterprise Analytics with subscription pricing"*

### 🧪 **Testing & Validation**
Comprehensive testing and validation tools for AI transaction metering.
- Generate realistic test data for AI transactions
- Validate field mapping and data integrity between your application and Revenium.
- Batch submission testing and analysis
- Regression testing and baseline comparison
- *Example: "Generate test data for AI transaction validation to test our usage-based pricing plan based on AI consumption"*
- *Example: "Validate my last AI transaction's field mappings"*

### 🔧 **Diagnostics & Configuration**
Advanced system diagnostics and configuration analysis.
- Comprehensive configuration status reporting
- Environment variable analysis and validation
- API connectivity testing and troubleshooting
- Configuration analysis and recommendations
- *Example: "Run full diagnostic check on my MCP server configuration"*
- *Example: "Show me configuration status and recommendations"*
- *Example: "Analyze my configuration for potential issues"*

### **Known Limitations**
Revenium's API provides many other endpoints that are not yet been implemented in our repository.  If there is one you'd like to see added, submit a PR or open an issue with the request.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed on your system
- **Git** for cloning the repository
- **Revenium API key** (from the API Keys page in the Revenium application)
- An **MCP-compatible AI assistant** (Claude Desktop, Augment Code, Cursor, Roocode, etc.)

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/revenium/revenium-mcp.git
cd revenium-mcp

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Choose Your Profile

The MCP server supports **two profiles** to match your use case and reduce tool complexity:

#### **Profile Overview**

| Profile | Tools | Target Users | Use Cases |
|---------|-------|--------------|-----------|
| **Starter** | 7 tools | Cost monitoring & alerts | Cost analysis, AI transaction metering |
| **Business** | 15 tools | Complete AI analytics & billing | Product & subscription management, usage-based billing, comprehensive analytics |

#### **Startup Commands**

Choose your profile by setting the `TOOL_PROFILE` environment variable:

```bash
# Starter Profile (7 tools) - Cost monitoring, alerts, AI metering integration
TOOL_PROFILE=starter python run_server_dev.py

# Business Profile (15 tools) - Complete AI analytics & billing (default)
TOOL_PROFILE=business python run_server_dev.py
# or simply:
python run_server_dev.py
```

#### **Configuration Options**

You can override individual tools regardless of profile:

```bash
# Add specific tool to starter profile (example)
TOOL_PROFILE=starter TOOL_ENABLED_MANAGE_CAPABILITIES=true python run_server_dev.py

# Disable specific tools in business profile
TOOL_PROFILE=business TOOL_ENABLED_SLACK_MANAGEMENT=false python run_server_dev.py
```

> **📖 For detailed configuration options**, see the comprehensive guide at [`docs/user_guides/MCP_Tool_Configuration_Guide.md`](docs/user_guides/MCP_Tool_Configuration_Guide.md)

### Step 3: Configure Your AI Assistant

Configure the MCP server in your AI assistant client. Only your API key is required - other configuration values are loaded automatically.

Follow the configuration instructions below for your specific AI assistant client:

---

## 💻 Installation

### Prerequisites

- **Python 3.8+** with pip or [uvx](https://github.com/astral-sh/uv)
- **Your Revenium API key**

### For Claude Desktop

**Option 1: Using uvx (Recommended)**

uvx automatically handles dependencies and virtual environments:

```bash
uvx revenium-mcp
```

**Option 2: Install the package with pip:**

```bash
pip install revenium-mcp
```

**Locate your Claude Desktop config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this configuration:**

**Minimal Configuration (Recommended):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python",
      "args": ["-m", "revenium_mcp_server"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Advanced Configuration (Optional Overrides):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python",
      "args": ["-m", "revenium_mcp_server"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here",
        "REVENIUM_TEAM_ID": "ABC123x",
        "REVENIUM_TENANT_ID": "DEF456n",
        "REVENIUM_OWNER_ID": "GHI789z",
        "REVENIUM_BASE_URL": "https://api.revenium.io",
        "REVENIUM_APP_BASE_URL": "https://ai.revenium.io",
        "REVENIUM_DEFAULT_EMAIL": "your_email@company.com"
      }
    }
  }
}
```

**Restart Claude Desktop**

### For Claude Code

**Option 1: Simple Installation (Recommended)**
```bash
claude mcp add revenium-platform \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- python -m revenium_mcp_server
```

**Option 2: Advanced Installation if you need to override default settings**
```bash
claude mcp add revenium-platform \
  -e REVENIUM_API_KEY=your_api_key_here \
  -e REVENIUM_TEAM_ID=ABC123x \
  -e REVENIUM_TENANT_ID=DEF456n \
  -e REVENIUM_OWNER_ID=GHI789z \
  -e REVENIUM_BASE_URL=https://api.revenium.io \
  -e REVENIUM_APP_BASE_URL=https://ai.revenium.io \
  -e REVENIUM_DEFAULT_EMAIL=your_email@company.com \
  -- python -m revenium_mcp_server
```

**Option 3: JSON Installation (Alternative)**
```bash
claude mcp add-json revenium-platform '{
  "command": "python",
  "args": ["-m", "revenium_mcp_server"],
  "env": {
    "REVENIUM_API_KEY": "your_api_key_here"
  }
}'
```

### Development Installation

If you're developing or testing locally:

**Clone and install in development mode:**

```bash
git clone https://github.com/revenium/revenium-mcp.git
cd revenium-mcp
pip install -e .
```

- For Claude Desktop, use the module installation method above
- For Claude Code:

```bash
claude mcp add revenium-platform-dev \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- python -m revenium_mcp_server
```

### VS Code with Continue Extension

1. **Install Continue extension** from the VS Code marketplace
2. **Open Continue settings** (Ctrl/Cmd + Shift + P → "Continue: Open Config")
3. **Add MCP server configuration:**

**Minimal Configuration (Recommended):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "./venv/bin/python",
      "args": ["/absolute/path/to/revenium-mcp/run_server.py"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Advanced Configuration (Optional Overrides):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "./venv/bin/python",
      "args": ["/absolute/path/to/revenium-mcp/run_server.py"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here",
        "REVENIUM_TEAM_ID": "ABC123x",
        "REVENIUM_TENANT_ID": "DEF456n",
        "REVENIUM_OWNER_ID": "GHI789z",
        "REVENIUM_BASE_URL": "https://api.revenium.io/meter",
        "REQUEST_TIMEOUT": "30"
      }
    }
  }
}
```

### Cursor IDE (Manual Configuration)

1. **Open Cursor settings** (Ctrl/Cmd + ,)
2. **Navigate to Extensions → MCP**
3. **Add server configuration:**

**Minimal Configuration (Recommended):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "./venv/bin/python",
      "args": ["/absolute/path/to/revenium-mcp/run_server.py"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Advanced Configuration (Optional Overrides):**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "./venv/bin/python",
      "args": ["/absolute/path/to/revenium-mcp/run_server.py"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here",
        "REVENIUM_TEAM_ID": "ABC123x",
        "REVENIUM_TENANT_ID": "DEF456n",
        "REVENIUM_OWNER_ID": "GHI789z",
        "REVENIUM_BASE_URL": "https://api.revenium.io/meter",
        "REQUEST_TIMEOUT": "30"
      }
    }
  }
}
```

### Other MCP-Compatible IDEs

For other IDEs that support MCP, follow their specific MCP server configuration instructions using:
- **Command**: `python` or `./venv/bin/python`
- **Args**: `["/absolute/path/to/revenium-mcp/run_server.py"]`
- **Environment variables**: Set the `REVENIUM_API_KEY` as shown below:

**Minimal configuration for any MCP client:**
```json
{
  "env": {
    "REVENIUM_API_KEY": "your_api_key_here"
  }
}
```

### Step 3: Configuration Complete

The MCP server will load additional configuration values from your account automatically, including Team ID, Tenant ID, Owner ID, and default email.

### Optional Configuration Overrides

You can override the automatically loaded values if needed:

**When you might need overrides:**
- Multi-tenant environments: Operating on behalf of a different tenant
- Custom email preferences: Alerts sent to a different email address
- Non-primary users: When you're not the primary user for the account (the user defined in the configuration will be set as the owner for any customers, products, alerts, etc. created via the MCP server )
- Custom API endpoints: Using a different Revenium instance

Use the `debug_auto_discovery` tool to see which values are loaded automatically vs. explicitly configured.

---

## 💡 Usage Examples

Once configured, you can interact with your Revenium platform through natural language. Here are some examples to get you started:

### Setup & Onboarding
```
"Show me my setup status and what needs to be configured"
"Help me set up email notifications for alerts"
"Check if my MCP server is properly configured"
"Guide me through the initial setup process"
```

### Slack Integration
```
"Set up Slack notifications for my alerts"
"Connect my Slack workspace to receive notifications"
"Show me my current Slack configurations"
"Help me configure Slack channels for different alert types"
```

### Product Management
```
"Create a Gold Tier AI product with $199 per month base fee plus usage-based pricing that charges 1.10x the actual AI costs"
"Show me all my products and their current subscription counts"
"Set up a free tier with 1000 API calls, then $0.02 per call after that"
```

### Customer Operations
```
"List all customer organizations and their subscription status"
"Show me all subscribers and their organization details"
"List customer organizations with their creation dates"
```

### Monitoring & Alerts
```
"Set up an alert when monthly costs exceed $1000"
"Create a budget alert for 50000 tokens per month"
"Show me all active alerts and their current status"
```

### Usage Tracking
```
"Send 5 test transactions using the GPT-4o model with randomized tokens for customer Acme Corp, task doc-summarization, agent content-creator"
"Show me this month's AI usage by customer"
"List available metering element templates for cost tracking"
```

### Workflow Automation
```
"Start the customer onboarding workflow for new client ABC Corp"
"Set up a complete product launch workflow with monitoring"
"Begin product setup workflow for Enterprise Analytics with subscription pricing"
```

### Business Analytics & Visualization
```
"Analyze my AI costs and show me a chart"
"Compare OpenAI vs Anthropic costs for the last quarter with a visual breakdown"
"Show me cost trends over the last month with a line chart"
```

### Enhanced Spike Detection
```
"Detect cost anomalies in the last 7 days with normal sensitivity across all providers"
"Find API key anomalies in the last month above $50 with aggressive sensitivity"
"Analyze agent cost spikes for the past week with conservative sensitivity"
"Analyze weekend cost spikes across all dimensions for the last 30 days"
"Show me consecutive day anomaly patterns for the last week"
```

### Subscriber Credentials Management
```
"Create API credentials for customer billing integration"
"Update subscriber credentials for automated billing"
"Show me all subscriber credentials and their status"
"Analyze billing impact of credential changes"
```

### Testing & Validation
```
"Generate test data for AI transaction validation"
"Validate my AI transaction field mappings"
"Run comprehensive validation tests on my metering setup"
"Analyze field mapping accuracy for my transactions"
```

### Diagnostics & Configuration
```
"Run full diagnostic check on my MCP server configuration"
"Check my environment variables and API connectivity"
"Show me configuration status and recommendations"
"Analyze my configuration for potential issues"
```

---

## 🔧 Configuration Details

### MCP Client Configuration

Configure environment variables directly in your MCP client's JSON configuration.

### Required Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REVENIUM_API_KEY` | ✅ | Your account API key from the API Keys page in Revenium | `hak_1234567890abcdef` |

### Automatically Loaded Values

These values are loaded from your account and can be overridden if needed:

| Variable | Override When | Example |
|----------|---------------|---------|
| `REVENIUM_TEAM_ID` | Multi-tenant environments | `ABC123x` |
| `REVENIUM_TENANT_ID` | Operating on behalf of different tenant | `DEF456n` |
| `REVENIUM_OWNER_ID` | Non-primary user scenarios | `GHI789z` |
| `REVENIUM_DEFAULT_EMAIL` | Custom alert email preferences | `alerts@company.com` |

### Optional Configuration

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REVENIUM_BASE_URL` | ⚪ | API endpoint URL (defaults to main Revenium instance) | `https://api.revenium.io/meter` |
| `REVENIUM_APP_BASE_URL` | ⚪ | Defines which Revenium web application instance to use for Slack channel configurations (defaults to main Revenium instance) | `https://ai.revenium.io` |
| `LOG_LEVEL` | ⚪ | Logging verbosity level | `DEBUG` |
| `REQUEST_TIMEOUT` | ⚪ | API request timeout in seconds | `30` |

### Configuration Verification

Use the diagnostic tool to verify your configuration:

```
Ask your AI assistant: "Run the debug_auto_discovery tool"
```

This will show you:
- Which values are set via environment variables
- Which values are loaded automatically
- Current configuration status
- API connectivity test results

### Using Virtual Environment Python

If you prefer to use the virtual environment's Python interpreter in your IDE configuration:

```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "/absolute/path/to/revenium-mcp/venv/bin/python",
      "args": ["/absolute/path/to/revenium-mcp/run_server.py"]
    }
  }
}
```

**Note:** On Windows, use `venv\Scripts\python.exe` instead of `venv/bin/python`.

---

## 🔍 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check Python version (should be 3.11+)
python --version

# Verify dependencies are installed
pip list | grep fastmcp
pip list | grep loguru

# Try running the server directly
python run_server.py
```

#### MCP Client Can't Connect to Server
1. **Check file paths** - Ensure all paths in your MCP client configuration are absolute paths
2. **Verify API key** - Make sure your `REVENIUM_API_KEY` is set correctly in the MCP client JSON configuration
3. **Test configuration** - Use the diagnostic tool: ask your AI assistant to "Run the debug_auto_discovery tool"
4. **Check MCP client logs** - Look for connection errors in your AI assistant's logs
5. **Test API connectivity**:
   ```bash
   curl -H "x-api-key: your_api_key" \
        -H "Content-Type: application/json" \
        "https://api.revenium.io/meter/profitstream/v2/api/users/me"
   ```

#### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Or use the automated setup script (if available)
./scripts/setup-dev.sh
```

#### Authentication Errors
- Verify your API key is correct and active
- Use the diagnostic tool to check configuration status
- Ensure the base URL is correct for your environment
- Check that the `/users/me` endpoint is accessible with your API key

#### Configuration Priority
The system loads configuration values in this priority order:
1. **MCP client JSON configuration `env` section** (highest priority)
2. **System environment variables**
3. **Automatically loaded values** from `/users/me` API endpoint
4. **`.env` file in project root** (development only, lowest priority)

Use the `debug_auto_discovery` tool to see exactly which values are being used from each source.

### Getting Help

- **Documentation**: Check the [docs/](docs/) folder for detailed guides
- **Technical Details**: See [docs/deprecated/README-old.md](docs/deprecated/README-old.md) for comprehensive technical documentation
- **Issues**: Report problems on [GitHub Issues](https://github.com/revenium/revenium-mcp/issues)
- **Support**: Email [support@revenium.io](mailto:support@revenium.io)

---

## 🏗️ Advanced Topics

### Development Setup

For developers who want to contribute or customize the MCP server:

```bash
# Clone and setup for development
git clone https://github.com/revenium/revenium-mcp.git
cd revenium-mcp

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black src tests
isort src tests

# Type checking
mypy src
```

### Development Configuration (.env files)

When developing or testing the MCP server directly (outside of an MCP client), you can use `.env` files for configuration:

**Create a `.env` file in the project root:**

```bash
# Required - Only your API key is needed
REVENIUM_API_KEY=your_api_key_here                    # Your account API key from Revenium

# Optional development settings
REQUEST_TIMEOUT=30                                    # API request timeout in seconds
LOG_LEVEL=INFO                                        # Logging verbosity (INFO, DEBUG, WARNING, ERROR)
```

**Optional overrides for development:**

```bash
# Automatically loaded values (override only if needed for testing)
REVENIUM_TEAM_ID=ABC123x                              # Team ID (loaded from /users/me)
REVENIUM_TENANT_ID=DEF456n                            # Tenant ID (loaded from /users/me)
REVENIUM_OWNER_ID=GHI789z                             # User ID (loaded from /users/me)
REVENIUM_DEFAULT_EMAIL=your_email@company.com         # Default email (loaded from /users/me)
REVENIUM_BASE_URL=https://api.revenium.io/meter       # API endpoint (defaults to main Revenium instance)
```

**When to use .env files:**
- **Direct server testing**: Running `python run_server.py` for development
- **Local debugging**: Testing outside of MCP client context
- **Shared team configurations**: Common settings for development teams
- **CI/CD pipelines**: Automated testing and deployment

**Test the server directly:**

```bash
# Test that the server starts correctly
python run_server.py
```

You should see output indicating the MCP server is running successfully.

### Architecture Overview

The MCP server is built with:
- **FastMCP**: Modern MCP framework for Python
- **Pydantic**: Data validation and serialization
- **HTTPX**: Async HTTP client for API calls
- **Loguru**: Structured logging

### Key Components

- `enhanced_server.py` - Main MCP server entry point
- `client.py` - Revenium API client
- `tools.py` - Core business management tools
- `models.py` - Data models and validation

### Documentation

For detailed technical documentation, see:
- [Development Best Practices](docs/code_best_practices/development_best_practices.md)
- [Comprehensive Technical Guide](docs/deprecated/README-old.md) (full technical details)
- [Testing Documentation](tests/agent/) (agent testing scenarios)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** our coding standards (see [development best practices](docs/code_best_practices/development_best_practices.md))
4. **Add tests** for new functionality
5. **Ensure** all tests pass (`pytest`)
6. **Submit** a pull request

### Development Standards
- Follow agent-friendly design patterns
- Include comprehensive error handling
- Maintain 95%+ test coverage
- Use structured logging and validation

---

## 📄 License & Support

**License**: MIT License - see [LICENSE](LICENSE) file for details.

**Support Channels**:
- 📧 **Email**: [support@revenium.io](mailto:support@revenium.io)
- 🐛 **Issues**: [GitHub Issues](https://github.com/revenium/revenium-mcp/issues)
- 📚 **Documentation**: [docs/](docs/) folder

---

## 🎯 What's Next?

After getting started, you might want to:

1. **Choose your profile** - Start with `starter` profile (7 tools) for cost monitoring & alerts, then upgrade to `business` (15 tools) for complete AI analytics & billing
2. **Complete setup** - Use the Setup & Onboarding tools to ensure proper configuration
3. **Configure notifications** - Set up Slack integration for real-time alerts
4. **Explore all tools** - Try each of the 14 tool categories to understand their capabilities
5. **Set up monitoring** - Create alerts for your key business metrics
6. **Automate workflows** - Use the workflow engine for complex operations
7. **Integrate with your systems** - Connect your data sources for comprehensive tracking

**Ready to transform your business operations with AI?** Start with the Quick Start guide above and begin managing your platform through natural language conversations!

---

*This MCP server transforms Revenium's platform API into an intuitive, AI-powered business management interface. Experience the future of platform operations through natural language.* ✨