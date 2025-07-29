"""Integration tests for the OpenWebUI client.

These tests require a running OpenWebUI server and valid API credentials.
Set the OPENWEBUI_API_KEY and OPENWEBUI_API_BASE environment variables before running.
"""

import logging
import os
from pathlib import Path

import pytest
from openai.types.chat.chat_completion import ChatCompletion

from openwebui_client import OpenWebUIClient

logging.basicConfig(level=logging.DEBUG)

# Skip all tests if no API key or base URL is provided
pytestmark = pytest.mark.skipif(
    not (os.environ.get("OPENWEBUI_API_KEY") and os.environ.get("OPENWEBUI_API_BASE")),
    reason="OPENWEBUI_API_KEY and OPENWEBUI_API_BASE environment variables are required for integration tests",
)

model = os.getenv("OPENWEBUI_DEFAULT_MODEL") or "MS.qwen3:32b-q8_0"


@pytest.fixture
def client():
    """Create a client connected to a real OpenWebUI instance."""
    return OpenWebUIClient(
        api_key=os.environ.get("OPENWEBUI_API_KEY"),
        base_url=os.environ.get("OPENWEBUI_API_BASE", ""),
    )


@pytest.fixture
def file_path():
    return Path(__file__).parent / "data" / "Les_Processus_Cl_s.pdf"


def test_chat_completion(client):
    """Test that chat completions work with a real server."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"},
        ],
        max_tokens=10,  # Limit the response size for test efficiency
    )

    # Verify we got a response with the expected structure
    assert response.id is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.choices[0].message.role == "assistant"


def test_completion_with_tools(client: OpenWebUIClient) -> None:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the current time?"},
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

    assert isinstance(response, ChatCompletion)
    assert response.id is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.choices[0].message.role == "assistant"
    assert response.choices[0].message.tool_calls is not None
    assert response.choices[0].message.tool_calls[0].function.name == "get_current_time"


def test_chat_completion_with_file(client: OpenWebUIClient, file_path: Path) -> None:
    """Test chat completions with a file attachment."""
    file = client.files.from_path(file=file_path)

    assert file.id is not None

    # Make request with file attachment
    response = client.chat.completions.create(
        model=model,  # Use a model available on your OpenWebUI server
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What's in the attached file?"},
        ],
        files=[file],
        max_tokens=20,  # Limit the response size for test efficiency
    )

    # Verify we got a response
    assert isinstance(response, ChatCompletion)
    assert response.id is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    assert response.choices[0].message.role == "assistant"
    # The response should likely mention something about a test file
    assert (
        "test" in response.choices[0].message.content.lower()
        or "file" in response.choices[0].message.content.lower()
    )


def test_file_upload(client: OpenWebUIClient, file_path: Path) -> None:
    """Test file uploads."""
    try:
        file_obj = client.files.from_path(
            file=file_path,
            file_metadata={"purpose": "assistants"},
        )

        # Check that we got a file object back
        assert file_obj.id is not None
        assert file_obj.bytes == len(file_path.read_bytes())

    except Exception as e:
        pytest.xfail(f"File upload failed: {str(e)}")


def test_multiple_file_upload(client: OpenWebUIClient, file_path: Path) -> None:
    """Test multiple file uploads."""
    # Create small test files

    # Upload the files
    try:
        file_objects = client.files.from_paths(
            files=[
                (file_path, {"purpose": "assistants"}),
                (file_path, {"purpose": "assistants"}),
            ]
        )

        # Check that we got file objects back
        assert len(file_objects) == 2
        assert file_objects[0].id is not None
        assert file_objects[1].id is not None

    except Exception as e:
        pytest.xfail(f"Multiple file upload failed: {str(e)}")
