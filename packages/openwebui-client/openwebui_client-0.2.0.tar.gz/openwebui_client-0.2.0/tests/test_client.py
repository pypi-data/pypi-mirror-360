"""Tests for the OpenWebUIClient class."""

import pytest
from unittest.mock import patch, MagicMock

from openwebui_client.client import OpenWebUIClient
from openwebui_client.completions import OpenWebUICompletions
from openwebui_client.files import OpenWebUIFiles


def test_client_initialization():
    """Test that the client is initialized correctly."""
    client = OpenWebUIClient(api_key="test-key", base_url="http://test-url.com")

    assert client.api_key == "test-key"
    # Base URL should not have /v1 appended automatically
    assert client.base_url == "http://test-url.com"
    assert isinstance(client.chat.completions, OpenWebUICompletions)
    assert isinstance(client.files, OpenWebUIFiles)


def test_base_url_handling():
    """Test that the base URL is handled correctly."""
    # Test with trailing slash - should be removed
    client1 = OpenWebUIClient(api_key="test-key", base_url="http://test-url.com/")
    assert client1.base_url == "http://test-url.com"

    # Test with no trailing slash
    client2 = OpenWebUIClient(api_key="test-key", base_url="http://test-url.com")
    assert client2.base_url == "http://test-url.com"


def test_chat_property():
    """Test that the chat property works correctly."""
    client = OpenWebUIClient(api_key="test-key")

    # Access the chat property
    chat = client.chat
    
    # Verify it has the completions attribute with our custom implementation
    assert hasattr(chat, "completions")
    assert isinstance(chat.completions, OpenWebUICompletions)
