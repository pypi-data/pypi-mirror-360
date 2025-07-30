from typing import Optional

from .chat import BlockBrainChat
from .core import BlockBrainCore


class BlockBrainAPI:
    """Main BlockBrain API client with both core and simplified interfaces."""

    def __init__(
        self,
        base_url: str = "https://blocky.theblockbrain.ai",
        token: Optional[str] = None,
        bot_id: Optional[str] = None,
        tenant_domain: Optional[str] = None,
        enable_logging: bool = False,
        log_level: str = "INFO",
        default_model: Optional[str] = None,
    ):

        # Initialize core API
        self.core = BlockBrainCore(
            base_url=base_url,
            token=token,
            tenant_domain=tenant_domain,
            enable_logging=enable_logging,
            log_level=log_level,
        )

        # Store bot_id and default_model for convenience
        self.core.bot_id = bot_id
        self.core.default_model = default_model

        # Initialize simplified chat interface
        self._chat_interface = BlockBrainChat(self.core)

    def chat(self, *args, **kwargs):
        """
        Unified chat function that handles all chat scenarios:
        - Simple chat
        - Chat with file upload
        - Chat with context
        - Continue existing conversation

        Args:
            message (str): The message to send
            bot_id (Optional[str]): Bot ID (uses default if not provided)
            file_path (Optional[Union[str, Path]]): File to upload
            context (Optional[str]): Context to set for the conversation
            convo_id (Optional[str]): Existing conversation ID to continue
            session_id (Optional[str]): Session ID (auto-generated if not provided)
            convo_name (str): Name for new conversations (default: "Chat Session")
            cleanup (bool): Whether to delete conversation after response (default: True)
            wait_for_processing (bool): Wait for file processing (default: True)
            timeout (int): File processing timeout in seconds (default: 300)
            stream (bool): Enable streaming responses (default: True)
            model (Optional[str]): Model to use (overrides default_model if provided)

        Returns:
            Union[str, Dict[str, Any]]: AI response or error dict
        """
        return self._chat_interface.chat(*args, **kwargs)

    def set_token(self, token: str):
        """Set authentication token."""
        return self.core.set_token(token)

    def get_available_models(self):
        """Get all available LLM models."""
        return self.core.get_available_models()

    def change_data_room_model(self, convo_id: str, model: str):
        """Change the model for a specific data room/conversation."""
        return self.core.change_data_room_model(convo_id, model)
