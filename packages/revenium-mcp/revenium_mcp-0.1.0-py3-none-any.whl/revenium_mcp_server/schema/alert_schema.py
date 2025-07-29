"""Alert and anomaly schema discovery for MCP tools.

This module provides schema discovery, examples, and validation
specifically for alert and anomaly management functionality.
"""

from typing import Dict, List, Any, Optional
from loguru import logger

from .discovery_engine import BaseSchemaDiscovery


class AlertSchemaDiscovery(BaseSchemaDiscovery):
    """Alert and anomaly specific schema discovery."""
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get alert and anomaly capabilities.
        
        Returns:
            Capabilities dictionary for alerts and anomalies
        """
        return {
            "alert_types": ["THRESHOLD", "CUMULATIVE_USAGE", "RELATIVE_CHANGE"],
            "metrics": {
                "cost_metrics": [
                    "TOTAL_COST", "COST_PER_TRANSACTION", "INPUT_TOKEN_COST", 
                    "OUTPUT_TOKEN_COST", "CACHED_TOKEN_COST"
                ],
                "token_metrics": [
                    "TOKEN_COUNT", "INPUT_TOKEN_COUNT", "OUTPUT_TOKEN_COUNT", 
                    "CACHED_TOKEN_COUNT", "REASONING_TOKEN_COUNT"
                ],
                "performance_metrics": [
                    "TOKENS_PER_SECOND", "REQUESTS_PER_SECOND", "RESPONSE_TIME",
                    "TIME_TO_FIRST_TOKEN", "REQUEST_DURATION"
                ],
                "quality_metrics": [
                    "ERROR_RATE", "ERROR_COUNT", "SUCCESS_RATE", 
                    "RESPONSE_QUALITY_SCORE"
                ],
                "all": [
                    "TOTAL_COST", "COST_PER_TRANSACTION", "INPUT_TOKEN_COST", "OUTPUT_TOKEN_COST", "CACHED_TOKEN_COST",
                    "TOKEN_COUNT", "INPUT_TOKEN_COUNT", "OUTPUT_TOKEN_COUNT", "CACHED_TOKEN_COUNT", "REASONING_TOKEN_COUNT",
                    "TOKENS_PER_SECOND", "REQUESTS_PER_SECOND", "RESPONSE_TIME", "TIME_TO_FIRST_TOKEN", "REQUEST_DURATION",
                    "ERROR_RATE", "ERROR_COUNT", "SUCCESS_RATE", "RESPONSE_QUALITY_SCORE"
                ]
            },
            "operators": {
                "threshold_operators": ["GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN", "LESS_THAN_OR_EQUAL_TO"],
                "relative_change_operators": ["INCREASES_BY", "DECREASES_BY"],
                "string_operators": ["CONTAINS", "STARTS_WITH", "ENDS_WITH"],
                "equality_operators": ["EQUALS", "NOT_EQUALS"],
                "all": ["GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN", "LESS_THAN_OR_EQUAL_TO",
                       "INCREASES_BY", "DECREASES_BY", "CONTAINS", "STARTS_WITH", "ENDS_WITH", "EQUALS", "NOT_EQUALS"]
            },
            "time_periods": {
                "period_duration": [
                    "ONE_MINUTE", "FIVE_MINUTES", "TEN_MINUTES", "FIFTEEN_MINUTES",
                    "THIRTY_MINUTES", "ONE_HOUR", "TWO_HOURS", "SIX_HOURS",
                    "TWELVE_HOURS", "ONE_DAY", "THREE_DAYS", "SEVEN_DAYS",
                    "FOURTEEN_DAYS", "THIRTY_DAYS"
                ],
                "trigger_after_persists_duration": [
                    "FIVE_MINUTES", "TEN_MINUTES", "FIFTEEN_MINUTES", "THIRTY_MINUTES",
                    "ONE_HOUR", "TWO_HOURS", "SIX_HOURS", "TWELVE_HOURS",
                    "ONE_DAY", "THREE_DAYS", "SEVEN_DAYS", "FOURTEEN_DAYS", "THIRTY_DAYS"
                ],
                "comparison_period": [
                    "ONE_DAY", "THREE_DAYS", "SEVEN_DAYS", "FOURTEEN_DAYS", "THIRTY_DAYS"
                ],
                "tracking_period": ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY"]
            },
            "filter_dimensions": {
                "ORGANIZATION": {
                    "description": "Filter by customer/business organization",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "acme corp"
                },
                "CREDENTIAL": {
                    "description": "Filter by API key/credential name",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "production-api-key"
                },
                "PRODUCT": {
                    "description": "Filter by product name",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "AI API Service"
                },
                "MODEL": {
                    "description": "Filter by AI model name",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "gpt-4"
                },
                "PROVIDER": {
                    "description": "Filter by AI provider",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "openai"
                },
                "AGENT": {
                    "description": "Filter by agent/user",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "support-agent"
                },
                "SUBSCRIBER": {
                    "description": "Filter by subscriber name or email",
                    "operators": ["CONTAINS", "EQUALS", "NOT_EQUALS"],
                    "example": "john.doe@company.com"
                }
            },
            "schema": {
                "anomaly_data": {
                    "required": ["name", "alertType", "detection_rules"],
                    "optional": ["description", "enabled", "notificationAddresses", "filters"],
                    "detection_rule_schema": {
                        "required": ["rule_type", "metric", "operator", "value"],
                        "optional": ["time_window", "filters", "group_by", "isPercentage"]
                    }
                }
            }
        }
    
    def get_examples(self, example_type: Optional[str] = None) -> Dict[str, Any]:
        """Get alert and anomaly examples.
        
        Args:
            example_type: Optional filter for specific example types
            
        Returns:
            Examples dictionary
        """
        examples = [
            {
                "name": "High Cost Per Transaction Alert",
                "type": "threshold_cost",
                "description": "Triggers when cost per transaction exceeds threshold",
                "use_case": "Monitor API costs to prevent budget overruns",
                "template": {
                    "name": "High Cost Alert",
                    "alertType": "THRESHOLD",
                    "description": "Alert when cost per transaction is too high",
                    "enabled": True,
                    "detection_rules": [{
                        "rule_type": "THRESHOLD",
                        "metric": "COST_PER_TRANSACTION",
                        "operator": "GREATER_THAN_OR_EQUAL_TO",
                        "value": 0.50,
                        "time_window": "5m"
                    }],
                    "notificationAddresses": ["admin@company.com"]
                }
            },
            {
                "name": "Token Usage Monitoring",
                "type": "threshold_tokens",
                "description": "Monitor token consumption rates",
                "use_case": "Prevent excessive token usage",
                "template": {
                    "name": "High Token Usage",
                    "alertType": "THRESHOLD", 
                    "description": "Alert when token usage is high",
                    "enabled": True,
                    "detection_rules": [{
                        "rule_type": "THRESHOLD",
                        "metric": "TOKENS_PER_SECOND",
                        "operator": "GREATER_THAN",
                        "value": 1000,
                        "time_window": "1m"
                    }]
                }
            },
            {
                "name": "Monthly Budget Alert",
                "type": "cumulative_cost",
                "description": "Track cumulative spending over time periods",
                "use_case": "Monthly budget monitoring",
                "template": {
                    "name": "Monthly Budget Alert",
                    "alertType": "CUMULATIVE_USAGE",
                    "description": "Alert when monthly spending exceeds budget",
                    "enabled": True,
                    "detection_rules": [{
                        "rule_type": "CUMULATIVE_USAGE",
                        "metric": "TOTAL_COST",
                        "operator": "GREATER_THAN_OR_EQUAL_TO",
                        "value": 1000.00,
                        "time_window": "monthly"
                    }],
                    "notificationAddresses": ["billing@company.com"]
                }
            },
            {
                "name": "Error Rate Monitoring",
                "type": "threshold_quality",
                "description": "Monitor API error rates",
                "use_case": "Service quality monitoring",
                "template": {
                    "name": "High Error Rate",
                    "alertType": "THRESHOLD",
                    "description": "Alert when error rate exceeds threshold",
                    "enabled": True,
                    "detection_rules": [{
                        "rule_type": "THRESHOLD",
                        "metric": "ERROR_RATE",
                        "operator": "GREATER_THAN",
                        "value": 5.0,
                        "time_window": "5m",
                        "isPercentage": True
                    }]
                }
            }
        ]
        
        if example_type:
            filtered_examples = [ex for ex in examples if ex.get("type") == example_type]
            return {"examples": filtered_examples}
        
        return {"examples": examples}
    
    def validate_configuration(self, config_data: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Validate alert/anomaly configuration.
        
        Args:
            config_data: Configuration data to validate
            dry_run: Whether this is a dry run validation
            
        Returns:
            Validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": [],
            "dry_run": dry_run
        }
        
        # Check required fields
        required_fields = ["name", "alertType"]
        for field in required_fields:
            if field not in config_data:
                validation_result["valid"] = False
                validation_result["errors"].append({
                    "field": field,
                    "error": f"Required field '{field}' is missing",
                    "suggestion": f"Add '{field}' field to your configuration"
                })
        
        # Validate detection rules if present
        if "detection_rules" in config_data:
            for i, rule in enumerate(config_data["detection_rules"]):
                rule_validation = self._validate_detection_rule(rule, i)
                if not rule_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(rule_validation["errors"])
                validation_result["warnings"].extend(rule_validation.get("warnings", []))
                validation_result["suggestions"].extend(rule_validation.get("suggestions", []))
        
        # Add suggestions for improvement
        if validation_result["valid"]:
            validation_result["suggestions"].append({
                "type": "optimization",
                "message": "Configuration is valid and ready for creation",
                "next_steps": ["Use 'create' action to create this anomaly", "Consider adding filters for more specific monitoring"]
            })
        
        return validation_result
    
    def _validate_detection_rule(self, rule: Dict[str, Any], rule_index: int) -> Dict[str, Any]:
        """Validate a single detection rule."""
        result = {"valid": True, "errors": [], "warnings": [], "suggestions": []}
        
        # Check required fields
        required_fields = ["rule_type", "metric", "operator", "value"]
        for field in required_fields:
            if field not in rule:
                result["valid"] = False
                result["errors"].append({
                    "field": f"detection_rules[{rule_index}].{field}",
                    "error": f"Required field '{field}' is missing in detection rule {rule_index}",
                    "valid_values": self._get_valid_values_for_field(field)
                })
        
        # Validate specific field values
        capabilities = self.get_capabilities()
        
        if "rule_type" in rule:
            valid_types = ["THRESHOLD", "CUMULATIVE_USAGE", "RELATIVE_CHANGE"]
            if rule["rule_type"] not in valid_types:
                result["valid"] = False
                result["errors"].append({
                    "field": f"detection_rules[{rule_index}].rule_type",
                    "error": f"Invalid rule type: {rule['rule_type']}",
                    "valid_values": valid_types,
                    "suggestion": f"Use one of: {', '.join(valid_types)}"
                })
        
        if "metric" in rule:
            valid_metrics = capabilities["metrics"]["all"]
            if rule["metric"] not in valid_metrics:
                result["valid"] = False
                result["errors"].append({
                    "field": f"detection_rules[{rule_index}].metric",
                    "error": f"Invalid metric: {rule['metric']}",
                    "valid_values": valid_metrics,
                    "suggestion": "See capabilities for categorized metric options"
                })
        
        if "operator" in rule:
            valid_operators = capabilities["operators"]["all"]
            if rule["operator"] not in valid_operators:
                result["valid"] = False
                result["errors"].append({
                    "field": f"detection_rules[{rule_index}].operator",
                    "error": f"Invalid operator: {rule['operator']}",
                    "valid_values": valid_operators,
                    "suggestion": "Use operators like 'GREATER_THAN', 'LESS_THAN', 'CONTAINS', etc."
                })
        
        return result
    
    def _get_valid_values_for_field(self, field: str) -> List[str]:
        """Get valid values for a specific field."""
        capabilities = self.get_capabilities()
        field_mappings = {
            "rule_type": ["THRESHOLD", "CUMULATIVE_USAGE", "RELATIVE_CHANGE"],
            "metric": capabilities["metrics"]["all"],
            "operator": capabilities["operators"]["all"]
        }
        return field_mappings.get(field, [])
    
    def _build_quick_reference(self, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Build quick reference for alerts."""
        return {
            "alert_types": capabilities.get("alert_types", []),
            "available_metrics": {
                "cost": capabilities["metrics"]["cost_metrics"],
                "tokens": capabilities["metrics"]["token_metrics"],
                "performance": capabilities["metrics"]["performance_metrics"],
                "quality": capabilities["metrics"]["quality_metrics"]
            },
            "operators": {
                "threshold": capabilities["operators"]["threshold_operators"],
                "relative_change": capabilities["operators"]["relative_change_operators"],
                "string": capabilities["operators"]["string_operators"]
            },
            "time_periods": {
                "check_every": capabilities["time_periods"]["period_duration"],
                "trigger_after": capabilities["time_periods"]["trigger_after_persists_duration"],
                "compare_to": capabilities["time_periods"]["comparison_period"]
            },
            "filter_dimensions": list(capabilities.get("filter_dimensions", {}).keys())
        }
    
    def _build_common_patterns(self, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Build common patterns for alerts."""
        return {
            "cost_monitoring": {
                "metrics": ["TOTAL_COST", "COST_PER_TRANSACTION"],
                "operators": ["GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO"],
                "typical_values": "0.01 to 100.00 (dollars)"
            },
            "performance_monitoring": {
                "metrics": ["TOKENS_PER_SECOND", "REQUESTS_PER_SECOND", "ERROR_RATE"],
                "operators": ["GREATER_THAN", "LESS_THAN"],
                "typical_values": "Depends on metric (rates: 1-1000, error_rate: 1-10%)"
            },
            "usage_monitoring": {
                "metrics": ["TOKEN_COUNT", "INPUT_TOKEN_COUNT", "OUTPUT_TOKEN_COUNT"],
                "operators": ["GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO"],
                "typical_values": "100 to 100000 (tokens)"
            },
            "cumulative_usage_monitoring": {
                "metrics": ["TOTAL_COST", "TOKEN_COUNT", "REQUEST_COUNT"],
                "operators": ["GREATER_THAN_OR_EQUAL_TO", "GREATER_THAN"],
                "typical_values": "Budget limits: $100-$50000, Tokens: 100K-10M, Requests: 1K-100K",
                "time_periods": ["daily", "weekly", "monthly", "quarterly"],
                "description": "Monitor cumulative usage over calendar periods"
            }
        }
