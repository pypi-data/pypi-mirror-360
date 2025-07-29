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
