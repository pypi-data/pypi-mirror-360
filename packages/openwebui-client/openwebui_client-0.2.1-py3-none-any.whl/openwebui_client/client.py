"""OpenWebUI client for interacting with the OpenWebUI API."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from openai import OpenAI
from openai._compat import cached_property
from openai.resources.chat import Chat as OpenAIChat
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_tool_message_param import (
    ChatCompletionToolMessageParam,
)

from .completions import OpenWebUICompletions
from .files import OpenWebUIFiles
from .tools import ToolsRegistry

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class OpenWebUIChat(OpenAIChat):
    """Custom Chat class that uses OpenWebUICompletions."""

    @cached_property
    def completions(self) -> OpenWebUICompletions:
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
        self.tool_registry = ToolsRegistry()

    @cached_property
    def chat(self) -> OpenWebUIChat:
        """Return the custom OpenWebUIChat instance."""
        return OpenWebUIChat(self)

    @cached_property
    def files(self) -> OpenWebUIFiles:
        return OpenWebUIFiles(self)

    def chat_with_tools(
        self,
        messages: List[ChatCompletionMessageParam],
        tools: Optional[Sequence[str]] = None,
        tool_params: Optional[Dict[str, Dict[str, Any]]] = None,
        model: Optional[str] = None,
        max_tool_calls: int = 5,
        files: Iterable[Path] = [],
    ) -> str:
        """Send a chat completion request and handle tool calls automatically.

        This will automatically execute tool calls and include their results
        in subsequent API calls until the model returns a final response.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            tools: List of tool names to use (None for all registered tools)
            tool_params: Optional parameters to pass to the tools when they are called
            model: Model to use (defaults to the client's default model)
            max_tool_calls: Maximum number of tool call rounds to allow
            files: Optional list of Path objects to files that should be included with the request

        Returns:
            The final assistant message content (str) after all tool calls are processed

        Raises:
            RuntimeError: If the maximum number of tool calls is exceeded

        Example:
            >>> client = OpenWebUIClient()
            >>> client.tool_registry.register(get_weather)
            >>> response = client.chat_with_tools(
            ...     messages=[{"role": "user", "content": "What's the weather in Paris?"}],
            ...     max_tool_calls=3
            ... )
            >>> print(response)
        """
        # Initialize tool_params if not provided
        if tool_params is None:
            tool_params = {}

        conversation: List[ChatCompletionMessageParam] = messages.copy()
        file_refs = self.files.from_paths([(file, None) for file in files])

        # Conversation is now a list that we can mutate
        tool_call_count = 0

        # Get tools from the registry
        all_tools = self.tool_registry.get_openai_tools()

        # Filter tools if specific ones were requested
        if tools:
            tool_schemas = [
                tool
                for tool in all_tools
                if tool.get("function", {}).get("name") in tools
            ]
        else:
            # Use all registered tools
            tool_schemas = all_tools

        _logger.debug("Starting chat with tools")
        _logger.debug(
            f"Available tools: {[t['function']['name'] for t in tool_schemas] if tool_schemas else 'None'}"
        )
        _logger.debug(f"Initial messages: {conversation}")

        while tool_call_count < max_tool_calls:
            # Get the next response from the model
            _logger.debug(
                f"Sending request to model (attempt {tool_call_count + 1}/{max_tool_calls})"
            )
            _logger.debug(f"Messages: {conversation}")
            _logger.debug(f"Using model: {model or self.default_model}")
            _logger.debug(
                f"Tools: {json.dumps(tool_schemas, indent=4)} if tool_schemas else 'None'"
            )

            # Debug log the tool dictionaries
            _logger.debug(f"Tool dictionaries: {json.dumps(tool_schemas, indent=2)}")
            # Also log the original tool schemas for comparison

            args = {
                "messages": conversation,
                "model": model or self.default_model,
                "tools": tool_schemas,
                "tool_choice": "auto",
                "files": file_refs,
            }
            _logger.debug(f"Args: {args}")
            response = self.chat.completions.create(**args)

            _logger.debug(f"Received response: {response}")

            # Not running in stream mode, this should never fail. Here for type safety.
            assert isinstance(response, ChatCompletion)
            message = response.choices[0].message

            # If there are no tool calls, we're done
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                _logger.debug("No tool calls in response, ending conversation")
                return message.content or ""
            response = self.chat.completions.create(**args)

            _logger.debug(f"Received response: {response}")

            # Not running in stream mode, this should never fail. Here for type safety.
            assert isinstance(response, ChatCompletion)
            message = response.choices[0].message

            # If there are no tool calls, we're done
            if not hasattr(message, "tool_calls") or not message.tool_calls:
                _logger.debug("No tool calls in response, ending conversation")
                return message.content or ""

            # Process tool calls
            tool_call_count += 1
            _logger.debug(f"Processing tool call {tool_call_count}/{max_tool_calls}")

            for tool_call in message.tool_calls:
                function = tool_call.function
                non_ai_params = tool_params.get(function.name, {})
                _logger.debug(f"Calling tool: {function.name}")
                _logger.debug(f"Arguments: {function.arguments}")
                if non_ai_params:
                    _logger.debug(f"Non-AI parameters: {non_ai_params}")

                # Execute the tool
                try:
                    _logger.debug(
                        f"Calling tool: {function.name} with args: {function.arguments}"
                    )
                    result = self.tool_registry.call_tool(
                        function.name,
                        json.loads(function.arguments),
                        non_ai_params=non_ai_params,
                    )
                    result_str = (
                        json.dumps(result) if not isinstance(result, str) else result
                    )
                    _logger.debug(
                        f"Tool {function.name} returned: {result_str[:200]}..."
                        if len(str(result_str)) > 200
                        else f"Tool {function.name} returned: {result_str}"
                    )
                except Exception as e:
                    result_str = f"Error: {e!s}"
                    _logger.error(
                        f"Error calling tool {function.name}: {e}", exc_info=True
                    )

                # Add the tool response to the conversation
                conversation.append(
                    ChatCompletionToolMessageParam(
                        tool_call_id=tool_call.id,
                        role="tool",
                        content=result_str,
                    )
                )

        raise RuntimeError(f"Maximum number of tool calls ({max_tool_calls}) exceeded")
