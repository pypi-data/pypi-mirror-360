# BlockBrain API Python Client

A modern, streamlined Python client for the BlockBrain API featuring a unified chat interface, file processing, context management, and real-time streaming responses.

## ✨ Key Features

- **🎯 Unified Interface**: Single `chat()` method handles all scenarios
- **📁 Smart File Processing**: Upload documents with automatic processing detection
- **🧠 Context Management**: Guide AI responses with custom context
- **💬 Conversation Continuity**: Seamless multi-turn conversations
- **⚡ Real-time Streaming**: Live response streaming (default) or batch processing
- **🔧 Dual-Level API**: High-level simplicity + low-level control
- **🏗️ Production Ready**: Type hints, error handling, and logging control
- **🔒 Secure**: Token-based authentication with tenant isolation

## 🚀 Quick Start

### Installation

```bash
pip install blockbrain-api
```

### Basic Usage

```python
from blockbrain_api import BlockBrainAPI

# Initialize client
api = BlockBrainAPI(
    token="your_api_token",
    bot_id="your_bot_id"
)

# Ask a question
response = api.chat("What is artificial intelligence?")
print(response)
# Output: "Artificial intelligence (AI) refers to the simulation of human intelligence..."
```

### File Analysis

```python
# Upload and analyze a document
response = api.chat(
    "Summarize the key points in this document",
    file_path="research_paper.pdf"
)
print(response)
```

### Contextual AI Assistant

```python
# Create a specialized assistant with context
response = api.chat(
    "Explain machine learning algorithms",
    context="You are a computer science professor teaching undergraduate students. Use simple language and provide examples."
)
print(response)
```

## 📚 API Reference

### Core Method: `api.chat()`

The `chat()` method is your main interface to BlockBrain. It intelligently handles all chat scenarios:

```python
api.chat(
    message: str,                           # Your question or message
    bot_id: Optional[str] = None,          # Bot ID (uses default if not set)
    file_path: Optional[str] = None,       # Path to file for upload
    context: Optional[str] = None,         # Context to guide the AI
    convo_id: Optional[str] = None,        # Continue existing conversation
    session_id: Optional[str] = None,      # Custom session ID
    convo_name: str = "Chat Session",      # Name for new conversations
    cleanup: bool = True,                  # Auto-delete conversation after
    wait_for_processing: bool = True,      # Wait for file processing
    timeout: int = 300,                    # File processing timeout (seconds)
    stream: bool = True                    # Enable streaming responses
) -> Union[str, Dict[str, Any]]
```

### Advanced API: `api.core`

For advanced use cases, access the low-level API:

```python
# Manual conversation management
api.core.create_data_room(convo_name, session_id, bot_id)
api.core.user_prompt(content, session_id, convo_id, stream=True)
api.core.upload_file(file_path, convo_id, session_id)
api.core.add_context(convo_id, context)
api.core.delete_data_room(convo_id)

# File processing utilities
api.core.check_file_upload_status(convo_id)
api.core.wait_for_file_processing(convo_id, timeout=300)
```

## 💡 Usage Examples

### 1. Simple Q&A

```python
api = BlockBrainAPI(token="your_token", bot_id="your_bot")

response = api.chat("What are the benefits of renewable energy?")
print(response)
```

### 2. Document Analysis

```python
# Analyze a PDF document
response = api.chat(
    "What methodology was used in this research?",
    file_path="research_study.pdf",
    wait_for_processing=True
)

# Multiple questions about the same document
questions = [
    "What are the main findings?",
    "What are the limitations?",
    "What future research is suggested?"
]

for question in questions:
    answer = api.chat(question, file_path="research_study.pdf")
    print(f"Q: {question}")
    print(f"A: {answer}\n")
```

### 3. Contextual AI Assistants

```python
# Create a coding mentor
coding_context = """
You are a senior software engineer and mentor. Provide practical, 
production-ready advice. Include code examples and best practices.
Focus on clean, maintainable solutions.
"""

response = api.chat(
    "How should I structure a REST API in Python?",
    context=coding_context
)

# Create a medical advisor
medical_context = """
You are a medical professional providing health information. 
Always recommend consulting healthcare providers for serious concerns.
Use clear, accessible language.
"""

response = api.chat(
    "What are the symptoms of vitamin D deficiency?",
    context=medical_context
)
```

