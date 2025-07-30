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

- **Python 3.8+** with pip
- **Your Revenium API key**
- **Optional**: [uv/uvx](https://github.com/astral-sh/uv) for isolated installation

### For Claude Desktop

**Option 1: Isolated Installation with uvx (Recommended)**

uvx automatically creates and manages isolated environments, preventing dependency conflicts:

```bash
# Install uv (includes uvx) if you don't have it
pip install uv

# uvx creates a persistent, isolated environment for revenium-mcp
uvx install revenium-mcp
```

**Option 2: Virtual Environment Installation (Traditional)**

```bash
# Create and activate a virtual environment
python -m venv revenium-mcp-env
source revenium-mcp-env/bin/activate  # On Windows: revenium-mcp-env\Scripts\activate

# Install the package
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
      "args": ["-m", "revenium_mcp"],
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
      "args": ["-m", "revenium_mcp"],
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

**Option 1: Isolated Installation with uvx (Recommended)**
```bash
# Install uv if you don't have it  
pip install uv

# One-shot installation - uvx manages isolation automatically
claude mcp add revenium-platform \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- uvx run revenium-mcp
```

**Option 2: Virtual Environment Installation**
```bash
# Create and activate virtual environment
python -m venv revenium-mcp-env
source revenium-mcp-env/bin/activate  # On Windows: revenium-mcp-env\Scripts\activate

# Install package
pip install revenium-mcp

# Add to Claude Code using venv python
claude mcp add revenium-platform \
  -e REVENIUM_API_KEY=your_api_key_here \
  -- ./revenium-mcp-env/bin/python -m revenium_mcp
```

**Advanced Installation with Custom Settings (any installation method)**
```bash
claude mcp add revenium-platform \
  -e REVENIUM_API_KEY=your_api_key_here \
  -e REVENIUM_TEAM_ID=ABC123x \
  -e REVENIUM_TENANT_ID=DEF456n \
  -e REVENIUM_OWNER_ID=GHI789z \
  -e REVENIUM_BASE_URL=https://api.revenium.io \
  -e REVENIUM_APP_BASE_URL=https://ai.revenium.io \
  -e REVENIUM_DEFAULT_EMAIL=your_email@company.com \
  -- uvx run revenium-mcp
  # OR: -- ./revenium-mcp-env/bin/python -m revenium_mcp
```


### For VS Code with Copilot Chat

**Install the package first:**
```bash
pip install revenium-mcp
```

**Configure MCP server:**

1. Open VS Code settings (Ctrl/Cmd + ,)
2. Search for "mcp" and enable `chat.mcp.enabled`
3. Create or edit `.vscode/mcp.json` in your workspace:

**Minimal Configuration:**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python",
      "args": ["-m", "revenium_mcp"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Advanced Configuration:**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python", 
      "args": ["-m", "revenium_mcp"],
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

### For Cursor IDE

**Install the package first:**
```bash
pip install revenium-mcp
```

**Configure MCP server:**

1. Open Cursor settings (Ctrl/Cmd + ,)
2. Navigate to Extensions → MCP or create `~/.cursor/mcp.json`
3. Add server configuration:

**Minimal Configuration:**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python",
      "args": ["-m", "revenium_mcp"],
      "env": {
        "REVENIUM_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Advanced Configuration:**
```json
{
  "mcpServers": {
    "revenium-platform": {
      "command": "python",
      "args": ["-m", "revenium_mcp"],
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

### Verification

**Test the installation:**
```bash
# Verify package is installed
python -c "import revenium_mcp; print('Package installed successfully')"

# Test the MCP server directly
python -m revenium_mcp
# (Press Ctrl+C to stop)
```

**For Claude Desktop:**
- Restart the app and look for the MCP tools indicator
- Try asking Claude to interact with your Revenium platform

**For Claude Code:**
- Run `claude mcp list` to verify the server is installed
- Run `claude mcp get revenium-platform` to see configuration details  
- Start Claude Code and use `/mcp` to check server status


### Step 3: Configuration Complete

The MCP server will load additional configuration values from your account automatically, including Team ID, Tenant ID, Owner ID, and default email.

### Optional Configuration Overrides

You can override the automatically loaded values if needed:

**When you might need overrides:**
- Multi-tenant environments: Operating on behalf of a different tenant
- Custom email preferences: Alerts sent to a different email address
- Non-primary users: When you're not the primary user for the account (the user defined in the configuration will be set as the owner for any customers, products, alerts, etc. created via the MCP server )
- Custom API endpoints: Using a different Revenium instance

Use the `system_diagnostics` tool to see which values are loaded automatically vs. explicitly configured.

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
Ask your AI assistant: "Run the system_diagnostics tool"
```

This will show you:
- Which values are set via environment variables
- Which values are loaded automatically
- Current configuration status
- API connectivity test results

---

## 🔍 Troubleshooting

#### Authentication Errors
- Verify your API key is correct and active
- Use the diagnostic tool to check configuration status
- Ensure the base URL is correct for your environment
- Check that the `/users/me` endpoint is accessible with your API key

#### Configuration Priority
The system loads configuration values in this priority order:
1. **MCP client JSON configuration `env` section** (highest priority)
2. **System environment variables**
3. **Automatically loaded values** from Revenium's API

Use the `system_diagnostics` tool to see exactly which values are being used from each source.

### Getting Help

- **Issues**: Report problems on [GitHub Issues](https://github.com/revenium/revenium-mcp/issues)
- **Support**: Email [support@revenium.io](mailto:support@revenium.io)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** our coding standards (see [development best practices](docs/code_best_practices/development_best_practices.md))
4. **Add tests** for new functionality
5. **Ensure** all tests pass (`pytest`)
6. **Submit** a pull request

---

## 📄 License & Support

**License**: MIT License - see [LICENSE](LICENSE) file for details.

**Support Channels**:
- 📧 **Email**: [support@revenium.io](mailto:support@revenium.io)
- 🐛 **Issues**: [GitHub Issues](https://github.com/revenium/revenium-mcp/issues)

---

## 🎯 What's Next?

After getting started, you might want to:

1. **Choose your profile** - Start with `starter` profile (7 tools) for cost monitoring & alerts, then upgrade to `business` (15 tools) for complete AI analytics & billing
2. **Complete setup** - Use the Setup & Onboarding tools to ensure proper configuration
3. **Configure notifications** - Set up Slack integration for real-time alerts
4. **Explore all tools** - Review each of the tool categories to understand their capabilities
5. **Set up monitoring** - Create alerts for your key business metrics
6. **Integrate with your systems** - Connect your AI agents for comprehensive tracking

---
