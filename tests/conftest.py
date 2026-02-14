"""
Shared pytest fixtures for endpoint tests.
"""
import asyncio
import os
import pytest
import dotenv

from api import XUIClient

# Load environment variables
dotenv.load_dotenv("../.env")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def xui_client() -> XUIClient:
    """
    Create and authenticate an XUIClient instance for testing against the real API.
    Yields the client and handles connection/disconnection.
    """
    base_url = os.getenv("BASE_URL")
    port_str = os.getenv("PORT")
    base_path = os.getenv("BASE_PATH")
    username = os.getenv("XUI_USERNAME")
    password = os.getenv("XUI_PASSWORD")

    if not all([base_url, port_str, base_path, username, password]):
        pytest.skip("Environment variables for XUIClient not configured (.env file required)")

    try:
        port = int(port_str)
    except (ValueError, TypeError):
        pytest.skip(f"Invalid PORT environment variable: {port_str}")

    # Reset singleton for clean test state
    XUIClient._instance = None

    client = XUIClient(base_url, port, base_path, xui_username=username, xui_password=password)
    client.connect()

    # Authenticate
    try:
        await client.login()
    except Exception as e:
        await client.disconnect()
        pytest.skip(f"Failed to authenticate with XUIClient: {e}")

    yield client

    # Cleanup
    try:
        await client.disconnect()
    except Exception:
        pass
    finally:
        # Reset singleton after test
        XUIClient._instance = None

