import inspect
import re
import logging
from typing import Callable, Any, List, Dict, Type, get_origin, get_type_hints, Optional, Union
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from .models import Parameter, ParameterType, AuthRequirement

logger = logging.getLogger("opal_tools_sdk")

def tool(name: str, description: str, auth_requirements: Optional[List[Dict[str, Any]]] = None):
    """Decorator to register a function as an Opal tool.

    Args:
        name: Name of the tool
        description: Description of the tool
        auth_requirements: Authentication requirements (optional)
            Format: [{"provider": "oauth_provider", "scope_bundle": "permissions_scope", "required": True}, ...]
            Example: [{"provider": "google", "scope_bundle": "calendar", "required": True}]

    Returns:
        Decorator function

    Note:
        If your tool requires authentication, define your handler function with two parameters:
        async def my_tool(parameters: ParametersModel, auth_data: Optional[Dict] = None):
            ...
    """
    def decorator(func: Callable):
        # Get the ToolsService instance from the global registry
        from . import _registry

        # Extract parameters from function signature
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        parameters: List[Parameter] = []
        param_model = None

        # Look for a parameter that is a pydantic model (for parameters)
        for param_name, param in sig.parameters.items():
            if param_name in type_hints:
                param_type = type_hints[param_name]
                if hasattr(param_type, '__fields__') or hasattr(param_type, 'model_fields'):  # Pydantic v1 or v2
                    param_model = param_type
                    break

        # If we found a pydantic model, extract parameters
        if param_model:
            model_fields = getattr(param_model, 'model_fields', getattr(param_model, '__fields__', {}))
            for field_name, field in model_fields.items():
                # Get field metadata
                field_info = field.field_info if hasattr(field, 'field_info') else field

                # Determine type
                if hasattr(field, 'outer_type_'):
                    field_type = field.outer_type_
                elif hasattr(field, 'annotation'):
                    field_type = field.annotation
                else:
                    field_type = str

                # Map Python type to Parameter type
                param_type = ParameterType.string
                if field_type == int:
                    param_type = ParameterType.integer
                elif field_type == float:
                    param_type = ParameterType.number
                elif field_type == bool:
                    param_type = ParameterType.boolean
                elif get_origin(field_type) is list:
                    param_type = ParameterType.list
                elif get_origin(field_type) is dict:
                    param_type = ParameterType.dictionary

                # Determine if required
                field_info_extra = getattr(field_info, "json_schema_extra") or {}
                if "required" in field_info_extra:
                    required = field_info_extra["required"]
                else:
                    required = field_info.default is ... if hasattr(field_info, 'default') else True

                # Get description
                description_text = ""
                if hasattr(field_info, 'description'):
                    description_text = field_info.description
                elif hasattr(field, 'description'):
                    description_text = field.description

                parameters.append(Parameter(
                    name=field_name,
                    param_type=param_type,
                    description=description_text,
                    required=required
                ))

                print(f"Registered parameter: {field_name} of type {param_type.value}, required: {required}")
        else:
            print(f"Warning: No parameter model found for {name}")

        endpoint = f"/tools/{name}"

        # Register the tool with the service
        auth_req_list = None
        if auth_requirements:
            auth_req_list = []
            for auth_req in auth_requirements:
                auth_req_list.append(AuthRequirement(
                    provider=auth_req.get("provider", ""),
                    scope_bundle=auth_req.get("scope_bundle", ""),
                    required=auth_req.get("required", True)
                ))

        print(f"Registering tool {name} with endpoint {endpoint}")

        if not _registry.services:
            print("No services registered in registry! Make sure to create ToolsService before decorating functions.")

        for service in _registry.services:
            service.register_tool(
                name=name,
                description=description,
                handler=func,
                parameters=parameters,
                endpoint=endpoint,
                auth_requirements=auth_req_list
            )

        return func

    return decorator
