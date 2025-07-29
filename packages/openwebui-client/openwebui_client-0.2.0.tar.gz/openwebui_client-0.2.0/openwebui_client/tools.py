from typing import (
    Union,
    Callable,
    Iterable,
    overload,
    Type,
    Dict,
    Any,
    List,
    get_type_hints,
    MutableSequence,
)
from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.shared_params import FunctionDefinition, FunctionParameters
import inspect


def toolify(
    arg: Union[Callable, Iterable[Callable]]
) -> Iterable[ChatCompletionToolParam]:
    """Convert Python functions into OpenAI tool parameters for chat completions.

    This function transforms Python callables into the format required by OpenAI's
    function calling API. It automatically generates JSON Schema definitions for
    function parameters based on type hints and creates proper tool definitions
    that can be passed to OpenAI's API.

    Args:
        arg (Union[Callable, Iterable[Callable]]): A single function or an iterable
            of functions to convert into tool parameters. Each function should have
            proper type hints for its parameters to generate accurate schemas.

    Returns:
        Iterable[ChatCompletionToolParam]: A list of ChatCompletionToolParam objects
            that can be directly passed to OpenAI's API in the 'tools' parameter.

    Examples:
        Converting a single function:
        >>> def add(a: int, b: int) -> int:
        ...     return a + b
        >>> tools = toolify(add)
        >>> # Pass tools to OpenAI API
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "What is 2+2?"}],
        ...     tools=tools
        ... )

        Converting multiple functions:
        >>> def multiply(a: int, b: int) -> int:
        ...     return a * b
        >>> tools = toolify([add, multiply])

    Note:
        - Function docstrings are used as tool descriptions in the API.
        - Type hints are used to generate parameter schemas.
        - For complex types, consider using more explicit schema definitions.
    """

    if callable(arg):
        return [_convert(arg)]
    else:
        return [_convert(func) for func in arg]


def _convert(func: Callable) -> ChatCompletionToolParam:
    """
    Convert a Python function into an OpenAI tool parameter.
    """
    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=func.__name__,
            description=func.__doc__ or "",
            parameters=_get_parameters_schema(func),
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


def _get_parameters_schema(func: Callable) -> FunctionParameters:
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

    for param_name, param in sig.parameters.items():
        # Skip 'self' and 'cls' parameters
        if param_name in ("self", "cls"):
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
