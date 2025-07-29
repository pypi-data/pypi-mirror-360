"""Integration tests for the weather bot example with real API calls.

This module contains integration tests for the weather bot example that make actual
API calls to the OpenAI API. These tests verify that the tool registration and
function calling functionality works as expected with the real API.
"""

import logging
import os
import sys
from typing import Any, Dict, List, Optional

import pytest

from openwebui_client.client import OpenWebUIClient

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# Set up logging
_logger = logging.getLogger(__name__)

# Skip if we don't have the required environment variables
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENWEBUI_API_KEY"),
    reason="OPENWEBUI_API_KEY environment variable not set",
)

model = os.getenv("OPENWEBUI_DEFAULT_MODEL") or "MS.qwen3:32b-q8_0"


# Define our test tools
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location.

    Args:
        location: The location to get weather for
        unit: The temperature unit to use (celsius or fahrenheit)

    Returns:
        str: A string describing the current weather
    """
    return f"The weather in {location} is 22 degrees {unit} and sunny."


def get_forecast(location: str, days: int = 1) -> str:
    """Get a weather forecast for a location.

    Args:
        location: The location to get the forecast for
        days: Number of days to forecast

    Returns:
        str: A string describing the forecast
    """
    return f"The forecast for {location} for the next {days} days is sunny."


def print_message(
    role: str,
    content: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Print a formatted message with role and content.

    Args:
        role: The role of the message sender (user, assistant, etc.)
        content: The content of the message
        tool_calls: Optional list of tool calls associated with the message
    """
    print(f"{role.upper()}: {content}")

    if tool_calls:
        print("  Tool calls:")
        for call in tool_calls:
            func_name = call.get("name")
            func_args = call.get("arguments")
            print(f"  - {func_name}: {func_args}")

    print("=" * 80)


@pytest.fixture
def client():
    """Create a client connected to a real OpenWebUI instance."""
    return OpenWebUIClient(
        api_key=os.environ.get("OPENWEBUI_API_KEY"),
        base_url=os.environ.get("OPENWEBUI_API_BASE", ""),
        default_model=model,
    )


def test_tool_param_registration(client):
    tool_registry = client.tool_registry
    tool_registry.register(get_weather)
    tool_registry.register(get_forecast)
    assert len(tool_registry._tools) == 2
    expected_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": get_weather.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "",
                        },
                        "unit": {
                            "type": "string",
                            "description": "",
                            "default": "celsius",
                        },
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_forecast",
                "description": get_forecast.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "",
                        },
                        "days": {
                            "type": "integer",
                            "description": "",
                            "default": 1,
                        },
                    },
                    "required": ["location"],
                },
            },
        },
    ]

    assert tool_registry.get_openai_tools() == expected_tools


def test_weather_bot_integration(client: OpenWebUIClient) -> None:
    """Test the weather bot with the real API using OpenAIClient.

    Args:
        tool_registry: The tool registry instance to use for testing
    """
    tool_registry = client.tool_registry

    # Register the tools
    tool_registry.register(get_weather)
    tool_registry.register(get_forecast)

    # Print registered tools for debugging
    print("\n" + "#" * 40 + " REGISTERED TOOLS " + "#" * 40)
    print("\nTool registry contents:")
    for _name, tool_info in tool_registry._tools.items():
        print("#" * 80)
        print(f"Tool: {_name}")
        print("Type:", type(tool_info[1]).__name__)
        print(f"Function: {tool_info[1]}")
        print(f"Schema: {tool_info[0]}")
    print("#" * 80 + "\n")

    # Test 1: Simple weather query
    print("\n" + "=" * 40 + " TEST 1: SIMPLE WEATHER QUERY " + "=" * 40)
    user_message = "What's the weather like in Toronto?"
    print_message("User", user_message)

    response = client.chat_with_tools(
        messages=[{"role": "user", "content": user_message}],
        max_tool_calls=5,
    )

    print_message("Assistant", response)

    # Verify the response includes the expected weather information
    assert response is not None
    assert "22" in response  # Should include the temperature from our mock
    assert "Toronto" in response

    # Test 2: Complex query using multiple tools
    print("\n" + "=" * 40 + " TEST 2: COMPLEX QUERY " + "=" * 40)
    user_message = (
        "What's the weather like in Toronto and what's the forecast for tomorrow?"
    )
    print_message("User", user_message)

    response = client.chat_with_tools(
        messages=[{"role": "user", "content": user_message}],
        max_tool_calls=5,
    )

    print_message("Assistant", response)

    # Verify we got a response that includes both current weather and forecast
    assert response is not None
    assert "22" in response  # Current temp
    assert "forecast" in response.lower()
