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

# Upload a file to OpenWebUI
with open("document.pdf", "rb") as file:
    uploaded_file = client.files.upload(file=file, purpose="assistant")

# Use file with chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Summarize this document for me."}
    ],
    file_ids=[uploaded_file.id]
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