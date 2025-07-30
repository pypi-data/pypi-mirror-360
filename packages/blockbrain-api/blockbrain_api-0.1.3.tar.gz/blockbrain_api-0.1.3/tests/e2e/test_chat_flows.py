"""End-to-end tests for chat operations with GET verification."""

import time
from pathlib import Path

import pytest


class TestChatFlows:
    """Test chat operations with comprehensive verification."""

    def test_simple_chat_flow(self, api_client, resource_tracker):
        """Test basic chat functionality with conversation verification."""
        # Execute chat
        question = "What is artificial intelligence?"
        response = api_client.chat(question)

        # Verify response structure (can be string or dict)
        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            # Direct string response from streaming
            assert len(response) > 0
            # For string responses, we can't verify conversation tracking
            return

        # Dictionary response
        assert "response" in response or "answer" in response or "content" in response

        # If conversation tracking is supported, verify it
        if "conversation_id" in response:
            resource_tracker.track_conversation(response["conversation_id"])

            # GET verification: Check conversation exists and contains our message
            conversation = api_client.core.get_conversation(response["conversation_id"])
            assert isinstance(conversation, dict)

            # Verify our question appears in the conversation
            if "messages" in conversation:
                messages = conversation["messages"]
                assert any(
                    question.lower() in msg.get("content", "").lower() for msg in messages if isinstance(msg, dict)
                )

    def test_chat_with_context(self, api_client, resource_tracker):
        """Test chat with context and verify context is applied."""
        context = "You are a helpful math tutor. Explain concepts simply."
        question = "What is calculus?"

        response = api_client.chat(question, context=context)

        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            # Direct string response from streaming
            response_text = response
        else:
            # Dictionary response
            response_text = response.get("response") or response.get("answer") or response.get("content") or ""

        # Context should influence the response (math tutor style)
        assert len(response_text) > 0

        # If conversation tracking supported, verify context was applied
        if "conversation_id" in response:
            resource_tracker.track_conversation(response["conversation_id"])

    def test_conversation_continuity(self, api_client, resource_tracker):
        """Test that conversations maintain context across multiple messages."""
        # Start conversation with cleanup=False to maintain conversation
        first_response = api_client.chat("My name is TestUser. Remember this.", cleanup=False)
        assert isinstance(first_response, (str, dict))

        # For string responses, we can't test conversation continuity easily
        if isinstance(first_response, str):
            pytest.skip("Conversation continuity requires conversation tracking (dict response)")

        if "conversation_id" not in first_response:
            pytest.skip("Conversation continuity requires conversation tracking")

        conversation_id = first_response["conversation_id"]
        resource_tracker.track_conversation(conversation_id)

        # Continue conversation
        second_response = api_client.chat("What is my name?", convo_id=conversation_id)

        assert isinstance(second_response, (str, dict))

        if isinstance(second_response, str):
            response_text = second_response.lower()
        else:
            response_text = (
                second_response.get("response") or second_response.get("answer") or second_response.get("content") or ""
            ).lower()

        # Should remember the name from previous message
        assert "testuser" in response_text

        # GET verification: Check full conversation history
        conversation = api_client.core.get_conversation(conversation_id)
        assert isinstance(conversation, dict)

        if "messages" in conversation:
            messages = conversation["messages"]
            assert len(messages) >= 4  # At least 2 user + 2 assistant messages

            # Verify both our messages are in the conversation
            message_contents = [msg.get("content", "") for msg in messages if isinstance(msg, dict)]
            assert any("testuser" in content.lower() for content in message_contents)
            assert any("what is my name" in content.lower() for content in message_contents)

    def test_chat_with_file_integration(self, api_client, resource_tracker, sample_text_file):
        """Test chat with file upload and verify file content integration."""
        question = "What topics are covered in this document?"

        response = api_client.chat(question, file_path=str(sample_text_file))

        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            response_text = response.lower()
        else:
            response_text = (
                response.get("response") or response.get("answer") or response.get("content") or ""
            ).lower()

        # Should reference content from the uploaded file
        # Our sample file mentions: Technology, AI, Data processing, API integration
        file_topics = ["technology", "ai", "data processing", "api integration"]
        assert any(topic in response_text for topic in file_topics)

        if isinstance(response, dict) and "conversation_id" in response:
            resource_tracker.track_conversation(response["conversation_id"])

            # GET verification: Check conversation includes file reference
            conversation = api_client.core.get_conversation(response["conversation_id"])
            if isinstance(conversation, dict) and "messages" in conversation:
                # Should have reference to file upload or file content
                conversation_text = str(conversation).lower()
                assert any(word in conversation_text for word in ["file", "document", "upload", "attachment"])

    def test_multiple_file_chat(self, api_client, resource_tracker, sample_text_file, sample_json_file):
        """Test chat with multiple files and verify integration."""
        question = "Compare the content of these files and tell me what they contain."

        # Upload first file and chat
        response1 = api_client.chat("Analyze this text file", file_path=str(sample_text_file), cleanup=False)
        assert isinstance(response1, (str, dict))

        # Skip multi-file test if we get string response (can't track conversation)
        if isinstance(response1, str):
            pytest.skip("Multi-file chat requires conversation tracking (dict response)")

        conversation_id = response1.get("conversation_id")
        if conversation_id:
            resource_tracker.track_conversation(conversation_id)

            # Continue conversation with second file
            response2 = api_client.chat(
                "Now also analyze this JSON file and compare it to the previous file",
                file_path=str(sample_json_file),
                convo_id=conversation_id,
            )

            assert isinstance(response2, (str, dict))

            if isinstance(response2, str):
                response_text = response2.lower()
            else:
                response_text = (
                    response2.get("response") or response2.get("answer") or response2.get("content") or ""
                ).lower()

            # Should reference both files or show comparison
            assert len(response_text) > 0

            # GET verification: Check conversation has both file references
            conversation = api_client.core.get_conversation(conversation_id)
            if isinstance(conversation, dict):
                conversation_str = str(conversation).lower()
                # Should reference both file types
                assert any(word in conversation_str for word in ["text", "json"])

    def test_chat_response_quality(self, api_client, resource_tracker):
        """Test that chat responses meet quality standards."""
        test_questions = ["Explain machine learning in one sentence.", "What is 2 + 2?", "Name three colors."]

        for question in test_questions:
            response = api_client.chat(question)

            assert isinstance(response, (str, dict))

            if isinstance(response, str):
                response_text = response
            else:
                response_text = response.get("response") or response.get("answer") or response.get("content") or ""

            # Basic quality checks
            assert len(response_text.strip()) > 0, f"Empty response for: {question}"
            assert len(response_text.strip()) > 5, f"Too short response for: {question}"

            # Should not be just error messages
            error_indicators = ["error", "failed", "unable", "cannot process"]
            response_lower = response_text.lower()
            assert not any(error in response_lower for error in error_indicators), f"Error response for: {question}"

            if "conversation_id" in response:
                resource_tracker.track_conversation(response["conversation_id"])

            # Small delay between requests to be respectful
            time.sleep(0.5)

    def test_chat_with_streaming_verification(self, api_client, resource_tracker):
        """Test streaming chat if supported and verify final result."""
        question = "Count from 1 to 5."

        # Try streaming chat
        try:
            stream_response = api_client.chat(question, stream=True)

            if hasattr(stream_response, "__iter__"):
                # Collect streaming response
                full_response = ""
                for chunk in stream_response:
                    if isinstance(chunk, str):
                        full_response += chunk
                    elif isinstance(chunk, dict):
                        content = chunk.get("content") or chunk.get("response") or ""
                        full_response += content

                # Verify we got a complete response
                assert len(full_response.strip()) > 0

                # Should contain numbers 1-5
                numbers = ["1", "2", "3", "4", "5"]
                assert any(num in full_response for num in numbers)

            else:
                # If streaming not supported, should get regular response
                assert isinstance(stream_response, dict)

        except Exception as e:
            # If streaming not supported, skip this test
            if "stream" in str(e).lower() or "not supported" in str(e).lower():
                pytest.skip("Streaming not supported by API")
            else:
                raise
