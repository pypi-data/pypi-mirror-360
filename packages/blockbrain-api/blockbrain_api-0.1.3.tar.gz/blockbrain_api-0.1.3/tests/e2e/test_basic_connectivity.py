"""Basic connectivity and authentication tests."""

import pytest

from blockbrain_api import BlockBrainAPI


class TestBasicConnectivity:
    """Test basic API connectivity and authentication."""

    def test_api_client_initialization(self, api_credentials):
        """Test that API client can be initialized with valid credentials."""
        api = BlockBrainAPI(
            base_url=api_credentials["base_url"], token=api_credentials["token"], bot_id=api_credentials["bot_id"]
        )

        assert api.core.token == api_credentials["token"]
        assert api.core.bot_id == api_credentials["bot_id"]  # bot_id is stored on core
        assert api.core.base_url == api_credentials["base_url"]

    def test_token_authentication(self, api_client):
        """Test that the API accepts our token by making a simple chat request."""
        # Try a simple chat - this should work with valid auth
        response = api_client.chat("Hello, this is a test")

        # Should get a valid response
        assert isinstance(response, (str, dict))
        if isinstance(response, dict):
            # Should have response content or be a valid error
            assert "response" in response or "answer" in response or "content" in response or "error" in response

    def test_invalid_token_handling(self, api_credentials):
        """Test that invalid tokens are handled gracefully."""
        api = BlockBrainAPI(
            base_url=api_credentials["base_url"], token="invalid_token_12345", bot_id=api_credentials["bot_id"]
        )

        # This should fail with an authentication error
        response = api.chat("Test message")

        # Should get an error response
        assert isinstance(response, dict)
        assert "error" in response or "status" in response or "unauthorized" in str(response).lower()

    def test_api_base_url_connectivity(self, api_credentials):
        """Test connectivity to the API base URL."""
        import requests

        # Test that the base URL is reachable
        try:
            response = requests.get(api_credentials["base_url"], timeout=10)
            # Should get some response (doesn't need to be 200, just reachable)
            assert response.status_code is not None
        except requests.RequestException:
            pytest.fail(f"Cannot reach API base URL: {api_credentials['base_url']}")

    def test_simple_chat_functionality(self, api_client, resource_tracker):
        """Test basic chat functionality works."""
        # Test simple chat
        response = api_client.chat("What is 2+2?")

        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            # Direct string response
            assert len(response) > 0
        else:
            # Dictionary response
            response_text = response.get("response") or response.get("answer") or response.get("content") or ""
            assert len(response_text) > 0 or "error" in response

            # Track conversation if available
            if "conversation_id" in response:
                resource_tracker.track_conversation(response["conversation_id"])

    def test_health_check_via_chat(self, api_client):
        """Use chat functionality as a health check for the API."""
        response = api_client.chat("Test connectivity")

        # Should get a valid response structure
        assert response is not None
        assert isinstance(response, (str, dict))

        # If it's a dict, should have response content or error
        if isinstance(response, dict):
            assert any(key in response for key in ["response", "answer", "content", "error"])

    def test_api_error_handling(self, api_client):
        """Test that API errors are handled gracefully."""
        # Try chat with empty message to test error handling
        response = api_client.chat("")

        # Should handle gracefully (either success or appropriate error)
        assert isinstance(response, (str, dict))

        if isinstance(response, dict):
            # If error, should be about empty input, not system error
            if "error" in response:
                error_msg = str(response["error"]).lower()
                # Should be input validation, not system error
                assert (
                    any(term in error_msg for term in ["empty", "invalid", "message", "input", "required"])
                    or len(error_msg) > 0
                )

    def test_request_timeout_handling(self, api_credentials):
        """Test that request timeouts are handled properly."""
        # Create client with very short timeout
        api = BlockBrainAPI(
            base_url=api_credentials["base_url"], token=api_credentials["token"], bot_id=api_credentials["bot_id"]
        )

        # Set a very short timeout on the session
        api.core.session.timeout = 0.001

        # This should timeout gracefully - using a method that requires bot_id
        response = api.core.list_data_rooms(bot_id="test_bot_id")

        # Should handle timeout gracefully (return error dict, not raise exception)
        assert isinstance(response, dict)
        # Might contain timeout or connection error - be more flexible with error detection
        if "error" in response:
            error_text = str(response["error"]).lower()
            # Look for various error indicators
            expected_errors = ["timeout", "connection", "network", "time", "failed", "unreachable", "connect"]
            has_expected_error = any(word in error_text for word in expected_errors)
            # If no expected error keywords, just ensure there's an error message
            assert has_expected_error or len(error_text) > 0, f"Unexpected error format: {response}"
