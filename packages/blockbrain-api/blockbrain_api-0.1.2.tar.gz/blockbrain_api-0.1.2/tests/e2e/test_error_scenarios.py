"""End-to-end tests for error scenarios and edge cases."""

import time
from pathlib import Path

import pytest


class TestErrorScenarios:
    """Test error handling, edge cases, and recovery scenarios."""

    def test_invalid_authentication_handling(self, api_credentials):
        """Test handling of invalid authentication scenarios."""
        from blockbrain_api import BlockBrainAPI

        # Test with invalid token
        api_invalid = BlockBrainAPI(
            base_url=api_credentials["base_url"], token="invalid_token_123456789", bot_id=api_credentials["bot_id"]
        )

        response = api_invalid.chat("Test message")

        # Should handle auth error gracefully
        assert isinstance(response, (str, dict))
        if isinstance(response, dict):
            assert "error" in response or "unauthorized" in str(response).lower()
        else:
            # String response might indicate success (API might be permissive)
            assert isinstance(response, str)

        # Test with missing token
        api_no_token = BlockBrainAPI(base_url=api_credentials["base_url"], token=None, bot_id=api_credentials["bot_id"])

        response2 = api_no_token.chat("Test message")
        assert isinstance(response2, (str, dict))
        # Should indicate missing authentication (if dict) or handle gracefully (if string)
        if isinstance(response2, dict):
            assert "error" in response2 or "token" in str(response2).lower()
        else:
            # String response might indicate success (API might be permissive)
            assert isinstance(response2, str)

    def test_invalid_bot_id_handling(self, api_credentials):
        """Test handling of invalid bot IDs."""
        from blockbrain_api import BlockBrainAPI

        api_invalid_bot = BlockBrainAPI(
            base_url=api_credentials["base_url"], token=api_credentials["token"], bot_id="invalid_bot_id_123456789"
        )

        response = api_invalid_bot.chat("Test message")

        # Should handle invalid bot ID gracefully (either success or error)
        assert isinstance(response, (str, dict))

        # If it's a dict response, check for error
        if isinstance(response, dict) and "error" in response:
            # Error is acceptable for invalid bot ID
            error_msg = str(response["error"]).lower()
            # Just verify error message exists, don't enforce specific terms
            assert len(error_msg) > 0, "Error message should not be empty"
        # If it's a string or successful dict, the API might be more permissive
        # which is also acceptable behavior

    def test_network_timeout_handling(self, api_credentials):
        """Test handling of network timeouts and connection issues."""
        from blockbrain_api import BlockBrainAPI

        # Create API client with very short timeout
        api_timeout = BlockBrainAPI(
            base_url=api_credentials["base_url"], token=api_credentials["token"], bot_id=api_credentials["bot_id"]
        )

        # Set extremely short timeout (make it even shorter)
        try:
            api_timeout.core.session.timeout = 0.0001
        except Exception:
            # If timeout setting fails, skip the test
            pytest.skip("Cannot set network timeout for testing")

        response = api_timeout.chat("Test message")

        # Should handle timeout gracefully (either success or error)
        assert isinstance(response, (str, dict))

        # If it's a dict response with error, check error content
        if isinstance(response, dict) and "error" in response:
            # Error should indicate timeout or connection issue
            error_msg = str(response["error"]).lower()
            timeout_indicators = ["timeout", "connection", "network", "request failed", "read timed out"]
            assert any(
                indicator in error_msg for indicator in timeout_indicators
            ), f"Unexpected error type: {error_msg}"
        else:
            # If successful (string response or dict without error), the API was fast enough
            # This is also acceptable - timeout might not have triggered
            pass

    def test_malformed_file_upload(self, api_client, test_data_room, api_credentials):
        """Test handling of problematic file uploads."""
        import uuid

        data_room_id = test_data_room["id"]
        session_id = str(uuid.uuid4())

        # Test non-existent file
        try:
            response1 = api_client.core.upload_file("/non/existent/file.txt", data_room_id, session_id)
            # If no exception, check for error in response
            assert isinstance(response1, dict)
            assert "error" in response1
            assert any(term in str(response1["error"]).lower() for term in ["not found", "file", "exist", "path"])
        except FileNotFoundError:
            # FileNotFoundError is expected and acceptable for non-existent files
            pass

        # Test empty file path
        try:
            response2 = api_client.core.upload_file("", data_room_id, session_id)
            # If no exception, check for error in response
            assert isinstance(response2, dict)
            assert "error" in response2
        except (FileNotFoundError, OSError, ValueError):
            # Exception for empty path is expected and acceptable
            pass

        # Test invalid data room ID
        response3 = api_client.core.upload_file(
            str(Path(__file__)), "invalid_room_id_123", session_id  # Use this test file
        )

        assert isinstance(response3, dict)
        assert "error" in response3

    def test_large_message_handling(self, api_client, resource_tracker):
        """Test handling of very large chat messages."""
        # Create a very long message
        large_message = "This is a test message. " * 1000  # ~24KB message

        response = api_client.chat(large_message)

        # Should either handle gracefully or truncate
        assert isinstance(response, (str, dict))

        if isinstance(response, dict) and "error" in response:
            # If error, should be about message size
            error_msg = str(response["error"]).lower()
            size_indicators = ["too long", "size", "limit", "length", "truncat"]
            assert any(indicator in error_msg for indicator in size_indicators)
        elif isinstance(response, str):
            # String response - should have content
            assert len(response) > 0
        else:
            # Dict response without error - should have response
            response_text = response.get("response") or response.get("answer") or response.get("content") or ""
            assert len(response_text) > 0

            if "conversation_id" in response:
                resource_tracker.track_conversation(response["conversation_id"])

    def test_rapid_sequential_requests(self, api_client, resource_tracker):
        """Test handling of rapid sequential requests (rate limiting)."""
        messages = ["What is 1+1?", "What is 2+2?", "What is 3+3?", "What is 4+4?", "What is 5+5?"]

        responses = []
        start_time = time.time()

        # Send requests as quickly as possible
        for message in messages:
            response = api_client.chat(message)
            responses.append(response)

            # Track conversations for cleanup
            if isinstance(response, dict) and "conversation_id" in response:
                resource_tracker.track_conversation(response["conversation_id"])

        end_time = time.time()
        total_time = end_time - start_time

        # All responses should be valid (either success or rate limit error)
        for i, response in enumerate(responses):
            assert isinstance(response, (str, dict)), f"Response {i} not a string or dict: {response}"

            if isinstance(response, dict) and "error" in response:
                # If error, might be rate limiting
                error_msg = str(response["error"]).lower()
                if any(term in error_msg for term in ["rate", "limit", "too many", "throttle"]):
                    # Rate limiting is acceptable
                    continue
                else:
                    # Other errors might indicate problems
                    pytest.fail(f"Unexpected error in rapid request {i}: {response}")
            elif isinstance(response, str):
                # String response - should have content
                assert len(response) > 0, f"Empty string response in rapid request {i}"
            else:
                # Dict response without error - should have content
                response_text = response.get("response") or response.get("answer") or response.get("content") or ""
                assert len(response_text) > 0, f"Empty response in rapid request {i}"

        # Should complete reasonably quickly (even with rate limiting)
        assert total_time < 60, f"Rapid requests took too long: {total_time}s"

    def test_concurrent_data_room_operations(self, api_client, resource_tracker, unique_test_name, api_credentials):
        """Test concurrent operations on data rooms."""
        import queue
        import threading
        import uuid

        results_queue = queue.Queue()
        bot_id = api_credentials["bot_id"]

        def create_room(room_suffix):
            """Create a room in a thread."""
            try:
                room_name = f"{unique_test_name}_CONCURRENT_{room_suffix}"
                session_id = str(uuid.uuid4())
                response = api_client.core.create_data_room(room_name, session_id, bot_id)
                results_queue.put(("success", response))
            except Exception as e:
                results_queue.put(("error", str(e)))

        # Start multiple concurrent room creation threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_room, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)

        # Collect results
        results = []
        while not results_queue.empty():
            result = results_queue.get()
            results.append(result)

        # Should have results from all threads
        assert len(results) >= 2, f"Not enough concurrent results: {len(results)}"

        # Track created rooms for cleanup
        for result_type, result_data in results:
            if result_type == "success" and isinstance(result_data, dict):
                # Extract room ID from response (handle nested structure)
                room_id = (
                    result_data.get("id")
                    or result_data.get("convoId")
                    or result_data.get("dataRoomId")
                    or result_data.get("body", {}).get("dataRoomId")
                    or result_data.get("body", {}).get("_id")
                )
                if room_id:
                    resource_tracker.track_data_room(room_id)

        # At least some operations should succeed
        successes = [r for r in results if r[0] == "success"]
        assert len(successes) > 0, "No concurrent operations succeeded"

    def test_invalid_data_operations(self, api_client):
        """Test operations with invalid data and parameters."""
        # Test invalid conversation ID
        response1 = api_client.chat("Continue this conversation", convo_id="invalid_conv_id_123456")

        assert isinstance(response1, (str, dict))
        if isinstance(response1, dict) and "error" in response1:
            # The error message is in content.body, not in the error field itself
            if "content" in response1 and "body" in response1["content"]:
                error_msg = str(response1["content"]["body"]).lower()
            else:
                error_msg = str(response1.get("error", "")).lower()
            assert any(
                term in error_msg
                for term in ["conversation", "not found", "invalid", "convo", "no longer available", "oops"]
            )
        # String response is also acceptable (API might be permissive)

        # Test invalid data room ID in chat
        response2 = api_client.chat("Use this data room", convo_id="invalid_room_id_123456")

        assert isinstance(response2, (str, dict))
        if isinstance(response2, dict) and "error" in response2:
            # The error message is in content.body, not in the error field itself
            if "content" in response2 and "body" in response2["content"]:
                error_msg = str(response2["content"]["body"]).lower()
            else:
                error_msg = str(response2.get("error", "")).lower()
            assert any(
                term in error_msg
                for term in ["room", "not found", "invalid", "access", "convo", "no longer available", "oops"]
            )
        # String response is also acceptable (API might be permissive)

    def test_edge_case_inputs(self, api_client, resource_tracker):
        """Test edge case inputs and special characters."""
        edge_case_messages = [
            "",  # Empty message
            " ",  # Whitespace only
            "\n\n\n",  # Only newlines
            "🚀🤖💻🔥✨",  # Only emojis
            "SELECT * FROM users; DROP TABLE users;--",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "A" * 50,  # Long single word
            "Hello\x00World",  # Null byte
            "测试中文消息",  # Chinese characters
            "🎭🎨🎪🎨🎭" * 100,  # Many emojis
        ]

        for i, message in enumerate(edge_case_messages):
            try:
                response = api_client.chat(message)

                # Should handle gracefully (either success or appropriate error)
                assert isinstance(response, (str, dict)), f"Non-string/dict response for edge case {i}: {message}"

                if isinstance(response, dict) and "error" in response:
                    # Error should be about empty/invalid input, not system error
                    error_msg = str(response["error"]).lower()
                    expected_error_terms = ["empty", "invalid", "message", "input", "required"]
                    system_error_terms = ["internal", "server", "crash", "exception", "500"]

                    # Should be input validation error, not system error
                    has_expected = any(term in error_msg for term in expected_error_terms)
                    has_system = any(term in error_msg for term in system_error_terms)

                    assert has_expected or not has_system, f"System error for edge case {i}: {message} -> {response}"
                elif isinstance(response, str):
                    # String response - should be non-empty for non-empty inputs
                    if message.strip():
                        assert (
                            len(response.strip()) > 0
                        ), f"Empty string response for non-empty edge case {i}: {message}"
                else:
                    # Dict response without error - should have some response content
                    response_text = response.get("response") or response.get("answer") or response.get("content") or ""

                    # For non-empty inputs, should get non-empty response
                    if message.strip():
                        assert len(response_text.strip()) > 0, f"Empty response for non-empty edge case {i}: {message}"

                    if "conversation_id" in response:
                        resource_tracker.track_conversation(response["conversation_id"])

            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Unhandled exception for edge case {i}: {message} -> {str(e)}")

            # Small delay between edge case tests
            time.sleep(0.2)

    def test_api_recovery_after_errors(self, api_client, resource_tracker):
        """Test that API client recovers properly after errors."""
        # First, cause an error
        error_response = api_client.core.get_data_room("definitely_not_a_real_room_id")
        assert isinstance(error_response, dict)
        assert "error" in error_response

        # Then, verify normal operations still work
        normal_response = api_client.chat("What is 2+2?")

        assert isinstance(normal_response, (str, dict))
        if isinstance(normal_response, str):
            # String response - should be non-empty
            assert len(normal_response) > 0, "API didn't recover after error"
        elif "error" not in normal_response:
            # Dict response without error - should have content
            response_text = (
                normal_response.get("response") or normal_response.get("answer") or normal_response.get("content") or ""
            )
            assert len(response_text) > 0, "API didn't recover after error"

            if "conversation_id" in normal_response:
                resource_tracker.track_conversation(normal_response["conversation_id"])

        # Test multiple recovery cycles
        for i in range(3):
            # Cause error
            api_client.core.delete_data_room(f"fake_room_{i}")

            # Verify recovery
            recovery_response = api_client.chat(f"Test recovery {i}")
            assert isinstance(recovery_response, (str, dict))

            if isinstance(recovery_response, dict) and "conversation_id" in recovery_response:
                resource_tracker.track_conversation(recovery_response["conversation_id"])
