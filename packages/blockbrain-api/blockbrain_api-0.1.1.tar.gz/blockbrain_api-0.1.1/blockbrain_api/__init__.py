"""
BlockBrain API Python Client

A modern, streamlined Python client for the BlockBrain API featuring:
- Unified chat interface
- File processing and analysis
- Context management
- Conversation continuation
- Real-time streaming responses

Usage:
    from blockbrain_api import BlockBrainAPI

    # Initialize client
    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Simple chat
    response = api.chat("What is AI?")

    # Chat with file upload
    response = api.chat("Analyze this document", file_path="document.pdf")

    # Access core API for advanced usage
    response = api.core.user_prompt("Hello", session_id, convo_id)
"""

from .api import BlockBrainAPI
from .core import BlockBrainCore
from .chat import BlockBrainChat

__version__ = "0.1.1"
__author__ = "BlockBrain"
__email__ = "support@blockbrain.ai"

__all__ = ["BlockBrainAPI", "BlockBrainCore", "BlockBrainChat"]
