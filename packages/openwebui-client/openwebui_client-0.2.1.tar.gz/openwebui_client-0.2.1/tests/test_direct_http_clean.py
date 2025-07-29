"""Direct HTTP test for the /api/v1/files endpoint."""

import os
import pytest
import requests
from pathlib import Path

# Skip all tests if no API key or base URL is provided
pytestmark = pytest.mark.skipif(
    not (os.environ.get("OPENWEBUI_API_KEY") and os.environ.get("OPENWEBUI_API_BASE")),
    reason="OPENWEBUI_API_KEY and OPENWEBUI_API_BASE environment variables are required",
)


@pytest.fixture
def api_base():
    """Get the API base URL from environment variables."""
    return os.environ.get("OPENWEBUI_API_BASE", "").rstrip("/")


@pytest.fixture
def api_key():
    """Get the API key from environment variables."""
    return os.environ.get("OPENWEBUI_API_KEY")


@pytest.fixture
def file_content():
    """Get test file content."""
    with open(Path(__file__).parent / "data" / "Bemade Header.pdf", "rb") as f:
        return f.read()


def test_direct_file_upload(api_base, api_key, file_content):
    """Test direct file upload to the /v1/files endpoint."""
    url = f"{api_base}/v1/files/"  # Note the trailing slash

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    files = {
        "file": ("test.pdf", file_content, "application/pdf"),
    }

    data = {
        "purpose": "assistants",
        "process": "true",  # This parameter is required by OpenWebUI
    }

    # Print the request details for debugging
    print("\n===== REQUEST DETAILS =====")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    print(f"Files: {[(k, (v[0], '...content...', v[2])) for k, v in files.items()]}")

    # Make the direct request
    response = requests.post(url, headers=headers, files=files, data=data)

    # Print the full response for debugging
    print("\n===== RESPONSE DETAILS =====")
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {response.headers}")
    print(f"Response Body: {response.text}")

    # Assert the response status code
    assert response.status_code in [
        200,
        201,
    ], f"Expected 200/201, got {response.status_code}: {response.text}"

    # If successful, assert that we got a file object back
    if response.status_code in [200, 201]:
        file_obj = response.json()
        assert "id" in file_obj, "Response missing 'id' field"
