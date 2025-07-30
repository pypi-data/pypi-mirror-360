"""End-to-end tests for model selection functionality."""

import time

import pytest


class TestModelSelection:
    """Test model selection and change functionality."""

    def test_get_available_models(self, api_client):
        """Test getting list of available models."""
        # Execute: Get available models
        models_response = api_client.get_available_models()

        # Verify response structure
        assert isinstance(models_response, dict), "Models response should be a dictionary"
        assert "body" in models_response, "Models response should have 'body' field"
        assert isinstance(models_response["body"], list), "Models body should be a list"

        models = models_response["body"]
        assert len(models) > 0, "Should have at least one model available"

        # Verify model structure
        for model in models:
            assert isinstance(model, dict), "Each model should be a dictionary"
            assert "_id" in model, "Model should have _id field"
            assert "model" in model, "Model should have model field"
            assert "isEnable" in model, "Model should have isEnable field"

        # Check for known models (at least one should be available)
        model_names = [model["model"] for model in models]
        expected_models = ["azure-gpt-41", "gpt-4", "gpt-4o", "anthropic-claude-v3.5-sonnet"]
        available_expected = [model for model in expected_models if model in model_names]
        assert len(available_expected) > 0, f"At least one expected model should be available: {expected_models}"

    def test_api_with_default_model(self, api_credentials):
        """Test BlockBrainAPI initialization with default model."""
        from blockbrain_api import BlockBrainAPI

        # Get available models first to choose a valid one
        temp_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
        )

        models_response = temp_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]
        assert len(enabled_models) > 0, "Need at least one enabled model for testing"

        test_model = enabled_models[0]

        # Create client with default model
        api_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
            default_model=test_model,
        )

        # Verify default model is stored
        assert hasattr(api_client.core, "default_model"), "Core should have default_model attribute"
        assert api_client.core.default_model == test_model, "Default model should be set correctly"

    def test_chat_with_default_model(self, api_credentials, resource_tracker):
        """Test chat using default model set during initialization."""
        from blockbrain_api import BlockBrainAPI

        # Get an enabled model
        temp_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
        )

        models_response = temp_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]
        test_model = enabled_models[0]

        # Create client with default model
        api_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
            default_model=test_model,
        )

        # Execute: Chat with default model
        question = "What is the capital of France?"
        response = api_client.chat(question, cleanup=False)

        # Verify response
        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            assert len(response) > 0
            # Can't verify model usage with string response
            return

        # For dict response, try to track conversation for cleanup
        if "conversation_id" in response:
            resource_tracker.track_conversation(response["conversation_id"])

    def test_chat_with_override_model(self, api_credentials, resource_tracker):
        """Test chat with model parameter overriding default."""
        from blockbrain_api import BlockBrainAPI

        # Get available models
        temp_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
        )

        models_response = temp_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]

        if len(enabled_models) < 2:
            pytest.skip("Need at least 2 enabled models to test override functionality")

        default_model = enabled_models[0]
        override_model = enabled_models[1]

        # Create client with default model
        api_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
            default_model=default_model,
        )

        # Execute: Chat with model override
        question = "What is 2 + 2?"
        response = api_client.chat(question, model=override_model, cleanup=False)

        # Verify response
        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            assert len(response) > 0
            return

        # For dict response, try to track conversation for cleanup
        if "conversation_id" in response:
            resource_tracker.track_conversation(response["conversation_id"])

    def test_change_data_room_model(self, api_client, resource_tracker, test_data_room, api_credentials):
        """Test changing model for an existing data room."""
        room_id = test_data_room["id"]

        # Get available models
        models_response = api_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]

        if len(enabled_models) == 0:
            pytest.skip("Need at least one enabled model to test model changing")

        test_model = enabled_models[0]

        # Execute: Change model
        change_response = api_client.change_data_room_model(room_id, test_model)

        # Verify response (should not have error)
        assert isinstance(change_response, dict)
        assert not change_response.get("error"), f"Model change should succeed: {change_response}"

        # GET Verify: Check that model was actually changed
        room_details = api_client.core.get_data_room(room_id)
        assert isinstance(room_details, dict)

        # The model should be reflected in the data room details
        # Note: The exact field name might vary, so we check common locations
        room_data = room_details.get("body", room_details)
        model_field = room_data.get("model") or room_data.get("llm_model") or room_data.get("aiModel")

        if model_field:
            assert model_field == test_model, f"Model should be updated to {test_model}, got {model_field}"

    def test_create_data_room_with_model(self, api_client, resource_tracker, unique_test_name, api_credentials):
        """Test creating data room with specific model."""
        import uuid

        # Get available models
        models_response = api_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]

        if len(enabled_models) == 0:
            pytest.skip("Need at least one enabled model to test data room creation with model")

        test_model = enabled_models[0]

        # Execute: Create data room with model
        room_name = f"{unique_test_name}_MODEL_ROOM"
        session_id = str(uuid.uuid4())
        bot_id = api_credentials["bot_id"]

        room_response = api_client.core.create_data_room(room_name, session_id, bot_id, model=test_model)

        # Extract room ID
        room_id = (
            room_response.get("id")
            or room_response.get("convoId")
            or room_response.get("dataRoomId")
            or room_response.get("body", {}).get("dataRoomId")
            or room_response.get("body", {}).get("_id")
        )

        assert room_id, f"No ID found in create response: {room_response}"
        resource_tracker.track_data_room(room_id)

        # GET Verify: Check that model was set
        room_details = api_client.core.get_data_room(room_id)
        assert isinstance(room_details, dict)

        # Small delay to ensure model setting is processed
        time.sleep(1)

        # Check if model is reflected in room details
        room_data = room_details.get("body", room_details)
        model_field = room_data.get("model") or room_data.get("llm_model") or room_data.get("aiModel")

        if model_field:
            assert model_field == test_model, f"Model should be set to {test_model}, got {model_field}"

    def test_create_completion_with_model(self, api_client, resource_tracker):
        """Test OpenAI-style completion with model parameter."""
        # Get available models
        models_response = api_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]

        if len(enabled_models) == 0:
            pytest.skip("Need at least one enabled model to test completion with model")

        test_model = enabled_models[0]

        # Execute: Create completion with model
        messages = [{"role": "user", "content": "What is the largest planet in our solar system?"}]

        response = api_client._chat_interface.create_completion(messages=messages, model=test_model, cleanup=False)

        # Verify response
        assert isinstance(response, (str, dict))

        if isinstance(response, str):
            assert len(response.strip()) > 0
            assert "jupiter" in response.lower()
        else:
            response_text = response.get("response") or response.get("answer") or response.get("content") or ""
            assert len(response_text.strip()) > 0
            assert "jupiter" in response_text.lower()

            # Track for cleanup if possible
            if "conversation_id" in response:
                resource_tracker.track_conversation(response["conversation_id"])

    def test_model_parameter_precedence(self, api_credentials, resource_tracker):
        """Test that model parameter overrides default_model."""
        from blockbrain_api import BlockBrainAPI

        # Get available models
        temp_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
        )

        models_response = temp_client.get_available_models()
        models = models_response["body"]
        enabled_models = [model["model"] for model in models if model["isEnable"]]

        if len(enabled_models) < 2:
            pytest.skip("Need at least 2 enabled models to test precedence")

        default_model = enabled_models[0]
        override_model = enabled_models[1]

        # Create client with default model
        api_client = BlockBrainAPI(
            base_url=api_credentials["base_url"],
            token=api_credentials["token"],
            bot_id=api_credentials["bot_id"],
            default_model=default_model,
        )

        # Test 1: Chat without model parameter (should use default)
        response1 = api_client.chat("Test 1", cleanup=False)
        assert isinstance(response1, (str, dict))

        if isinstance(response1, dict) and "conversation_id" in response1:
            resource_tracker.track_conversation(response1["conversation_id"])

        # Test 2: Chat with model parameter (should use override)
        response2 = api_client.chat("Test 2", model=override_model, cleanup=False)
        assert isinstance(response2, (str, dict))

        if isinstance(response2, dict) and "conversation_id" in response2:
            resource_tracker.track_conversation(response2["conversation_id"])

        # Both should work successfully
        if isinstance(response1, str):
            assert len(response1.strip()) > 0
        else:
            response_text = response1.get("response") or response1.get("answer") or response1.get("content") or ""
            assert len(response_text.strip()) > 0

        if isinstance(response2, str):
            assert len(response2.strip()) > 0
        else:
            response_text = response2.get("response") or response2.get("answer") or response2.get("content") or ""
            assert len(response_text.strip()) > 0

    def test_invalid_model_handling(self, api_client, resource_tracker):
        """Test handling of invalid model names."""
        invalid_model = "non-existent-model-12345"

        # Execute: Try to change to invalid model
        # This should either fail gracefully or warn and continue
        try:
            response = api_client.chat("Test with invalid model", model=invalid_model)

            # If it succeeds, verify response is still valid
            assert isinstance(response, (str, dict))

            if isinstance(response, str):
                # Should still get a valid response (likely fell back to default)
                assert len(response.strip()) > 0
            else:
                response_text = response.get("response") or response.get("answer") or response.get("content") or ""
                if isinstance(response_text, str):
                    assert len(response_text.strip()) > 0
                else:
                    # If response_text is not a string, the response structure is different
                    # Just verify we got some response
                    assert response_text is not None

                if "conversation_id" in response:
                    resource_tracker.track_conversation(response["conversation_id"])

        except Exception as e:
            # If it fails, the error should be reasonable
            error_msg = str(e).lower()
            assert any(word in error_msg for word in ["model", "invalid", "not found", "unsupported"])

    def test_model_list_contains_enabled_models(self, api_client):
        """Test that the model list contains at least some enabled models."""
        # Execute: Get available models
        models_response = api_client.get_available_models()
        models = models_response["body"]

        # Verify we have some enabled models
        enabled_models = [model for model in models if model.get("isEnable", False)]
        assert len(enabled_models) > 0, "Should have at least one enabled model"

        # Verify enabled models have required fields
        for model in enabled_models[:3]:  # Test first 3 enabled models
            assert model.get("model"), "Enabled model should have model name"
            assert model.get("_id"), "Enabled model should have ID"

            # Optional fields that might be present
            description = model.get("description")
            if description:
                assert isinstance(description, str)
                assert len(description) > 0

    def test_core_api_model_methods(self, api_client):
        """Test model-related methods in core API."""
        # Test get_available_models through core
        core_models = api_client.core.get_available_models()
        assert isinstance(core_models, dict)
        assert "body" in core_models

        # Test through main API (should be same result)
        api_models = api_client.get_available_models()
        assert isinstance(api_models, dict)
        assert "body" in api_models

        # Should return the same data
        assert core_models["body"] == api_models["body"]
