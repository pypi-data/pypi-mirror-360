"""Analytics package for business intelligence and insights.

This package provides comprehensive analytics capabilities for the Revenium MCP server,
including cost analysis, profitability tracking, and business intelligence features.

Key Components:
- BusinessAnalyticsEngine: Core analytics processing and orchestration
- CostAnalyticsProcessor: Cost trend analysis and breakdown
- ProfitabilityAnalyticsProcessor: Customer and product profitability analysis
- ComparativeAnalyticsProcessor: Period-over-period and benchmarking analysis
- AlertAnalyticsWorkflowProcessor: Alert-to-analytics workflows and root cause analysis
- TimeSeriesProcessor: Time series data processing utilities
- ChartDataFormatter: Chart data formatting for visualizations
- NLPBusinessProcessor: Natural language processing for business queries
- AnalyticsMiddleware: Data processing middleware

Architecture:
This analytics package follows the hybrid service layer approach, providing
shared analytics services that can be used by multiple MCP tools while
maintaining clean separation of concerns.
"""

from .business_analytics_engine import BusinessAnalyticsEngine
from .cost_analytics_processor import CostAnalyticsProcessor
from .profitability_analytics_processor import (
    ProfitabilityAnalyticsProcessor,
    ProfitabilityData,
    CustomerProfitability,
    ProductProfitability
)
from .comparative_analytics_processor import (
    ComparativeAnalyticsProcessor,
    ComparisonResult,
    PercentageChange,
    BenchmarkData,
    ComparisonMetadata
)
from .time_series_processor import TimeSeriesProcessor
from .chart_data_formatter import ChartDataFormatter
from .ucm_integration import AnalyticsUCMIntegration, AnalyticsCapabilityDiscovery
from .nlp_business_processor import NLPBusinessProcessor, QueryIntent, NLPQueryResult
from .alert_analytics_workflow_processor import (
    AlertAnalyticsWorkflowProcessor,
    AlertContext,
    RootCauseAnalysis
)
from .transaction_level_analytics_processor import (
    TransactionLevelAnalyticsProcessor,
    TransactionLevelData,
    AgentTransactionData,
    TaskAnalyticsData
)
from .transaction_level_validation import (
    TransactionLevelParameterValidator
)

__all__ = [
    "BusinessAnalyticsEngine",
    "CostAnalyticsProcessor",
    "ProfitabilityAnalyticsProcessor",
    "ProfitabilityData",
    "CustomerProfitability",
    "ProductProfitability",
    "ComparativeAnalyticsProcessor",
    "ComparisonResult",
    "PercentageChange",
    "BenchmarkData",
    "ComparisonMetadata",
    "TimeSeriesProcessor",
    "ChartDataFormatter",
    "AnalyticsUCMIntegration",
    "AnalyticsCapabilityDiscovery",
    "NLPBusinessProcessor",
    "QueryIntent",
    "NLPQueryResult",
    "AlertAnalyticsWorkflowProcessor",
    "AlertContext",
    "RootCauseAnalysis",
    "TransactionLevelAnalyticsProcessor",
    "TransactionLevelData",
    "AgentTransactionData",
    "TaskAnalyticsData",
    "TransactionLevelParameterValidator"
]

__version__ = "1.0.0"
