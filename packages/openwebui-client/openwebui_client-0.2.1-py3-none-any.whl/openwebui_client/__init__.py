"""OpenWebUI API client library.

This library provides a client for the OpenWebUI API, compatible with
the OpenAI Python SDK but with extensions specific to OpenWebUI.
"""

import os
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

from .client import OpenWebUIClient

# Export key classes and functions
__all__ = [
    "OpenWebUIClient",
    "client",
]

try:
    __version__ = version("openwebui-client")
except PackageNotFoundError:
    __version__ = "unknown"
