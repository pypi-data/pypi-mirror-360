============
Installation
============

Requirements
-----------

* Python 3.10 or higher
* OpenAI Python SDK

Installation from PyPI
---------------------

The recommended way to install the OpenWebUI client is via pip:

.. code-block:: bash

    pip install openwebui-client

Installation from Source
-----------------------

If you prefer to install from source:

.. code-block:: bash

    git clone https://github.com/mdurepos/openwebui-client.git
    cd openwebui-client
    pip install -e .

Development Installation
-----------------------

For development, you'll want to install the package with development dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

This will install additional packages required for development, such as pytest, black, isort, and mypy.
