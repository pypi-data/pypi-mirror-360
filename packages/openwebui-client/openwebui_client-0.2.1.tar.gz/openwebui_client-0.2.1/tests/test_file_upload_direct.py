"""Direct HTTP test for file uploads based on a working curl script."""

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
    """Get the API base URL from environment variables but remove /api suffix if present."""
    base_url = os.environ.get("OPENWEBUI_API_BASE", "")
    # Remove the /api suffix if present
    if base_url.endswith("/api"):
        base_url = base_url[:-4]
    return base_url.rstrip("/")


@pytest.fixture
def api_key():
    """Get the API key from environment variables."""
    return os.environ.get("OPENWEBUI_API_KEY")


@pytest.fixture
def file_content():
    """Get test file content."""
    with open(Path(__file__).parent / "data" / "Bemade Header.pdf", "rb") as f:
        return f.read()


def test_direct_file_upload_with_trailing_slash_and_process(
    api_base, api_key, file_content
):
    """Test direct file upload using the exact format from the working curl script."""
    # Note the trailing slash and use of the base URL without /api
    url = f"{api_base}/api/v1/files/"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    # Create a temporary file
    temp_file_path = Path(__file__).parent / "data" / "temp_test.pdf"
    with open(temp_file_path, "wb") as f:
        f.write(file_content)

    files = {}

    try:
        # Use the format from the curl script with process=true
        files = {
            "file": open(temp_file_path, "rb"),
        }
        data = {
            "process": "true",
        }

        # Print the request details for debugging
        print("\n===== REQUEST DETAILS =====")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        print(f"Files: {list(files.keys())}")

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
            print(f"File ID: {file_obj['id']}")
    finally:
        # Close the file handle
        for f in files.values():
            f.close()

        # Clean up the temporary file
        if temp_file_path.exists():
            temp_file_path.unlink()
