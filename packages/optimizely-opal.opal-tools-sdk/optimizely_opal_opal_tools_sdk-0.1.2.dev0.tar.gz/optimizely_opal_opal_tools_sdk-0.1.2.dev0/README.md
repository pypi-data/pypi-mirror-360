# Opal Tools SDK for Python

This SDK simplifies the creation of tools services compatible with the Opal Tools Management Service.

## Features

- Easy definition of tool functions with decorators
- Automatic generation of discovery endpoints
- Parameter validation and type checking
- Authentication helpers
- FastAPI integration

## Installation

```bash
pip install optimizely-opal.opal-tools-sdk
```

Note: While the package is installed as `optimizely-opal.opal-tools-sdk`, you'll still import it in your code as `opal_tools_sdk`:

```python
# Import using the package name
from opal_tools_sdk import ToolsService, tool
```

## Usage

```python
from opal_tools_sdk import ToolsService, tool
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)

class WeatherParameters(BaseModel):
    location: str
    units: str = "metric"

@tool("get_weather", "Gets current weather for a location")
async def get_weather(parameters: WeatherParameters):
    # Implementation...
    return {"temperature": 22, "condition": "sunny"}

# Discovery endpoint is automatically created at /discovery
```

## Authentication

The SDK provides two ways to require authentication for your tools:

### 1. Using the `@requires_auth` decorator

```python
from opal_tools_sdk import ToolsService, tool
from opal_tools_sdk.auth import requires_auth
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()
tools_service = ToolsService(app)

class CalendarParameters(BaseModel):
    date: str
    timezone: str = "UTC"

# Single authentication requirement
@requires_auth(provider="google", scope_bundle="calendar", required=True)
@tool("get_calendar_events", "Gets calendar events for a date")
async def get_calendar_events(parameters: CalendarParameters, auth_data=None):
    # The auth_data parameter contains authentication information
    token = auth_data.get("credentials", {}).get("token", "")

    # Use the token to make authenticated requests
    # ...

    return {"events": ["Meeting at 10:00", "Lunch at 12:00"]}

# Multiple authentication requirements (tool can work with either provider)
@requires_auth(provider="google", scope_bundle="calendar", required=True)
@requires_auth(provider="microsoft", scope_bundle="outlook", required=True)
@tool("get_calendar_availability", "Check calendar availability")
async def get_calendar_availability(parameters: CalendarParameters, auth_data=None):
    provider = auth_data.get("provider", "")
    token = auth_data.get("credentials", {}).get("token", "")

    if provider == "google":
        # Use Google Calendar API
        pass
    elif provider == "microsoft":
        # Use Microsoft Outlook API
        pass

    return {"available": True, "provider_used": provider}
```

### 2. Specifying auth requirements in the `@tool` decorator

```python
@tool(
    "get_email",
    "Gets emails from the user's inbox",
    auth_requirements=[
        {"provider": "google", "scope_bundle": "gmail", "required": True}
    ]
)
async def get_email(parameters: EmailParameters, auth_data=None):
    # Implementation...
    return {"emails": ["Email 1", "Email 2"]}
```

## Documentation

See full documentation for more examples and configuration options.
