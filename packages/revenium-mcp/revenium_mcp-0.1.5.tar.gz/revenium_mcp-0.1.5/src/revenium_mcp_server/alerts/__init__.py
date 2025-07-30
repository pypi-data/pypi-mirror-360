"""Alert System Package.

This package contains all alert and anomaly management functionality.
Includes anomaly CRUD operations, alert querying, semantic processing, and analytics.
"""

# Import core managers
from .anomaly_manager import AnomalyManager
from .alert_manager import AlertManager

# Import advanced features
from .semantic_processor import AlertSemanticProcessor
from .analytics_engine import AnalyticsEngine, TimeRange
from .analytics_formatter import AnalyticsFormatter

# Import models for convenience from original models.py file
from ..models import (
    # Enumerations
    AnomalyStatus, AlertSeverity, AlertStatus, AlertType, MetricType,
    OperatorType, PeriodDuration, GroupByDimension, TriggerDuration,
    FilterOperator,

    # Configuration models
    AlertFilter, SlackConfiguration, WebhookConfiguration,
    AdvancedAlertConfiguration, DetectionRule, ThresholdViolation,

    # Main models
    AIAnomalyRequest, AIAnomaly, AIAnomalyLegacy, AIAlert
)

__all__ = [
    # Core managers
    "AnomalyManager",
    "AlertManager",

    # Advanced features
    "AlertSemanticProcessor",
    "AnalyticsEngine",
    "TimeRange",
    "AnalyticsFormatter",

    # Enumerations
    "AnomalyStatus", "AlertSeverity", "AlertStatus", "AlertType", "MetricType",
    "OperatorType", "PeriodDuration", "GroupByDimension", "TriggerDuration",
    "FilterOperator",

    # Configuration models
    "AlertFilter", "SlackConfiguration", "WebhookConfiguration",
    "AdvancedAlertConfiguration", "DetectionRule", "ThresholdViolation",

    # Main models
    "AIAnomalyRequest", "AIAnomaly", "AIAnomalyLegacy", "AIAlert"
]
