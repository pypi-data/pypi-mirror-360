# OpenWebUI Client

[![PyPI version](https://img.shields.io/pypi/v/openwebui-client.svg)](https://pypi.org/project/openwebui-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/openwebui-client.svg)](https://pypi.org/project/openwebui-client/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://bemade.github.io/openwebui-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A client library for the OpenWebUI API, compatible with the OpenAI Python SDK but with extensions specific to OpenWebUI features.

## Installation

```bash
pip install openwebui-client
```

## Quick Start

```python
from openwebui_client import OpenWebUIClient

# Initialize client
client = OpenWebUIClient(
    api_key="your_api_key",  # Optional if set in environment variable
    base_url="http://your-openwebui-instance:5000",
    default_model="gpt-4"
)

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]
)
print(response.choices[0].message.content)
```

## Using Function Calling / Tools

The client supports OpenAI-compatible function calling with tools:

```python
# Direct tool usage with chat completions
response = client.chat.completions.create(
    model="your_model",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the current time?"}
    ],
    tools=[
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        }
    ],
)

# Check if the model used tools
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    print(f"Tool called: {tool_call.function.name}")
```

### Using the Tool Registry

The client includes a tool registry for easier management of tools:

```python
# Define tool functions
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather in a given location.

    Args:
        location: The location to get weather for
        unit: The temperature unit to use (celsius or fahrenheit)

    Returns:
        str: A string describing the current weather
    """
    return f"The weather in {location} is sunny and 25°{unit[0]}"

# Register tools with the client
client.tool_registry.register(get_weather)

# Use chat_with_tools for automatic tool handling
response = client.chat_with_tools(
    messages=[{"role": "user", "content": "What's the weather like in Toronto?"}],
    max_tool_calls=5,
)

print(response)  # Will contain the final response after any tool calls
```

## File Operations

```python
# Upload a file to OpenWebUI
uploaded_file = client.files.from_path(file)

# Upload multiple files to OpenWebUI
with open("document.pdf", "rb") as file:
    uploaded_files = client.files.from_paths(
        files=[
            (file1, None),
            (file2, {"xMetaField": "xMetaValue"})
        ]
    )

uploaded_files.append(uploaded_file)

# Use file with chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarize this document for me."}
    ],
    files=uploaded_files
)
```

## Features

- **OpenAI Compatibility**: Use the familiar OpenAI Python SDK interfaces
- **File Upload**: Upload and process files with OpenWebUI
- **File-Aware Chat Completions**: Reference files in chat completions
- **Typed Interface**: Full type hints for better IDE integration

## Documentation

Full documentation is available at [https://bemade.github.io/openwebui-client/](https://bemade.github.io/openwebui-client/)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest

# Build documentation
cd docs
make html
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Projects

- [OpenWebUI](https://github.com/open-webui/open-webui) - A user-friendly WebUI for LLMs
