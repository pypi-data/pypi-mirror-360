#!/usr/bin/env python3
"""
Comprehensive Examples for BlockBrain API Python Client

This file demonstrates all capabilities of the BlockBrain API client,
including simple chat, file uploads, context setting, conversation
continuation, streaming, error handling, and advanced usage.
"""

import os
import json
from blockbrain_api import BlockBrainAPI


def example_1_basic_setup():
    """Example 1: Basic API setup and initialization"""
    print("=== Example 1: Basic API Setup ===")

    # Basic initialization
    api = BlockBrainAPI(token="your_token_here", bot_id="your_bot_id_here")

    # Advanced initialization with all options
    api_advanced = BlockBrainAPI(
        token="your_token_here",
        bot_id="your_bot_id_here",
        base_url="https://blocky.theblockbrain.ai",  # Custom base URL
        tenant_domain="your_tenant",  # For multi-tenant setups
        enable_logging=True,  # Enable logging (disabled by default)
        log_level="DEBUG",  # Set log level
    )

    print("✓ API clients initialized")
    print("✓ Logging is disabled by default, enable with enable_logging=True")
    print()


def example_2_simple_chat():
    """Example 2: Simple chat interactions"""
    print("=== Example 2: Simple Chat ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Basic chat
    response = api.chat("What is artificial intelligence?")
    print(f"Q: What is artificial intelligence?")
    print(f"A: {response}")
    print()

    # Chat with custom conversation name
    response = api.chat("Explain quantum computing", convo_name="Quantum Physics Discussion")
    print(f"Q: Explain quantum computing")
    print(f"A: {response}")
    print()


def example_3_chat_with_context():
    """Example 3: Using context to guide AI responses"""
    print("=== Example 3: Chat with Context ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Without context
    response1 = api.chat("Explain machine learning")
    print("Without context:")
    print(f"A: {response1[:100]}...")
    print()

    # With context
    context = (
        "You are a computer science professor explaining to undergraduate students. "
        "Use simple language and provide practical examples."
    )
    response2 = api.chat("Explain machine learning", context=context)
    print("With context (professor explaining to undergraduates):")
    print(f"A: {response2[:100]}...")
    print()


def example_4_file_upload():
    """Example 4: File upload and analysis"""
    print("=== Example 4: File Upload and Analysis ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Create a sample text file for demonstration
    sample_file = "sample_document.txt"
    with open(sample_file, "w") as f:
        f.write(
            "This is a sample document about artificial intelligence. "
            "AI is revolutionizing many industries including healthcare, "
            "finance, and transportation. Machine learning algorithms "
            "enable computers to learn from data without explicit programming."
        )

    try:
        # Upload file and ask question
        response = api.chat(
            "What is the main topic of this document?", file_path=sample_file, wait_for_processing=True, timeout=60
        )
        print(f"File: {sample_file}")
        print(f"Q: What is the main topic of this document?")
        print(f"A: {response}")
        print()

        # Ask follow-up question about the same file
        response2 = api.chat("What industries are mentioned in the document?", file_path=sample_file)
        print(f"Q: What industries are mentioned in the document?")
        print(f"A: {response2}")
        print()

    except FileNotFoundError:
        print("Sample file not found - this is expected in the demo")
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)


def example_5_conversation_continuation():
    """Example 5: Conversation continuation with ID extraction"""
    print("=== Example 5: Conversation Continuation ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Method 1: Continue conversation by disabling cleanup
    print("Method 1: Using cleanup=False")

    # Start conversation without cleanup
    response1 = api.chat(
        "Tell me about the history of computers",
        cleanup=False,  # Keep conversation alive
        convo_name="Computer History Discussion",
    )
    print(f"Initial: {response1[:100]}...")

    # For demonstration - in real usage you'd extract convo_id from response/error handling
    print("Note: In practice, you'd extract conversation ID from API internals")
    print("The current API doesn't expose conversation ID in successful responses")
    print()

    # Method 2: Using core API for more control
    print("Method 2: Using core API for manual conversation management")

    import uuid

    session_id = str(uuid.uuid4())

    # Create conversation manually using core API
    data_room_response = api.core.create_data_room(
        convo_name="Manual Computer Discussion", session_id=session_id, bot_id="your_bot_id"
    )

    if isinstance(data_room_response, dict) and not data_room_response.get("error"):
        # Extract conversation ID
        convo_id = (
            data_room_response.get("id")
            or data_room_response.get("convoId")
            or data_room_response.get("dataRoomId")
            or data_room_response.get("body", {}).get("dataRoomId")
        )

        if convo_id:
            print(f"✓ Created conversation: {convo_id}")

            # Send first message
            response1 = api.core.user_prompt(
                "What were the first computers like?", session_id=session_id, convo_id=convo_id
            )
            print(f"Q1: What were the first computers like?")
            print(f"A1: {response1[:100]}...")

            # Continue conversation
            response2 = api.core.user_prompt(
                "How did they evolve into personal computers?", session_id=session_id, convo_id=convo_id
            )
            print(f"Q2: How did they evolve into personal computers?")
            print(f"A2: {response2[:100]}...")

            # Clean up manually
            api.core.delete_data_room(convo_id)
            print("✓ Conversation cleaned up")
    print()


def example_6_streaming_modes():
    """Example 6: Streaming vs non-streaming responses"""
    print("=== Example 6: Streaming vs Non-Streaming ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Streaming mode (default)
    print("Streaming mode (default):")
    response_stream = api.chat("Explain the solar system briefly", stream=True)
    print(f"Type: {type(response_stream)}")
    print(f"Response: {response_stream[:100]}...")
    print()

    # Non-streaming mode
    print("Non-streaming mode:")
    response_json = api.chat("Explain the solar system briefly", stream=False)
    print(f"Type: {type(response_json)}")
    if isinstance(response_json, dict):
        print(f"JSON keys: {list(response_json.keys())}")
    else:
        print(f"Response: {response_json[:100]}...")
    print()


def example_7_error_handling():
    """Example 7: Comprehensive error handling"""
    print("=== Example 7: Error Handling ===")

    # Invalid credentials example
    api_invalid = BlockBrainAPI(token="invalid_token", bot_id="invalid_bot")

    response = api_invalid.chat("Hello")

    # Check for errors
    if isinstance(response, dict) and response.get("error"):
        print("✓ Error detected:")
        print(f"  Error: {response.get('error')}")
        if "details" in response:
            details = response["details"]
            print(f"  Status Code: {details.get('status_code')}")
            print(f"  Content: {details.get('content')}")
    else:
        print(f"Unexpected response: {response}")
    print()

    # File not found example
    api_valid = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    try:
        response = api_valid.chat("Analyze this file", file_path="nonexistent_file.pdf")
        if isinstance(response, dict) and response.get("error"):
            print("✓ File error detected:")
            print(f"  Error: {response.get('error')}")
    except FileNotFoundError as e:
        print(f"✓ FileNotFoundError caught: {e}")
    except Exception as e:
        print(f"✓ Other error caught: {e}")
    print()


def example_8_advanced_configuration():
    """Example 8: Advanced configuration options"""
    print("=== Example 8: Advanced Configuration ===")

    # Different bot IDs per request
    api = BlockBrainAPI(token="your_token")  # No default bot_id

    response1 = api.chat("Hello", bot_id="bot_1")
    response2 = api.chat("Hello", bot_id="bot_2")

    print("✓ Different bot IDs per request")
    print()

    # Custom session management
    import uuid

    custom_session = str(uuid.uuid4())

    response = api.chat("Remember this session", session_id=custom_session, cleanup=False)
    print(f"✓ Custom session ID: {custom_session}")
    print()

    # File processing configuration
    response = api.chat(
        "Analyze document with custom settings",
        file_path="document.pdf",
        wait_for_processing=True,
        timeout=600,  # 10 minutes
        cleanup=False,
    )
    print("✓ Custom file processing timeout")
    print()


def example_9_core_api_access():
    """Example 9: Using the core API for advanced operations"""
    print("=== Example 9: Core API Access ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Access core API methods
    print("Available core API methods:")
    core_methods = [method for method in dir(api.core) if not method.startswith("_")]
    for method in core_methods:
        print(f"  - api.core.{method}()")
    print()

    # Example: Manual conversation management
    import uuid

    session_id = str(uuid.uuid4())

    # 1. Create data room
    data_room = api.core.create_data_room(convo_name="Core API Demo", session_id=session_id, bot_id="your_bot_id")
    print(f"✓ Created data room: {type(data_room)}")

    # 2. Add context
    if isinstance(data_room, dict) and not data_room.get("error"):
        convo_id = data_room.get("body", {}).get("dataRoomId")
        if convo_id:
            context_result = api.core.add_context(convo_id=convo_id, context="You are a helpful AI assistant")
            print(f"✓ Added context: {type(context_result)}")

            # 3. Send user prompt
            response = api.core.user_prompt(
                content="Hello, who are you?", session_id=session_id, convo_id=convo_id, stream=True
            )
            print(f"✓ Sent prompt: {response[:50]}...")

            # 4. Clean up
            delete_result = api.core.delete_data_room(convo_id)
            print(f"✓ Cleaned up: {type(delete_result)}")
    print()


def example_10_practical_scenarios():
    """Example 10: Real-world practical scenarios"""
    print("=== Example 10: Practical Scenarios ===")

    api = BlockBrainAPI(token="your_token", bot_id="your_bot_id")

    # Scenario 1: Document Q&A system
    print("Scenario 1: Document Q&A System")

    def document_qa(file_path, questions):
        """Ask multiple questions about a document"""
        results = []
        for question in questions:
            response = api.chat(question, file_path=file_path)
            results.append({"question": question, "answer": response})
        return results

    # questions = ["What is this document about?", "What are the key findings?"]
    # results = document_qa("research_paper.pdf", questions)
    print("✓ Multi-question document analysis function")
    print()

    # Scenario 2: Contextual chatbot
    print("Scenario 2: Contextual Chatbot")

    def create_contextual_bot(context, bot_name="Assistant"):
        """Create a chatbot with specific context"""

        def chat_with_context(message):
            return api.chat(message, context=context, convo_name=f"{bot_name} Session")

        return chat_with_context

    # Expert chatbots
    physics_bot = create_contextual_bot(
        "You are a physics professor. Explain concepts clearly with examples.", "Physics Professor"
    )

    coding_bot = create_contextual_bot(
        "You are a senior software engineer. Provide practical coding advice.", "Coding Mentor"
    )

    print("✓ Created contextual chatbots")
    print()

    # Scenario 3: Batch processing
    print("Scenario 3: Batch Processing")

    def batch_process_questions(questions, context=None):
        """Process multiple questions efficiently"""
        results = []
        for i, question in enumerate(questions):
            try:
                response = api.chat(question, context=context, convo_name=f"Batch {i+1}")
                results.append({"id": i + 1, "question": question, "answer": response, "success": True})
            except Exception as e:
                results.append({"id": i + 1, "question": question, "error": str(e), "success": False})
        return results

    # questions = ["What is AI?", "How does ML work?", "Explain neural networks"]
    # results = batch_process_questions(questions)
    print("✓ Batch processing function")
    print()


def main():
    """Run all examples"""
    print("BlockBrain API Python Client - Comprehensive Examples")
    print("=" * 60)
    print()

    # Note about credentials
    print("📝 Note: Replace 'your_token_here' and 'your_bot_id_here' with actual credentials")
    print("🔧 Most examples will show errors with placeholder credentials - this is expected")
    print()

    examples = [
        example_1_basic_setup,
        example_2_simple_chat,
        example_3_chat_with_context,
        example_4_file_upload,
        example_5_conversation_continuation,
        example_6_streaming_modes,
        example_7_error_handling,
        example_8_advanced_configuration,
        example_9_core_api_access,
        example_10_practical_scenarios,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"Example {example.__name__} error: {e}")
            print("(This is expected with placeholder credentials)")
            print()

    print("✅ All examples completed!")
    print()
    print("Next steps:")
    print("1. Replace placeholder credentials with real ones")
    print("2. Try running individual examples")
    print("3. Modify examples for your specific use cases")
    print("4. Check the README.md for more documentation")


if __name__ == "__main__":
    main()
