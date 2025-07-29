"""Tests for the OpenWebUICompletions class."""

import pytest
from unittest.mock import patch, MagicMock

from openai._types import NOT_GIVEN
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage
from openai.types.file_object import FileObject
from openai.types.chat.chat_completion import Choice
from openwebui_client.completions import OpenWebUICompletions


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    client = MagicMock()
    # Set up base_url and api_key to be proper strings
    client.base_url = "https://test.com"
    client.api_key = "test_api_key"

    # Create a proper ChatCompletion with dictionary structure instead of MagicMock objects
    client.post.return_value = ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="Test response", role="assistant"
                ),
            )
        ],
        created=1619990475,
        model="gpt-4",
        object="chat.completion",
        usage=CompletionUsage(completion_tokens=10, prompt_tokens=20, total_tokens=30),
    )
    return client


@patch("requests.post")
def test_create_with_files(mock_post, mock_client):
    """Test create method with files parameter."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": "test-id",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {"content": "Test response", "role": "assistant"},
            }
        ],
        "created": 1619990475,
        "model": "gpt-4",
        "object": "chat.completion",
        "usage": {
            "completion_tokens": 10,
            "prompt_tokens": 20,
            "total_tokens": 30,
        },
    }
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Initialize completions
    completions = OpenWebUICompletions(client=mock_client)

    # Create a proper mock file
    mock_file = MagicMock(spec=FileObject)
    mock_file.id = "file-123"
    files = [mock_file]

    # Call create with files
    response = completions.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4",
        files=files,
    )

    # Check that requests.post was called
    mock_post.assert_called_once()

    # Check that the post was called with the right URL and data format
    args, kwargs = mock_post.call_args
    assert args[0] == "https://test.com/chat/completions"

    # Verify files were properly formatted in the JSON payload
    assert "files" in kwargs["json"]
    assert kwargs["json"]["files"][0]["id"] == "file-123"
    assert kwargs["json"]["files"][0]["type"] == "file"

    # Verify the response was properly constructed
    assert isinstance(response, ChatCompletion)
    assert response.choices[0].message.content == "Test response"


def test_create_without_files(mock_client):
    """Test create method without files parameter."""
    completions = OpenWebUICompletions(client=mock_client)

    # Call create without files parameter
    response = completions.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4",
    )

    # For the no-files case, super().create() is called instead, so we don't check
    # post method arguments directly. Just make sure we got the right response.

    # Check that we got a response
    assert isinstance(response, ChatCompletion)
    assert response.choices[0].message.content == "Test response"


def test_create_with_not_given_params(mock_client):
    """Test that NOT_GIVEN parameters are handled correctly."""
    completions = OpenWebUICompletions(client=mock_client)

    # Call create with some NOT_GIVEN parameters
    response = completions.create(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4",
        temperature=1.0,
        max_tokens=NOT_GIVEN,
        stop=NOT_GIVEN,
    )

    # For the 'with NOT_GIVEN params' case, super().create() is called instead, so we don't check
    # post method arguments directly. Just make sure we got the right response.

    # Check that we got a response
    assert isinstance(response, ChatCompletion)
    assert response.choices[0].message.content == "Test response"
