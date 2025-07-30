"""Common validation utilities.

This module provides shared validation functions used across the MCP server.
"""

from typing import Any, Dict, List, Optional
from ..validators import InputValidator
from ..exceptions import ValidationError

# Re-export common validation functions
__all__ = ["InputValidator", "ValidationError", "validate_required_params", "validate_id_format"]


def validate_required_params(params: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required parameters are present.
    
    Args:
        params: Dictionary of parameters to validate
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in params or params[field] is None]
    
    if missing_fields:
        raise ValidationError(
            message=f"Missing required parameters: {', '.join(missing_fields)}",
            field="parameters",
            expected=f"Required fields: {', '.join(required_fields)}"
        )


def validate_id_format(id_value: Any, field_name: str = "id") -> str:
    """Validate ID format and convert to string.
    
    Args:
        id_value: ID value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Validated ID as string
        
    Raises:
        ValidationError: If ID format is invalid
    """
    if not id_value:
        raise ValidationError(
            message=f"{field_name} cannot be empty",
            field=field_name,
            expected="Non-empty string or number"
        )
    
    # Convert to string and validate
    id_str = str(id_value).strip()
    if not id_str:
        raise ValidationError(
            message=f"{field_name} cannot be empty after conversion",
            field=field_name,
            expected="Non-empty string or number"
        )
    
    return id_str
