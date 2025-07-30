"""Data Models Package.

This package contains all Pydantic data models organized by domain.
Each module contains models for a specific resource type (products, customers, etc.).
"""

# Import base classes and common utilities
from .base import (
    BaseReveniumModel, TimestampMixin, IdentifierMixin, MetadataMixin, StatusMixin,
    APIResponse, ListResponse, RatingAggregationType,
    validate_email_address, validate_positive_number, validate_non_empty_string
)

# Import product models
from .products import (
    ProductStatus, PlanType, SetupFee, Element, RatingAggregation,
    Tier, Plan, Product
)

# Import customer models
from .customers import (
    UserStatus, UserRole, SubscriberStatus, OrganizationType, OrganizationStatus,
    TeamStatus, TeamRole, User, Subscriber, Organization, TeamMember,
    Team, CustomerAnalytics, CustomerRelationship
)

# Import alert models
from .alerts import (
    AnomalyStatus, AlertSeverity, AlertStatus, AlertType, MetricType,
    OperatorType, PeriodDuration, GroupByDimension, TriggerDuration,
    FilterOperator, AlertFilter, SlackConfiguration, WebhookConfiguration,
    AdvancedAlertConfiguration, DetectionRule, ThresholdViolation,
    AIAnomalyRequest, AIAnomaly, AIAnomalyLegacy, AIAlert
)

# Import subscription models
from .subscriptions import (
    SubscriptionStatus, Subscription, SubscriptionMetrics,
    SubscriptionEvent, SubscriptionEventType
)

# Import source models
from .sources import (
    SourceType, Source
)

# Import metering element models
from .metering_elements import (
    MeteringElementType, MeteringElementStatus, MeteringElementDefinition,
    MeteringElementUsage, MeteringElementTemplate, STANDARD_AI_METERING_ELEMENTS,
    get_templates_by_category, get_template_by_name, get_all_template_categories
)

# Temporary backward compatibility - import from original models.py
from ..models import *

__all__ = [
    # Base classes and mixins
    "BaseReveniumModel", "TimestampMixin", "IdentifierMixin", "MetadataMixin", "StatusMixin",
    # Common response models
    "APIResponse", "ListResponse",
    # Common enumerations
    "RatingAggregationType",
    # Validation utilities
    "validate_email_address", "validate_positive_number", "validate_non_empty_string",
    # Product models
    "ProductStatus", "PlanType", "SetupFee", "Element", "RatingAggregation",
    "Tier", "Plan", "Product",
    # Customer models
    "UserStatus", "UserRole", "SubscriberStatus", "OrganizationType", "OrganizationStatus",
    "TeamStatus", "TeamRole", "User", "Subscriber", "Organization", "TeamMember",
    "Team", "CustomerAnalytics", "CustomerRelationship",
    # Alert models
    "AnomalyStatus", "AlertSeverity", "AlertStatus", "AlertType", "MetricType",
    "OperatorType", "PeriodDuration", "GroupByDimension", "TriggerDuration",
    "FilterOperator", "AlertFilter", "SlackConfiguration", "WebhookConfiguration",
    "AdvancedAlertConfiguration", "DetectionRule", "ThresholdViolation",
    "AIAnomalyRequest", "AIAnomaly", "AIAnomalyLegacy", "AIAlert",
    # Subscription models
    "SubscriptionStatus", "Subscription", "SubscriptionMetrics",
    "SubscriptionEvent", "SubscriptionEventType",
    # Source models
    "SourceType", "Source",  # Note: SourceStatus removed - API doesn't support status field
    # Metering element models
    "MeteringElementType", "MeteringElementStatus", "MeteringElementDefinition",
    "MeteringElementUsage", "MeteringElementTemplate", "STANDARD_AI_METERING_ELEMENTS",
    "get_templates_by_category", "get_template_by_name", "get_all_template_categories",
    # Pagination and filtering models (from original models.py)
    "SortOrder", "SortField", "PaginationParams", "FilterCondition",
    "FilterParams", "PaginationMetadata", "PaginatedResponse"
]
