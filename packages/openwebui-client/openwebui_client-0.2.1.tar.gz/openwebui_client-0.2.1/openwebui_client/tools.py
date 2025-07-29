import inspect
import logging
from typing import (
    Any,
    Callable,
    Dict,
    List,
    MutableSequence,
    Optional,
    Tuple,
    Type,
    get_type_hints,
)

from openai.types.chat.chat_completion import ChatCompletion
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition, FunctionParameters

_logger = logging.getLogger(__name__)


def _convert(
    func: Callable,
    name: Optional[str] = None,
    description: str = "",
    non_ai_params: Optional[List[str]] = None,
) -> ChatCompletionToolParam:
    """
    Convert a Python function into an OpenAI tool parameter.
    """
    local_non_ai_params = non_ai_params.copy() if non_ai_params is not None else []
    if not description:
        description = func.__doc__ or ""

    if local_non_ai_params:
        non_ai_param_joined = "\\n- ".join(local_non_ai_params)
        description += f"""

        Non-AI parameters (do not use these):
        {non_ai_param_joined}
        """

    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=name or func.__name__,
            description=description,
            parameters=_get_parameters_schema(func, local_non_ai_params),
        ),
    )


def _type_to_schema(type_: Type[Any]) -> Dict[str, Any]:
    """Convert Python type to OpenAPI schema.

    This method maps Python types to their corresponding JSON Schema types.
    It handles basic types (str, int, float, bool) as well as generic
    types from the typing module (List, Dict, etc.).

    Args:
        type_ (Type): The Python type to convert to a schema.

    Returns:
        dict: A dictionary representing the JSON Schema for the type.

    Note:
        For complex or custom types, the type will be converted to a string
        representation in the schema. For more precise control over the schema,
        consider using Pydantic models or explicitly defining the schema.
    """
    if type_ is str:
        return {"type": "string"}
    elif type_ is int:
        return {"type": "integer"}
    elif type_ is float:
        return {"type": "number"}
    elif type_ is bool:
        return {"type": "boolean"}
    elif type_ is list or type_ is List:
        return {"type": "array", "items": {}}
    elif type_ is dict or type_ is Dict:
        return {"type": "object"}
    else:
        # For custom types or more complex types, default to string
        # and include the type name in the description
        type_name = getattr(type_, "__name__", str(type_))
        return {
            "type": "string",
            "description": f"Expected type: {type_name}",
            "x-python-type": type_name,
        }


def _get_parameters_schema(
    func: Callable,
    non_ai_params: List[str] = None,
) -> FunctionParameters:
    """Generate OpenAPI schema for function parameters.

    This method inspects the function signature and type hints to generate
    a JSON Schema that describes the function's parameters in a format
    compatible with OpenAI's function calling API.

    Args:
        func (Callable): The function for which to generate the parameter schema.

    Returns:
        dict: A dictionary containing the OpenAPI schema for the function's
            parameters.

    Example:
        >>> def example(a: int, b: str = "default") -> None:
        ...     pass
        >>> schema = tool_registry._get_parameters_schema(example)
        >>> print(schema)
        {'type': 'object', 'properties': {'a': {'type': 'integer', 'description': ''}, 'b': {'type': 'string', 'description': '', 'default': 'default'}}, 'required': ['a']}  # noqa: E501
    """
    params: Dict[str, Any] = {
        "type": "object",
        "properties": {},
        "required": [],
    }
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    # Initialize local non_ai_params list
    # Extract parameter information
    sig = inspect.signature(func)
    required: List[str] = []
    type_hints = get_type_hints(func)

    for param_name, param in sig.parameters.items():
        # Skip 'self' and 'cls' parameters
        if param_name in ("self", "cls") or param_name in non_ai_params:
            continue

        param_type = type_hints.get(param_name, str)
        param_schema = _type_to_schema(param_type)
        param_schema["description"] = ""

        if param.default != inspect.Parameter.empty:
            param_schema["default"] = param.default
        else:
            required = params["required"]
            if isinstance(required, MutableSequence):
                required.append(param_name)

        params["properties"][param_name] = param_schema

    return params


def call_tools_from_response(response: ChatCompletion) -> Any:
    if response.choices:
        choice = response.choices[0]
        if choice.message.tool_calls:
            for _tool_call in choice.message.tool_calls:
                pass


class ToolsRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tuple[ChatCompletionToolParam, Callable]] = {}

    def register(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: str = "",
        non_ai_params: List[str] = None,
    ) -> None:
        tool_name = name or func.__name__
        tool = _convert(
            func,
            name=tool_name,
            description=description,
            non_ai_params=non_ai_params,
        )
        self._tools[tool_name] = (tool, func)

    def _get_parameter_info(
        self,
        param: inspect.Parameter,
        param_type: Type[Any],
    ) -> Dict[str, Any]:
        """Get parameter information for the schema.

        Args:
            param: The parameter to get info for
            param_type: The type of the parameter

        Returns:
            Dictionary containing parameter schema information
        """
        param_info: Dict[str, Any] = {}

        # Handle different parameter types
        if param_type in (str, int, float, bool):
            param_info["type"] = param_type.__name__
        elif param_type == list:
            param_info.update({"type": "array", "items": {"type": "string"}})
        elif param_type == dict:
            param_info["type"] = "object"
        else:
            param_info["type"] = "string"

        # Add description if available
        if param.annotation != inspect.Parameter.empty:
            param_info["description"] = str(param.annotation)

        # Add default value if available
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default

        return param_info

    def _get_type_name(self, type_: Type[Any]) -> str:
        """Convert Python type to JSON schema type name.

        Args:
            type_: The Python type to convert

        Returns:
            String representing the JSON schema type
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
        }
        return type_map.get(type_, "string")

    def get_tool(self, name: str) -> Optional[Callable[..., Any]]:
        """Get a registered tool by name.

        Args:
            name: The name of the tool

        Returns:
            The registered function or None if not found
        """
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[1]

    def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
        non_ai_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Call a registered tool by name with the given arguments.

        This method executes a registered tool with the provided arguments and
        returns the result.

        Args:
            name: The name of the tool to call.
            arguments: A dictionary of arguments to pass to the tool.
            non_ai_params: Optional dictionary of non-AI parameters to pass to the tool.
                These parameters are not part of the AI's function calling interface
                but can be used to pass system-level dependencies.


        Returns:
            The result of the tool execution.

        Raises:
            ToolError: If the tool is not found or if there's an error during execution.
        """
        if non_ai_params is None:
            non_ai_params = {}

        tool = self.get_tool(name)
        if not tool:
            raise ToolError(f"Tool '{name}' not found")

        try:
            # Merge non_ai_params with the arguments
            kwargs = {**arguments, **non_ai_params}
            return tool(**kwargs)
        except Exception as e:
            raise ToolError(f"Error calling tool '{name}': {e}") from e

    def get_openai_tools(self) -> List[ChatCompletionToolParam]:
        """Get all registered tools in OpenAI format.

        Returns:
            List[Dict[str, Any]]: A list of tool definitions in OpenAI format
        """
        return [tool[0] for tool in self._tools.values()]

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()

    # Make the registry callable as a decorator
    tool = register


class ToolError(Exception):
    """Exception raised for errors in tool registration or execution.

    This exception is raised when there are issues with tool registration,
    schema generation, or during tool execution.
    """
