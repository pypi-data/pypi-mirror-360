from pathlib import Path
from typing import Any, Dict, Optional, Union

from .core import BlockBrainCore


class BlockBrainChat:
    """Simplified chat interface for BlockBrain API."""

    def __init__(self, core: BlockBrainCore):
        self.core = core

    def chat(
        self,
        message: str,
        bot_id: Optional[str] = None,
        file_path: Optional[Union[str, Path]] = None,
        context: Optional[str] = None,
        convo_id: Optional[str] = None,
        session_id: Optional[str] = None,
        convo_name: str = "Chat Session",
        cleanup: bool = True,
        wait_for_processing: bool = True,
        timeout: int = 300,
        stream: bool = True,
        model: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Unified chat function that handles all chat scenarios:
        - Simple chat
        - Chat with file upload
        - Chat with context
        - Continue existing conversation
        """
        try:
            import uuid

            # Use provided session_id or generate new one
            if not session_id:
                session_id = str(uuid.uuid4())

            # Use provided bot_id or default
            bot_id = bot_id or getattr(self.core, "bot_id", None)
            if not bot_id:
                raise ValueError("bot_id is required. Provide it in the method call or set it during initialization.")

            # Determine which model to use: provided model > default model > None
            effective_model = model or getattr(self.core, "default_model", None)

            # If continuing existing conversation, use provided convo_id
            if convo_id:
                # Just send the message to existing conversation
                prompt_response = self.core.user_prompt(
                    message, session_id, convo_id, stream=stream, model=effective_model
                )
                return prompt_response

            # Create new data room for new conversation
            data_room_response = self.core.create_data_room(convo_name, session_id, bot_id, model=effective_model)
            if isinstance(data_room_response, dict) and data_room_response.get("error"):
                return {"error": "Failed to create data room", "details": data_room_response}

            # Extract conversation ID from response
            convo_data = data_room_response
            convo_id = (
                convo_data.get("id")
                or convo_data.get("convoId")
                or convo_data.get("dataRoomId")
                or convo_data.get("body", {}).get("dataRoomId")
            )

            if not convo_id:
                return {
                    "error": f"Could not extract conversation ID from response. "
                    f"Available fields: {list(convo_data.keys())}"
                }

            # Upload file if provided
            if file_path:
                upload_response = self.core.upload_file(file_path, convo_id, session_id)
                if isinstance(upload_response, dict) and upload_response.get("error"):
                    return {"error": "Failed to upload file", "details": upload_response}

                # Wait for file processing if requested
                if wait_for_processing:
                    self.core.logger.info("Waiting for file processing to complete...")
                    processing_result = self.core.wait_for_file_processing(convo_id, timeout)
                    if not processing_result.get("success"):
                        self.core.logger.warning(f"File processing wait failed: {processing_result.get('error')}")
                        # Continue anyway - user might still want to ask questions

            # Add context if provided
            if context:
                context_response = self.core.add_context(convo_id, context)
                if isinstance(context_response, dict) and context_response.get("error"):
                    self.core.logger.warning(f"Failed to add context, continuing anyway. Details: {context_response}")

            # Send the message
            prompt_response = self.core.user_prompt(message, session_id, convo_id, stream=stream, model=effective_model)

            # Clean up data room if requested
            if cleanup:
                try:
                    delete_response = self.core.delete_data_room(convo_id)
                    self.core.logger.info(f"Data room {convo_id} cleaned up")
                except Exception as e:
                    self.core.logger.warning(f"Failed to cleanup data room {convo_id}: {e}")

            # Return the actual prompt response content
            return prompt_response

        except Exception as e:
            return {"error": str(e)}

    def upload_and_ask(
        self,
        file_path: Union[str, Path],
        question: str,
        bot_id: Optional[str] = None,
        convo_name: str = "Quick Upload",
        context: Optional[str] = None,
        cleanup: bool = True,
        wait_for_processing: bool = True,
        timeout: int = 300,
        stream: bool = True,
        model: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """Upload a file and ask a question about it in one operation."""
        return self.chat(
            message=question,
            bot_id=bot_id,
            file_path=file_path,
            context=context,
            convo_name=convo_name,
            cleanup=cleanup,
            wait_for_processing=wait_for_processing,
            timeout=timeout,
            stream=stream,
            model=model,
        )

    def simple_chat(
        self,
        question: str,
        bot_id: Optional[str] = None,
        convo_name: str = "New Data Room",
        context: Optional[str] = None,
        cleanup: bool = True,
        stream: bool = True,
        model: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """Start a simple chat conversation."""
        return self.chat(
            message=question,
            bot_id=bot_id,
            context=context,
            convo_name=convo_name,
            cleanup=cleanup,
            stream=stream,
            model=model,
        )

    def create_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        bot_id: Optional[str] = None,
        stream: bool = True,
        context: Optional[str] = None,
        cleanup: bool = True,
        **kwargs,
    ) -> Union[str, Dict[str, Any]]:
        """OpenAI-style completion interface."""
        # Extract user message content
        user_content = ""
        for message in messages:
            if message.get("role") == "user":
                user_content = message.get("content", "")
                break

        if not user_content:
            raise ValueError("No user message found in messages")

        try:
            # Create a simple chat with cleanup setting and context
            return self.chat(user_content, bot_id, context=context, cleanup=cleanup, stream=stream, model=model)

        except Exception as e:
            return {"error": str(e)}

    def create_chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        bot_id: Optional[str] = None,
        context: Optional[str] = None,
        cleanup: bool = True,
        stream: bool = True,
        **kwargs,
    ) -> Union[str, Dict[str, Any]]:
        """OpenAI-style chat completion interface."""
        return self.create_completion(
            messages, model, bot_id, stream=stream, context=context, cleanup=cleanup, **kwargs
        )
