# BlockBrain Python SDK - Claude Development Guide

This document provides comprehensive context and configuration for Claude sessions working on the BlockBrain Python SDK. It captures essential patterns, common issues, and step-by-step workflows for extending the SDK.

## 📋 Project Overview

**Purpose**: Python client library for BlockBrain AI API
**Current Version**: 0.1.2
**API Type**: Chat/AI service with data rooms, file uploads, and conversation management
**Test Coverage**: 37/39 E2E tests passing with live API
**Package Status**: Published on PyPI as `blockbrain-api`

## 🚀 Quick Start for New Claude Sessions

1. **Read this entire file first** - contains critical patterns and gotchas
2. **Check current test status**: `source .env && python -m pytest tests/e2e/ -v --tb=short`
3. **Understand the API structure** by examining `blockbrain_api/core.py`
4. **Review recent changes** in git history: `git log --oneline -10`
5. **Use TodoWrite tool** to track your work and progress

## 🏗️ Project Architecture

### Core Files Structure
```
blockbrain_api/
├── __init__.py          # Package exports and version
├── core.py              # Core API methods (GET/POST operations)
├── chat.py              # High-level chat interface
├── api.py               # Main API class (combines core + chat)

tests/
├── conftest.py          # Pytest fixtures and configuration
├── utils/cleanup.py     # Resource tracking and cleanup
├── e2e/                 # End-to-end tests with live API
│   ├── test_basic_connectivity.py
│   ├── test_chat_flows.py
│   ├── test_data_room_operations.py
│   ├── test_error_scenarios.py
│   └── test_file_operations.py
└── test_data/           # Sample files for testing
```

### Key Classes
- **`BlockBrainAPI`**: Main user-facing class (high-level interface)
- **`BlockBrainCore`**: Low-level API operations (direct HTTP calls)
- **`BlockBrainChat`**: Convenience methods for chat operations

## 🔧 API Patterns & Conventions

### Response Structure Pattern
**Critical**: BlockBrain API often returns nested responses:
```python
# Typical API response structure
{
    "body": {
        "_id": "actual_id_here",
        "name": "resource_name",
        "status": "success"
    },
    "code": 200,
    "key": None
}
```

**Always extract data like this:**
```python
# Extract ID from nested response
item_id = (
    response.get("id")
    or response.get("convoId")
    or response.get("dataRoomId")
    or response.get("body", {}).get("_id")
    or response.get("body", {}).get("id")
)
```

### Method Signature Patterns
**Common parameter patterns:**
```python
# File upload signature
upload_file(file_path: str, convo_id: str, session_id: str)

# Data room creation
create_data_room(convo_name: str, session_id: str, bot_id: str)

# Chat methods use convo_id, not data_room_id
chat("message", convo_id="room_id")
```

### Chat Response Types
**Critical**: Chat responses can be either strings OR dicts:
```python
# Always handle both types
assert isinstance(response, (str, dict))

if isinstance(response, str):
    response_text = response.lower()
else:
    response_text = (
        response.get("response")
        or response.get("answer")
        or response.get("content")
        or ""
    ).lower()
```

### Error Message Extraction
```python
# Error messages are often nested in content.body
if isinstance(response, dict) and "error" in response:
    if "content" in response and "body" in response["content"]:
        error_msg = str(response["content"]["body"]).lower()
    else:
        error_msg = str(response.get("error", "")).lower()
```

## 🧪 Testing Framework

### Test Philosophy: Execute → GET Verify → Cleanup
1. **Execute**: Perform the operation (POST/PUT/PATCH)
2. **GET Verify**: Use GET requests to confirm operation succeeded
3. **Cleanup**: Remove test resources and verify cleanup

### Resource Tracking
**Always use `resource_tracker` fixture:**
```python
def test_example(api_client, resource_tracker, api_credentials):
    # Create resource
    response = api_client.core.create_data_room(name, session_id, bot_id)
    room_id = extract_id_from_response(response)

    # Track for cleanup
    resource_tracker.track_data_room(room_id)

    # Test continues...
```

### Test Environment
- **Local**: Use `.env` file with same secrets as CI
- **CI**: Environment variables set in GitHub Actions
- **Required**: `BLOCKBRAIN_TOKEN` and `BLOCKBRAIN_BOT_ID`

### Running Tests
```bash
# All E2E tests
source .env && python -m pytest tests/e2e/ -v

# Specific test file
source .env && python -m pytest tests/e2e/test_chat_flows.py -v

# Single test
source .env && python -m pytest tests/e2e/test_chat_flows.py::TestChatFlows::test_simple_chat -v
```

## 🔄 Development Workflow

