"""
BlockBrain API Python Client

A modern, streamlined Python client for the BlockBrain API featuring:
- Unified chat interface
- File processing and analysis
- Context management
- Conversation continuation
- Real-time streaming responses
- Model selection and switching

Usage:
    from blockbrain_api import BlockBrainAPI

    # Initialize client
    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Initialize client with default model
    api = BlockBrainAPI(
        token="your_token",
        bot_id="your_bot_id",
        default_model="gpt-4o"
    )

    # Simple chat
    response = api.chat("What is AI?")

    # Chat with specific model (overrides default)
    response = api.chat("What is AI?", model="claude-3.5-sonnet")

    # Chat with file upload
    response = api.chat("Analyze this document", file_path="document.pdf")

    # Get available models
    models = api.get_available_models()

    # Change model for existing data room
    api.change_data_room_model(convo_id, "gpt-4")

    # Access core API for advanced usage
    response = api.core.user_prompt("Hello", session_id, convo_id)
"""

from .api import BlockBrainAPI
from .chat import BlockBrainChat
from .core import BlockBrainCore

__version__ = "0.1.3"
__author__ = "BlockBrain"
__email__ = "support@blockbrain.ai"

__all__ = ["BlockBrainAPI", "BlockBrainCore", "BlockBrainChat"]
