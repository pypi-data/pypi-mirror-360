"""OpenWebUI client for interacting with the OpenWebUI API."""

import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI
from openai._streaming import Stream
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from openai.types.chat.completion_create_params import ResponseFormat
from openai.resources.chat import Chat as OpenAIChat
from openai._compat import cached_property

from httpx import Response

from .completions import OpenWebUICompletions
from .files import OpenWebUIFiles

_logger = logging.getLogger(__name__)


class OpenWebUIChat(OpenAIChat):
    """Custom Chat class that uses OpenWebUICompletions."""

    @cached_property
    def completions(self):
        return OpenWebUICompletions(self._client)


class OpenWebUIClient(OpenAI):
    """Client for interacting with the OpenWebUI API.

    This client extends the OpenAI client with OpenWebUI-specific
    features like file attachments in chat completions.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:5000",
        default_model: str = "gpt-4",
        **kwargs: Any,
    ) -> None:
        """Initialize the OpenWebUI client.

        Args:
            api_key: Your OpenWebUI API key
            base_url: Base URL for the API (defaults to OpenWebUI's local instance)
            default_model: Default model to use for completions
            **kwargs: Additional arguments to pass to the OpenAI client
        """
        # OpenWebUI has different endpoint patterns than OpenAI
        # Remove trailing slash if present
        if base_url.endswith("/"):
            base_url = base_url[:-1]

        # Initialize the parent OpenAI class
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)

        # Store additional configuration
        self.default_model = default_model
        self.base_url = base_url

    @cached_property
    def chat(self):
        """Return the custom OpenWebUIChat instance."""
        return OpenWebUIChat(self)

    @cached_property
    def files(self):
        return OpenWebUIFiles(self)

    def chat_completion_with_files(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        files: Optional[List[bytes]] = None,
        temperature: Optional[float] = None,
        response_format: Optional[ResponseFormat] = None,
        **kwargs: Any,
    ) -> ChatCompletion | Stream[ChatCompletionChunk] | Response:
        """Create a chat completion with optional file attachments.

        Args:
            messages: The messages to send to the API
            model: The model to use (defaults to self.default_model)
            files: Optional list of file bytes to attach to the request
            temperature: Optional temperature parameter
            response_format: Optional response format
            **kwargs: Additional arguments to pass to the API

        Returns:
            The chat completion response
        """
        # Use default model if not specified
        if model is None:
            model = self.default_model

        # Build request parameters
        params = {"model": model, "messages": messages, **kwargs}

        if temperature is not None:
            params["temperature"] = temperature

        if response_format is not None:
            params["response_format"] = response_format

        # Handle file uploads if provided
        if files:
            # Make request with file attachments
            file_data = [("files", file) for file in files]

            # OpenWebUI uses a different endpoint format
            endpoint = "/api/openai/chat/completions"

            # Send as multipart/form-data
            headers = {"Content-Type": "multipart/form-data"}
            response = self._client.post(
                endpoint, json=params, files=file_data, headers=headers
            )
        else:
            # Use standard completions endpoint
            response = self.chat.completions.create(**params)

        return response