### 4. Multi-turn Conversations

**Option A: Using Core API (Recommended for conversation management)**

```python
import uuid

# Set up conversation
session_id = str(uuid.uuid4())
data_room = api.core.create_data_room(
    convo_name="Technical Discussion",
    session_id=session_id,
    bot_id="your_bot_id"
)

# Extract conversation ID
convo_id = data_room.get("body", {}).get("dataRoomId")

if convo_id:
    # First message
    response1 = api.core.user_prompt(
        "Tell me about Python web frameworks",
        session_id=session_id,
        convo_id=convo_id
    )
    print(f"AI: {response1}")
    
    # Follow-up questions maintain context
    response2 = api.core.user_prompt(
        "Which one is best for beginners?",
        session_id=session_id,
        convo_id=convo_id
    )
    print(f"AI: {response2}")
    
    response3 = api.core.user_prompt(
        "Can you show me a simple example?",
        session_id=session_id,
        convo_id=convo_id
    )
    print(f"AI: {response3}")
    
    # Clean up when done
    api.core.delete_data_room(convo_id)
```

**Option B: Using chat() with cleanup=False**

```python
# Start conversation without auto-cleanup
response1 = api.chat(
    "Let's discuss climate change solutions",
    cleanup=False,
    convo_name="Climate Discussion"
)

# Note: In production, you'd need to track conversation IDs
# for proper continuation with the current API design
```

### 5. Streaming vs Batch Responses

```python
# Streaming mode (default) - real-time text assembly
response = api.chat("Explain photosynthesis", stream=True)
print(f"Final response: {response}")
# Output: Complete assembled text

# Batch mode - full JSON response
response = api.chat("Explain photosynthesis", stream=False)
print(f"Response type: {type(response)}")
print(f"Status: {response.get('status')}")
print(f"Content: {response.get('body')}")
```

### 6. Error Handling

```python
response = api.chat("Hello world")

# Check for errors
if isinstance(response, dict) and response.get('error'):
    print(f"❌ Error: {response['error']}")
    
    # Get detailed error info
    if 'details' in response:
        details = response['details']
        status_code = details.get('status_code')
        error_content = details.get('content', {})
        
        print(f"Status Code: {status_code}")
        print(f"Error Type: {error_content.get('key')}")
        print(f"Message: {error_content.get('body')}")
else:
    print(f"✅ Success: {response}")

# File upload error handling
try:
    response = api.chat("Analyze this", file_path="missing_file.pdf")
except FileNotFoundError:
    print("❌ File not found")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## ⚙️ Configuration

### Basic Configuration

```python
api = BlockBrainAPI(
    token="your_api_token",              # Required: Your API token
    bot_id="your_bot_id"                 # Required: Your bot ID
)
```

### Advanced Configuration

```python
api = BlockBrainAPI(
    token="your_api_token",
    bot_id="your_bot_id",
    base_url="https://blocky.theblockbrain.ai",  # Custom API endpoint
    tenant_domain="your_company",               # Multi-tenant setup
    enable_logging=True,                        # Enable debug logging
    log_level="DEBUG"                          # Set logging level
)
```

### Dynamic Bot Selection

```python
# Use different bots for different purposes
api = BlockBrainAPI(token="your_token")  # No default bot

# Use specialized bots per request
technical_response = api.chat("Explain APIs", bot_id="technical_bot_id")
creative_response = api.chat("Write a story", bot_id="creative_bot_id")
```

### Session Management

```python
import uuid

# Custom session for conversation tracking
custom_session = str(uuid.uuid4())

