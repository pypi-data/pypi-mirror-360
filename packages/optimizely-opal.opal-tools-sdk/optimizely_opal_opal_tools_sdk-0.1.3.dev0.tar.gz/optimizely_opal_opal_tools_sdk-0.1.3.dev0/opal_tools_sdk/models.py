from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

class ParameterType(str, Enum):
    """Types of parameters supported by Opal tools."""
    string = "string"
    integer = "integer"
    number = "number"
    boolean = "boolean"
    list = "array"  # Changed to match main service expectation
    dictionary = "object"  # Standard JSON schema type

@dataclass
class Parameter:
    """Parameter definition for an Opal tool."""
    name: str
    param_type: ParameterType
    description: str
    required: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        return {
            "name": self.name,
            "type": self.param_type.value,
            "description": self.description,
            "required": self.required
        }

@dataclass
class AuthRequirement:
    """Authentication requirements for an Opal tool."""
    provider: str  # e.g., "google", "microsoft"
    scope_bundle: str  # e.g., "calendar", "drive"
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        return {
            "provider": self.provider,
            "scope_bundle": self.scope_bundle,
            "required": self.required
        }

@dataclass
class Function:
    """Function definition for an Opal tool."""
    name: str
    description: str
    parameters: List[Parameter]
    endpoint: str
    auth_requirements: Optional[List[AuthRequirement]] = None
    http_method: str = "POST"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for the discovery endpoint."""
        result = {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "endpoint": self.endpoint,
            "http_method": self.http_method
        }

        if self.auth_requirements:
            result["auth_requirements"] = [auth.to_dict() for auth in self.auth_requirements]

        return result