### Pre-commit Hooks
The project uses pre-commit hooks for code quality:
- **black**: Code formatting
- **flake8**: Linting
- **isort**: Import sorting
- **Standard checks**: Trailing whitespace, YAML validation, etc.

### Git Workflow
1. **Always test locally first**: `source .env && python -m pytest tests/e2e/ -v`
2. **Commit with descriptive messages**: Follow conventional commit format
3. **Pre-commit hooks run automatically**: Fix any issues they report
4. **Push to trigger CI**: GitHub Actions will run full test suite

## 📝 Adding New Endpoints: Step-by-Step Process

### Phase 1: Analysis & Planning
1. **Examine the curl example** provided by user
2. **Identify request method** (GET, POST, PUT, DELETE)
3. **Extract parameters** and their types
4. **Understand expected response structure**
5. **Plan test scenarios** (success, error, edge cases)

### Phase 2: Implementation
1. **Add method to `blockbrain_api/core.py`**:
   ```python
   def new_method(self, param1: str, param2: str) -> Dict[str, Any]:
       """Method description with parameters and return type."""
       endpoint = f"/api/endpoint/{param1}"
       data = {"param2": param2}
       return self._make_request("POST", endpoint, json=data)
   ```

2. **Add convenience method to `blockbrain_api/chat.py`** (if applicable)
3. **Update `__all__` exports** if needed
4. **Consider parameter validation** and error handling

### Phase 3: Testing
1. **Create E2E tests** in appropriate test file:
   ```python
   def test_new_method(self, api_client, resource_tracker, api_credentials):
       """Test new method with live API."""
       # Execute
       response = api_client.core.new_method(param1, param2)

       # Extract and track resources
       resource_id = extract_id_from_response(response)
       resource_tracker.track_resource(resource_id)

       # GET Verify
       verification = api_client.core.get_resource(resource_id)
       assert verification is not None

       # Additional assertions...
   ```

2. **Test error scenarios**:
   - Invalid parameters
   - Non-existent resources
   - Authentication errors

3. **Run tests locally**: `source .env && python -m pytest tests/e2e/ -v`

### Phase 4: Documentation & Cleanup
1. **Update docstrings** with examples
2. **Consider README updates** if it's a major feature
3. **Version bump** if needed for PyPI release
4. **Commit with comprehensive message**

## ⚠️ Common Issues & Solutions

### Issue: Parameter Mismatches
**Problem**: Method signatures don't match API requirements
**Solution**: Always check existing working methods for parameter patterns

### Issue: Response Structure Confusion
**Problem**: Assuming flat response structure
**Solution**: Use flexible ID extraction pattern (see API Patterns section)

### Issue: Chat Response Type Errors
**Problem**: Assuming chat always returns dict
**Solution**: Always check for both string and dict responses

### Issue: Upload Status Polling Timeouts
**Problem**: Complex upload status tracking fails
**Solution**: Use simple time delays instead of polling: `time.sleep(5)`

### Issue: Cleanup Failures
**Problem**: Test resources not properly cleaned up
**Solution**: Always use `resource_tracker` and verify cleanup in tests

### Issue: Local vs CI Test Differences
**Problem**: Tests pass locally but fail in CI
**Solution**: Ensure `.env` file has same values as GitHub Actions secrets

## 📚 Important Files Reference

### Configuration Files
- **`pyproject.toml`**: Package configuration, dependencies, version
- **`.pre-commit-config.yaml`**: Code quality hooks
- **`.env.example`**: Template for local environment variables
- **`.gitignore`**: Standard Python gitignore with .env excluded

### Testing Files
- **`tests/conftest.py`**: Pytest configuration and fixtures
- **`tests/utils/cleanup.py`**: Resource tracking and cleanup utilities
- **`tests/test_data/`**: Sample files for upload testing

### Core Implementation
- **`blockbrain_api/core.py`**: All direct API calls
- **`blockbrain_api/chat.py`**: High-level convenience methods
- **`blockbrain_api/api.py`**: Main user-facing class

## 🎯 Key Success Metrics

- **Test Coverage**: Maintain 95%+ E2E test passing rate
- **API Compatibility**: All methods work with live API
- **Error Handling**: Graceful handling of all error scenarios
- **Resource Cleanup**: No test resources left in system
- **Code Quality**: All pre-commit hooks pass
- **Documentation**: Clear docstrings and examples

## 🔮 Future Considerations

When adding new endpoints, consider:
1. **Streaming support** - Does the endpoint support streaming responses?
2. **File handling** - Does it involve file uploads/downloads?
3. **Resource management** - What resources need cleanup?
4. **Error scenarios** - What can go wrong and how to handle it?
5. **Testing complexity** - How to verify the operation worked?

---

**Remember**: Always test locally with live API before pushing. The E2E tests are the source of truth for API compatibility.