response = api.chat(
    "Start of our conversation",
    session_id=custom_session,
    cleanup=False
)
```

## 🛠️ Response Formats

### Successful Streaming Response (Default)
```python
response = api.chat("Hello")
# Type: str
# Example: "Hello! How can I help you today?"
```

### Successful Batch Response
```python
response = api.chat("Hello", stream=False)
# Type: dict
# Example: {
#   "body": {...},
#   "status": "success",
#   "metadata": {...}
# }
```

### Error Response
```python
response = api.chat("Hello")  # with invalid credentials
# Type: dict
# Example: {
#   "error": "Failed to create data room",
#   "details": {
#     "error": True,
#     "status_code": 401,
#     "content": {
#       "code": 401,
#       "key": "UNAUTHORIZED",
#       "body": "Invalid token"
#     }
#   }
# }
```

## 🎯 Real-World Use Cases

### Document Q&A System

```python
class DocumentQA:
    def __init__(self, api_token, bot_id):
        self.api = BlockBrainAPI(token=api_token, bot_id=bot_id)
    
    def analyze_document(self, file_path, questions):
        """Analyze a document with multiple questions"""
        results = []
        
        for question in questions:
            try:
                answer = self.api.chat(
                    question,
                    file_path=file_path,
                    wait_for_processing=True,
                    timeout=600  # 10 minutes for large files
                )
                results.append({
                    "question": question,
                    "answer": answer,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        return results

# Usage
qa_system = DocumentQA("your_token", "your_bot")
questions = [
    "What is the main topic of this document?",
    "What are the key findings?",
    "What recommendations are made?"
]
results = qa_system.analyze_document("report.pdf", questions)
```

### Contextual Chatbot Factory

```python
def create_specialist_bot(api, specialty_context, name):
    """Create a specialized chatbot with specific context"""
    def chat_with_context(message):
        return api.chat(
            message,
            context=specialty_context,
            convo_name=f"{name} Session"
        )
    return chat_with_context

# Create different specialist bots
api = BlockBrainAPI(token="your_token", bot_id="your_bot")

# Medical information bot
medical_bot = create_specialist_bot(
    api,
    "You are a medical information assistant. Provide accurate health information but always recommend consulting healthcare professionals.",
    "Medical Assistant"
)

# Coding mentor bot
coding_bot = create_specialist_bot(
    api,
    "You are a senior software engineer. Provide practical coding advice with examples and best practices.",
    "Coding Mentor"
)

# Business advisor bot
business_bot = create_specialist_bot(
    api,
    "You are a business consultant. Provide strategic advice based on industry best practices and data-driven insights.",
    "Business Advisor"
)

# Usage
health_info = medical_bot("What are the symptoms of dehydration?")
coding_help = coding_bot("How do I optimize database queries?")
business_advice = business_bot("How should I price my SaaS product?")
```

## 📖 Complete Examples

For comprehensive examples covering all features, see [`examples.py`](examples.py):

```bash
python examples.py
```

The examples include:
- **Basic Setup & Configuration**
- **Simple Chat Interactions** 
- **File Upload & Analysis**
- **Context Management**
- **Conversation Continuation**
- **Streaming vs Batch Modes**
- **Error Handling Patterns**
- **Advanced Core API Usage**
- **Production Use Cases**

## 🔧 Development

### Installing for Development

```bash
# Clone the repository
git clone https://github.com/blockbrain/blockbrain-api-python
cd blockbrain-api-python

# Install with development dependencies
pip install -e ".[dev]"
```

### Building the Package

```bash
# Build distribution packages
python setup.py sdist bdist_wheel

# Install locally
pip install .

# Run examples
python examples.py
```

### Testing

```bash
# Run with your credentials
export BLOCKBRAIN_TOKEN="your_token"
export BLOCKBRAIN_BOT_ID="your_bot_id"

python examples.py
```

## 📋 Requirements

- **Python**: 3.7+
- **Dependencies**: `requests >= 2.25.0`
- **API Access**: BlockBrain API token and bot ID

## 🤝 Support & Resources

### Documentation & Examples
- **📋 Complete Examples**: [`examples.py`](examples.py) - Comprehensive usage examples
- **📚 API Documentation**: [docs.blockbrain.ai](https://docs.blockbrain.ai)
- **🔧 Core API Reference**: Access via `api.core.*` methods

### Getting Help
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/blockbrain/blockbrain-api-python/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/blockbrain/blockbrain-api-python/discussions)  
- **✉️ Direct Support**: support@blockbrain.ai

### Community
- **🌟 Star on GitHub**: Show your support
- **🔀 Contribute**: Pull requests welcome
- **📢 Share**: Help others discover BlockBrain

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready to get started?** Install the package and run the examples to see BlockBrain in action! 🚀