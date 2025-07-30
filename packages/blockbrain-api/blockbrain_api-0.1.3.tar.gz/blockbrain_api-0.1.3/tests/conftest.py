"""Pytest configuration and fixtures for end-to-end tests."""

import logging
import os
from pathlib import Path
from typing import Generator

import pytest

from blockbrain_api import BlockBrainAPI
from tests.utils.cleanup import TestResourceTracker, cleanup_test_resources_by_prefix

# Load .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not installed, skip loading
    pass

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test requiring live API")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Add e2e marker to all tests in e2e directory."""
    for item in items:
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


@pytest.fixture(scope="session")
def api_credentials():
    """Get API credentials from environment variables."""
    token = os.getenv("BLOCKBRAIN_TOKEN")
    bot_id = os.getenv("BLOCKBRAIN_BOT_ID")
    base_url = os.getenv("BLOCKBRAIN_BASE_URL", "https://blocky.theblockbrain.ai")

    if not token or not bot_id:
        pytest.skip(
            "E2E tests require BLOCKBRAIN_TOKEN and BLOCKBRAIN_BOT_ID environment variables. "
            "These should be set in GitHub Actions secrets for CI/CD."
        )

    return {"token": token, "bot_id": bot_id, "base_url": base_url}


@pytest.fixture(scope="session")
def api_client(api_credentials) -> BlockBrainAPI:
    """Create API client for testing."""
    return BlockBrainAPI(
        base_url=api_credentials["base_url"],
        token=api_credentials["token"],
        bot_id=api_credentials["bot_id"],
        enable_logging=True,
        log_level="DEBUG",
    )


@pytest.fixture(scope="session", autouse=True)
def session_cleanup(api_client, api_credentials):
    """Clean up any leftover test resources at start and end of session."""
    # Set bot_id on api_client so cleanup can access it
    api_client.core.bot_id = api_credentials["bot_id"]

    # Cleanup any leftover resources from previous failed runs
    logger.info("Performing pre-test cleanup...")
    cleanup_test_resources_by_prefix(api_client, "E2E_TEST_")

    yield

    # Final cleanup after all tests
    logger.info("Performing post-test cleanup...")
    cleanup_test_resources_by_prefix(api_client, "E2E_TEST_")


@pytest.fixture
def resource_tracker(api_client) -> Generator[TestResourceTracker, None, None]:
    """Track and cleanup test resources for each test."""
    tracker = TestResourceTracker(api_client)

    yield tracker

    # Cleanup resources after each test
    logger.info("Cleaning up test resources...")
    cleanup_results = tracker.cleanup_all()

    # Log cleanup results
    if cleanup_results["cleaned"]:
        logger.info(f"Cleaned up resources: {cleanup_results['cleaned']}")
    if cleanup_results["failed"]:
        logger.warning(f"Failed to cleanup resources: {cleanup_results['failed']}")
    if cleanup_results["verified"]:
        logger.info(f"Verified cleanup: {cleanup_results['verified']}")


@pytest.fixture
def test_data_dir() -> Path:
    """Get path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def sample_text_file(test_data_dir) -> Path:
    """Get path to sample text file."""
    return test_data_dir / "sample.txt"


@pytest.fixture
def sample_json_file(test_data_dir) -> Path:
    """Get path to sample JSON file."""
    return test_data_dir / "sample.json"


@pytest.fixture
def sample_md_file(test_data_dir) -> Path:
    """Get path to sample markdown file."""
    return test_data_dir / "sample.md"


@pytest.fixture
def unique_test_name() -> str:
    """Generate unique test identifier."""
    import random
    import time

    timestamp = int(time.time())
    random_id = random.randint(1000, 9999)
    return f"E2E_TEST_{timestamp}_{random_id}"


@pytest.fixture
def test_data_room(api_client, resource_tracker, unique_test_name, api_credentials):
    """Create a test data room for the test."""
    import uuid

    room_name = f"{unique_test_name}_ROOM"
    session_id = str(uuid.uuid4())
    bot_id = api_credentials["bot_id"]

    # Create data room
    room_response = api_client.core.create_data_room(room_name, session_id, bot_id)

    # Extract room ID from response (handle nested structure)
    room_id = (
        room_response.get("id")
        or room_response.get("convoId")
        or room_response.get("dataRoomId")
        or room_response.get("body", {}).get("dataRoomId")
        or room_response.get("body", {}).get("_id")
    )

    assert room_id, f"No ID found in create response: {room_response}"
    resource_tracker.track_data_room(room_id)

    # Verify creation with GET
    room_details = api_client.core.get_data_room(room_id)
    room_data = room_details.get("body", room_details)
    actual_room_id = room_data.get("_id") or room_data.get("id") or room_details.get("id")
    assert actual_room_id == room_id, "Data room creation not verified"

    return {"id": room_id, "name": room_name, "details": room_details}


# Skip E2E tests if running without credentials
def pytest_runtest_setup(item):
    """Skip E2E tests if credentials not available."""
    if item.get_closest_marker("e2e"):
        if not os.getenv("BLOCKBRAIN_TOKEN") or not os.getenv("BLOCKBRAIN_BOT_ID"):
            pytest.skip("E2E tests require API credentials")
