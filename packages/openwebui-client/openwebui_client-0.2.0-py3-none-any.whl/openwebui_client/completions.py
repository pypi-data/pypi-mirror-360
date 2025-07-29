"""OpenWebUI completions class for handling file parameters in chat completions."""

import logging
import httpx
from typing import (
    Collection,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Union,
)
from openai.types.file_object import FileObject
from openai._types import Body, Headers, NotGiven, Query, NOT_GIVEN
from openai._streaming import Stream
from openai.resources.chat import Completions
from openai.types.shared.chat_model import ChatModel
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    completion_create_params,
    ChatCompletionChunk,
)
from openai.types.shared_params.metadata import Metadata
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.chat.chat_completion_audio_param import ChatCompletionAudioParam
from openai.types.chat.chat_completion_prediction_content_param import (
    ChatCompletionPredictionContentParam,
)
from openai.types.chat.chat_completion_stream_options_param import (
    ChatCompletionStreamOptionsParam,
)
from openai._utils import required_args

_logger = logging.getLogger(__name__)


class OpenWebUICompletions(Completions):
    """Extended Completions class that supports the 'files' parameter for OpenWebUI."""

    def __init__(self, client):
        """Initialize the OpenWebUI completions handler.

        Args:
            client: The OpenAI client to use for requests
        """
        # Pass the full OpenAI client, not just its internal client
        super().__init__(client=client)

    @required_args(["messages", "model"], ["messages", "model", "stream"])
    def create(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str, ChatModel],
        audio: Optional[ChatCompletionAudioParam] | NotGiven = NOT_GIVEN,
        files: Optional[Collection[FileObject]] | NotGiven = NOT_GIVEN,
        frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN,
        logprobs: Optional[bool] | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        modalities: Optional[List[Literal["text", "audio"]]] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: bool | NotGiven = NOT_GIVEN,
        prediction: (
            Optional[ChatCompletionPredictionContentParam] | NotGiven
        ) = NOT_GIVEN,
        presence_penalty: Optional[float] | NotGiven = NOT_GIVEN,
        reasoning_effort: Optional[ReasoningEffort] | NotGiven = NOT_GIVEN,
        response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: Optional[int] | NotGiven = NOT_GIVEN,
        service_tier: (
            Optional[Literal["auto", "default", "flex"]] | NotGiven
        ) = NOT_GIVEN,
        stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        stream_options: (
            Optional[ChatCompletionStreamOptionsParam] | NotGiven
        ) = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN,
        top_logprobs: Optional[int] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        web_search_options: (
            completion_create_params.WebSearchOptions | NotGiven
        ) = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """Create a chat completion with support for the 'files' parameter.

        This overrides the standard create method to handle the 'files' parameter
        that OpenWebUI supports but is not in the standard OpenAI API.

        Args:
            messages: A list of messages comprising the conversation so far.
            model: ID of the model to use.
            files: A list of file IDs to attach to the completion request (OpenWebUI specific).

            # Standard OpenAI parameters, see OpenAI API docs for details
            audio: Audio input parameters.
            frequency_penalty: Penalizes repeated tokens according to frequency.
            function_call: Controls how the model uses functions.
            functions: Functions the model may call to interact with external systems.
            logit_bias: Modifies likelihood of specific tokens appearing in completion.
            logprobs: Whether to return log probabilities of the output tokens.
            max_completion_tokens: Maximum number of tokens that can be generated for completions.
            max_tokens: Maximum number of tokens to generate in the response.
            metadata: Additional metadata to include in the completion.
            modalities: List of modalities the model should handle.
            n: How many completions to generate for each prompt.
            parallel_tool_calls: Whether function and tool calls should be made in parallel.
            prediction: Control specifics of prediction content.
            presence_penalty: Penalizes new tokens based on their presence so far.
            reasoning_effort: Controls how much effort the model spends reasoning.
            response_format: Format in which the model should generate responses.
            seed: Enables deterministic sampling for consistent outputs.
            service_tier: The service tier to use for the request.
            stop: Sequences where the API will stop generating further tokens.
            store: Whether to persist completion for future retrieval.
            stream: Whether to stream back partial progress.
            stream_options: Options for streaming responses.
            temperature: Controls randomness in the response.
            tool_choice: Controls how the model selects tools.
            tools: List of tools the model may call.
            top_logprobs: Number of log probabilities to return per token.
            top_p: Controls diversity via nucleus sampling.
            user: Unique identifier representing your end-user.
            web_search_options: Options to configure web search behavior.

            # Additional parameters for HTTP requests
            extra_headers: Additional HTTP headers.
            extra_query: Additional query parameters.
            extra_body: Additional body parameters.
            timeout: Request timeout in seconds.

        Returns:
            A ChatCompletion object containing the model's response.
        """
        # Extract and handle the 'files' parameter specially
        # Handle special case for files parameter
        if files:
            _logger.debug(f"Including {len(files)} files in chat completion request")

            # When files are provided, we need to handle the request manually
            # because the OpenAI API doesn't support this parameter

            # Create a dictionary of parameters for the API call, excluding special parameters
            request_data = {
                k: v
                for k, v in locals().items()
                if k != "self" and (k is not None or k != NOT_GIVEN) and "__" not in k
            }

            # Make the request using direct HTTP request
            # OpenWebUI requires files as a parameter in the form data
            import json
            import requests

            # Extract the base URL from the client
            base_url = str(self._client.base_url).rstrip("/")

            # Construct the full URL - try the api prefix again
            url = f"{base_url}/chat/completions"

            # Set up authentication headers and content type for JSON
            headers = {
                "Authorization": f"Bearer {self._client.api_key}",
                "Content-Type": "application/json",
            }

            # Let's try another approach - create a JSON payload with all parameters
            # Then add that payload as 'json' parameter in form data
            payload = {
                "model": model,
                "messages": [
                    {"role": m["role"], "content": m.get("content")} for m in messages
                ],
                "max_tokens": max_tokens if max_tokens is not NOT_GIVEN else None,
            }

            # Add any additional OpenAI parameters to the payload
            for key, value in request_data.items():
                if (
                    key not in ["self", "files", "messages", "model", "max_tokens"]
                    and value is not NOT_GIVEN
                    and value is not None
                ):
                    payload[key] = value

            # Add file references if provided
            # Try sending file IDs in the format OpenWebUI expects
            if files:
                # Based on error messages, let's try a different format
                # Check OpenWebUI's API source to see expected format
                file_ids = [f.id for f in files]

                # Format files exactly as shown in OpenWebUI's API docs
                formatted_files = [{"type": "file", "id": f.id} for f in files]
                payload["files"] = formatted_files

                # Log additional debug info about the file objects
                for i, file in enumerate(files):
                    _logger.debug(
                        f"File {i} details: id={file.id}, filename={getattr(file, 'filename', None)}"
                    )

            # No need for form data structure, send the payload directly as JSON

            # Print detailed request information
            _logger.debug(f"CHAT API - URL: {url}")
            _logger.debug(f"CHAT API - Headers: {headers}")
            _logger.debug(f"CHAT API - Payload: {payload}")

            # Make the HTTP request with JSON payload
            http_response = requests.post(url, headers=headers, json=payload)

            # Print response details
            _logger.debug(f"CHAT API - Response Status: {http_response.status_code}")
            _logger.debug(f"CHAT API - Response Headers: {dict(http_response.headers)}")
            _logger.debug(
                f"CHAT API - Response Body: {http_response.text[:500]}..."
                if len(http_response.text) > 500
                else f"CHAT API - Response Body: {http_response.text}"
            )

            # Raise an exception for any HTTP error
            http_response.raise_for_status()

            # Parse the JSON response
            response_data = http_response.json()

            # Convert the response to a ChatCompletion object
            response = ChatCompletion(**response_data)
            return response
        else:
            # Without files, delegate to the parent implementation
            # Just don't pass the 'files' parameter which is None anyway
            standard_kwargs = {
                k: v
                for k, v in locals().items()
                if k not in ["self", "files"] and "__" not in k
            }
            return super().create(**standard_kwargs)
