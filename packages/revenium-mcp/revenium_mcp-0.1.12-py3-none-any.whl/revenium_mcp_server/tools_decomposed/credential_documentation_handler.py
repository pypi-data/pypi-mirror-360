"""Documentation and examples handler for subscriber credentials management.

This module handles capabilities, examples, validation, agent summaries,
and natural language processing for credential operations.
"""

import re
from typing import Any, Dict
from loguru import logger

from ..nlp.credential_nlp_processor import CredentialNLPProcessor
from ..common.error_handling import create_structured_missing_parameter_error


class CredentialDocumentationHandler:
    """Handler for documentation and examples in credential management."""

    def __init__(self):
        """Initialize documentation handler."""
        self.nlp_processor = CredentialNLPProcessor()

    async def get_capabilities(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get tool capabilities and supported operations."""
        return {
            "action": "get_capabilities",
            "tool_name": "manage_subscriber_credentials",
            "version": "1.0.0",
            "capabilities": {
                "crud_operations": {
                    "create": {
                        "description": "Create new subscriber credentials",
                        "required_fields": ["label", "subscriberId", "organizationId", "externalId", "externalSecret"],
                        "optional_fields": ["name", "tags", "subscriptionIds"],
                        "field_types": {
                            "label": "string",
                            "name": "string", 
                            "subscriberId": "string",
                            "organizationId": "string",
                            "externalId": "string",
                            "externalSecret": "string",
                            "tags": "array",
                            "subscriptionIds": "array"
                        }
                    },
                    "read": {
                        "list": "Get paginated list of credentials",
                        "get": "Get specific credential by ID"
                    },
                    "update": {
                        "description": "Update existing credential",
                        "updatable_fields": ["label", "name", "externalId", "externalSecret", "tags", "subscriptionIds"]
                    },
                    "delete": {
                        "description": "Delete credential permanently",
                        "warning": "This action cannot be undone"
                    }
                },
                "helper_operations": {
                    "resolve_subscriber_email_to_id": "Convert subscriber email to ID",
                    "resolve_organization_name_to_id": "Convert organization name to ID"
                },
                "validation": {
                    "field_validation": "Validate credential data structure",
                    "required_field_check": "Ensure all required fields are present",
                    "data_type_validation": "Validate field data types"
                },
                "nlp_support": {
                    "parse_natural_language": "Parse natural language descriptions into credential data",
                    "intent_recognition": "Recognize credential management intents"
                }
            },
            "authentication": {
                "required": True,
                "method": "API key",
                "environment_variables": ["REVENIUM_API_KEY", "REVENIUM_TEAM_ID"]
            },
            "rate_limits": {
                "requests_per_minute": 100,
                "burst_limit": 20
            },
            "dependencies": {
                "manage_customers": "Required for subscriber and organization lookups"
            }
        }

    async def get_examples(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive usage examples."""
        example_type = arguments.get("example_type", "basic")
        
        examples = {
            "basic": {
                "list_credentials": {
                    "description": "List all subscriber credentials with pagination",
                    "usage": "list(page=0, size=20)",
                    "response": "Returns paginated list of credentials with metadata"
                },
                "get_credential": {
                    "description": "Get specific credential by ID",
                    "usage": "get(credential_id='jM7Xg7j')",
                    "response": "Returns detailed credential information"
                },
                "create_credential": {
                    "description": "Create new subscriber credential (supports both object and individual parameter formats)",
                    "usage_object": "create(credential_data={'label': 'API Key', 'subscriberId': 'sub_123', 'organizationId': 'org_456', 'externalId': 'key_789', 'externalSecret': 'secret_value'})",
                    "usage_individual": "create(label='API Key', subscriberId='sub_123', organizationId='org_456', externalId='key_789', externalSecret='secret_value')",
                    "recommended_approach": "Both formats work identically - use whichever feels more natural",
                    "example_data": {
                        "label": "Production API Key",
                        "name": "Production API Key",
                        "subscriberId": "Ydmx8nV",
                        "organizationId": "OQNyK9e",
                        "externalId": "api_key_12345",
                        "externalSecret": "sk_live_abcdef123456",
                        "tags": ["production", "api"],
                        "subscriptionIds": []
                    }
                },
                "update_credential": {
                    "description": "Update existing credential",
                    "usage": "update(credential_id='jM7Xg7j', credential_data={'label': 'Updated API Key', 'externalSecret': 'new_secret'})",
                    "example_data": {
                        "label": "Updated Production API Key",
                        "externalSecret": "sk_live_new_secret_123",
                        "tags": ["production", "api", "updated"]
                    }
                },
                "delete_credential": {
                    "description": "Delete credential permanently",
                    "usage": "delete(credential_id='jM7Xg7j')",
                    "warning": "This action cannot be undone"
                }
            },
            "field_mapping": {
                "browser_form_to_api": {
                    "description": "Mapping from browser form fields to API payload",
                    "mappings": {
                        "Subscriber Credential Name": "label and name",
                        "Subscriber E-Mail": "subscriberId (resolve email to ID)",
                        "Organization": "organizationId (resolve name to ID)",
                        "Credential ID": "externalId",
                        "External Secret": "externalSecret",
                        "Subscription": "subscriptionIds (array)",
                        "Tags": "tags (array)"
                    }
                },
                "helper_methods": {
                    "resolve_subscriber": "await client.resolve_subscriber_email_to_id('user@company.com')",
                    "resolve_organization": "await client.resolve_organization_name_to_id('Company Name')"
                }
            },
            "validation": {
                "validate_credential_data": {
                    "description": "Validate credential data before submission",
                    "usage": "validate(credential_data={...})",
                    "checks": ["required_fields", "field_types", "data_format"]
                }
            },
            "nlp": {
                "parse_natural_language": {
                    "description": "Parse natural language into credential data",
                    "usage": "parse_natural_language(text='Create API key for john@company.com at Acme Corp with secret abc123')",
                    "supported_patterns": [
                        "Create [credential type] for [email] at [organization] with secret [value]",
                        "Add new credential for [subscriber] in [organization]",
                        "Set up authentication for [email] with key [value]"
                    ]
                }
            }
        }

        if example_type in examples:
            return {
                "action": "get_examples",
                "example_type": example_type,
                "examples": examples[example_type]
            }
        else:
            return {
                "action": "get_examples",
                "available_types": list(examples.keys()),
                "examples": examples
            }

    async def validate_credential_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate credential data structure and fields."""
        credential_data = arguments.get("credential_data")
        operation_type = arguments.get("operation_type", "create")  # Default to create for backward compatibility

        if not credential_data:
            raise create_structured_missing_parameter_error(
                parameter_name="credential_data",
                action="validate credential data",
                examples={
                    "usage": "validate(credential_data={...})",
                    "usage_update": "validate(credential_data={...}, operation_type='update')",
                    "example_data": {
                        "label": "API Key",
                        "subscriberId": "sub_123",
                        "organizationId": "org_456",
                        "externalId": "key_789",
                        "externalSecret": "secret_value"
                    }
                }
            )

        validation_results = {
            "action": "validate",
            "operation_type": operation_type,
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_checks": {}
        }

        # Check required fields based on operation type
        if operation_type == "create":
            # For CREATE operations, all fields are required
            required_fields = ["label", "subscriberId", "organizationId", "externalId", "externalSecret"]
            for field in required_fields:
                if field not in credential_data or not credential_data[field]:
                    validation_results["errors"].append(f"Missing required field: {field}")
                    validation_results["valid"] = False
                    validation_results["field_checks"][field] = "missing"
                else:
                    validation_results["field_checks"][field] = "valid"
        else:
            # For UPDATE operations, only validate provided fields
            # No fields are strictly required since it's a partial update
            for field in credential_data.keys():
                if credential_data[field] is not None and credential_data[field] != "":
                    validation_results["field_checks"][field] = "valid"
                else:
                    validation_results["warnings"].append(f"Field '{field}' is empty or null")
                    validation_results["field_checks"][field] = "empty"

        # Check field types
        field_types = {
            "label": str,
            "name": str,
            "subscriberId": str,
            "organizationId": str,
            "externalId": str,
            "externalSecret": str,
            "tags": list,
            "subscriptionIds": list
        }

        for field, expected_type in field_types.items():
            if field in credential_data:
                if not isinstance(credential_data[field], expected_type):
                    validation_results["errors"].append(f"Field '{field}' should be of type {expected_type.__name__}")
                    validation_results["valid"] = False
                    validation_results["field_checks"][field] = f"invalid_type (expected {expected_type.__name__})"

        # Check for common issues
        if "label" in credential_data and len(credential_data["label"]) < 3:
            validation_results["warnings"].append("Label should be at least 3 characters long")

        if "externalSecret" in credential_data and len(credential_data["externalSecret"]) < 8:
            validation_results["warnings"].append("External secret should be at least 8 characters long for security")

        return validation_results

    async def get_agent_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent-friendly summary of subscriber credentials management capabilities."""
        return {
            "action": "get_agent_summary",
            "tool_name": "manage_subscriber_credentials",
            "description": "Comprehensive subscriber credentials management with CRUD operations and enhanced capabilities",
            "quick_start": {
                "1_list_credentials": "list() - Get all subscriber credentials",
                "2_get_credential": "get(credential_id='cred_123') - Get specific credential",
                "3_create_credential": "create(credential_data={...}) - Create new credential",
                "4_update_credential": "update(credential_id='cred_123', credential_data={...}) - Update credential",
                "5_delete_credential": "delete(credential_id='cred_123') - Delete credential"
            },
            "key_features": [
                "🔐 Full CRUD operations for subscriber credentials",
                "📧 Email-to-ID resolution for subscribers",
                "🏢 Organization name-to-ID resolution",
                "✅ Comprehensive field validation",
                "🤖 Natural language processing support",
                "📚 Rich examples and documentation",
                "🔒 Billing safety warnings and guidance"
            ],
            "common_workflows": {
                "create_new_credential": [
                    "1. Resolve subscriber email to ID if needed",
                    "2. Resolve organization name to ID if needed", 
                    "3. Prepare credential data with required fields",
                    "4. Call create() with credential_data",
                    "5. Verify creation with get() using returned ID"
                ],
                "update_existing_credential": [
                    "1. Get current credential with get(credential_id)",
                    "2. Modify desired fields in credential data",
                    "3. Call update() with credential_id and updated data",
                    "4. Verify update with get() to confirm changes"
                ]
            },
            "required_fields_for_create": ["label", "subscriberId", "organizationId", "externalId", "externalSecret"],
            "helper_methods": {
                "resolve_subscriber_email_to_id": "Convert subscriber email to ID for subscriberId field",
                "resolve_organization_name_to_id": "Convert organization name to ID for organizationId field"
            },
            "safety_notes": [
                "🔒 Credential operations affect authentication for billing and usage tracking",
                "⚠️ Deletion is permanent and cannot be undone",
                "🔐 External secrets should be strong and secure",
                "📋 Always validate data before submission"
            ]
        }

    async def parse_natural_language(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Parse natural language descriptions into credential data."""
        text = arguments.get("text") or arguments.get("description")
        if not text:
            raise create_structured_missing_parameter_error(
                parameter_name="text",
                action="parse natural language",
                examples={
                    "usage": "parse_natural_language(text='Create API key for john@company.com at Acme Corp with secret abc123')",
                    "supported_patterns": [
                        "Create [credential type] for [email] at [organization] with secret [value]",
                        "Add new credential for [subscriber] in [organization]",
                        "Set up authentication for [email] with key [value]"
                    ]
                }
            )

        # Use the NLP processor
        nlp_result = await self.nlp_processor.process_natural_language(text)
        
        # Convert to dictionary format
        return {
            "action": "parse_natural_language",
            "input_text": text,
            "intent": nlp_result.intent.value,
            "confidence": nlp_result.confidence,
            "extracted_entities": {
                entity_type: {
                    "value": entity.value,
                    "confidence": entity.confidence,
                    "context": entity.context
                }
                for entity_type, entity in nlp_result.entities.items()
            },
            "extracted_data": self.nlp_processor.extract_credential_data(nlp_result),
            "suggestions": nlp_result.suggestions,
            "warnings": nlp_result.warnings,
            "business_context": nlp_result.business_context
        }
