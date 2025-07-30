from typing import Dict, List, Any, Callable, Type, Optional, get_type_hints
import inspect
import logging
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException, Request
from fastapi.routing import APIRoute
from pydantic import BaseModel, create_model

from .models import Function, Parameter, ParameterType, AuthRequirement
from . import _registry

logger = logging.getLogger("opal_tools_sdk")

class ToolsService:
    """Main class for managing Opal tools."""

    def __init__(self, app: FastAPI):
        """Initialize the tools service.

        Args:
            app: FastAPI application to attach routes to
        """
        self.app = app
        self.router = APIRouter()
        self.functions: List[Function] = []
        self._init_routes()

        # Register in the global registry
        _registry.services.append(self)

        # Debug existing routes
        @app.get("/debug-routes")
        async def debug_routes():
            routes = []
            for route in app.routes:
                if isinstance(route, APIRoute):
                    routes.append({
                        "path": route.path,
                        "name": route.name,
                        "methods": route.methods
                    })
            return {"routes": routes}

    def _init_routes(self) -> None:
        """Initialize the discovery endpoint."""
        @self.router.get("/discovery")
        async def discovery() -> Dict[str, Any]:
            """Return the discovery information for this tools service."""
            return {"functions": [f.to_dict() for f in self.functions]}

        # Include router in app
        self.app.include_router(self.router)

    def _extract_auth_requirements(self, handler: Callable) -> List[AuthRequirement]:
        """Extract auth requirements from a handler function decorated with @requires_auth.

        Args:
            handler: The handler function

        Returns:
            List of AuthRequirement objects
        """
        auth_requirements = []

        # Check if the function is wrapped with @requires_auth
        if hasattr(handler, "__auth_requirements__"):
            # Auth requirements should always be a list
            if isinstance(handler.__auth_requirements__, list):
                for req in handler.__auth_requirements__:
                    auth_requirements.append(AuthRequirement(
                        provider=req.get("provider", ""),
                        scope_bundle=req.get("scope_bundle", ""),
                        required=req.get("required", True)
                    ))

        return auth_requirements

    def register_tool(self,
                     name: str,
                     description: str,
                     handler: Callable,
                     parameters: List[Parameter],
                     endpoint: str,
                     auth_requirements: Optional[List[AuthRequirement]] = None) -> None:
        """Register a tool function.

        Args:
            name: Name of the tool
            description: Description of the tool
            handler: Function that implements the tool
            parameters: List of parameters for the tool
            endpoint: API endpoint for the tool
            auth_requirements: List of authentication requirements (optional)
        """
        print(f"Registering tool: {name} with endpoint: {endpoint}")

        # Extract auth requirements from handler if decorated with @requires_auth
        handler_auth_requirements = self._extract_auth_requirements(handler)

        # If auth_requirements is explicitly provided, it takes precedence
        # Otherwise, use the requirements extracted from the handler
        final_auth_requirements = auth_requirements if auth_requirements else handler_auth_requirements

        function = Function(
            name=name,
            description=description,
            parameters=parameters,
            endpoint=endpoint,
            auth_requirements=final_auth_requirements
        )

        self.functions.append(function)

        # Create a direct route with the app for better control
        @self.app.post(endpoint)
        async def tool_endpoint(request: Request):
            try:
                # Parse JSON body
                body = await request.json()
                print(f"Received request for {endpoint} with body: {body}")

                # Parameters should be in the "parameters" key according to the spec
                # This matches how the tools-mgmt-service calls tools
                if "parameters" in body:
                    params = body["parameters"]
                else:
                    # For backward compatibility with direct test calls
                    print(f"Warning: 'parameters' key not found in request body. Using body directly.")
                    params = body

                # Extract auth data if available
                auth_data = body.get("auth")
                if auth_data:
                    print(f"Auth data provided for provider: {auth_data.get('provider', 'unknown')}")

                # Extract environment data if available
                environment = body.get("environment", {})
                if environment:
                    print(f"Environment data provided: {environment}")

                print(f"Extracted parameters: {params}")

                # Get the parameter model from handler's signature
                sig = inspect.signature(handler)
                param_name = list(sig.parameters.keys())[0]
                param_type = get_type_hints(handler).get(param_name)


                args = []
                kwargs = {}
                if param_type:
                    # Create instance of param model
                    model_instance = param_type(**params)
                    args.append(model_instance)
                else:
                    # Fall back if type hints not available
                    args.append(BaseModel(**params))

                # Check signature to see if it accepts other values

                # TODO: Change this to "auth"
                if auth_param := sig.parameters.get("auth_data"):
                    kwargs[auth_param.name] = auth_data

                if environment_param := sig.parameters.get("environment"):
                    kwargs[environment_param.name] = environment

                result = await handler(*args, **kwargs)

                print(f"Tool {name} returned: {result}")
                return result
            except Exception as e:
                import traceback
                print(f"Error in tool {name}: {str(e)}")
                print(traceback.format_exc())
                raise HTTPException(status_code=500, detail=str(e))

        # Update the route function name and docstring
        tool_endpoint.__name__ = f"tool_{name}"
        tool_endpoint.__doc__ = description
