========
Examples
========

Basic Chat Completion
--------------------

.. code-block:: python

    from openwebui_client import OpenWebUIClient

    client = OpenWebUIClient(
        api_key="your-openwebui-api-key",
        base_url="http://localhost:5000"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What can you tell me about OpenWebUI?"}
        ]
    )
    print(response.choices[0].message.content)

Chat Completion with Files
-------------------------

.. code-block:: python

    from openwebui_client import OpenWebUIClient

    client = OpenWebUIClient(
        api_key="your-openwebui-api-key",
        base_url="http://localhost:5000"
    )

    # Read file content
    with open("document.pdf", "rb") as f:
        file_content = f.read()

    # Create chat completion with file attachment
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarize the attached document."}
        ],
        files=[file_content]
    )

Using Function Calling / Tools
-----------------------------

Direct Tool Usage
~~~~~~~~~~~~~~~~

.. code-block:: python

    from openwebui_client import OpenWebUIClient

    client = OpenWebUIClient(
        api_key="your-openwebui-api-key",
        base_url="http://localhost:5000"
    )

    # Define a tool schema directly
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

Using the Tool Registry
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from openwebui_client import OpenWebUIClient
    from pathlib import Path

    client = OpenWebUIClient(
        api_key="your-openwebui-api-key",
        base_url="http://localhost:5000"
    )

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

    def get_forecast(location: str, days: int = 1) -> str:
        """Get the weather forecast for a location.

        Args:
            location: The location to get the forecast for
            days: Number of days to forecast

        Returns:
            str: A string describing the forecast
        """
        return f"The forecast for {location} for the next {days} day(s) is sunny."

    # Register tools with the client
    client.tool_registry.register(get_weather)
    client.tool_registry.register(get_forecast)

    # Use chat_with_tools for automatic tool handling
    response = client.chat_with_tools(
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": "What's the weather like in Toronto?"}
        ],
        max_tool_calls=5,
    )

    print(response)  # Will contain the final response after any tool calls

    # You can also include files with tool calls
    file_path = Path("weather_data.txt")
    response_with_file = client.chat_with_tools(
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": "Analyze the weather data in the attached file."}
        ],
        files=[file_path],
        max_tool_calls=5,
    )
    print(response.choices[0].message.content)

File Upload and Management
-------------------------

.. code-block:: python

    from openwebui_client import OpenWebUIClient

    client = OpenWebUIClient(
        api_key="your-openwebui-api-key",
        base_url="http://localhost:5000"
    )

    # Read file content
    with open("document.pdf", "rb") as f:
        file_content = f.read()

    # Upload a single file
    file_obj = client.files.create(
        file=file_content,
        file_metadata={"purpose": "assistants"}
    )
    print(f"File uploaded with ID: {file_obj.id}")

    # Upload multiple files
    with open("another_doc.pdf", "rb") as f2:
        file_content2 = f2.read()

    file_objects = client.files.create(
        files=[(file_content, {"purpose": "assistants"}),
               (file_content2, {"purpose": "assistants"})]
    )
    for i, file_obj in enumerate(file_objects):
        print(f"File {i+1} uploaded with ID: {file_obj.id}")
