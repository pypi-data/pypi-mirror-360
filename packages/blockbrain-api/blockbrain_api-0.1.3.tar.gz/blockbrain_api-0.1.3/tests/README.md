# BlockBrain API Testing Suite

This directory contains comprehensive end-to-end tests for the BlockBrain API Python SDK.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_data/              # Sample files for testing
│   ├── sample.txt          # Text file for upload tests
│   ├── sample.json         # JSON file for data processing tests
│   └── sample.md           # Markdown file for structure tests
├── e2e/                    # End-to-end tests
│   ├── test_basic_connectivity.py      # Authentication and connectivity
│   ├── test_chat_flows.py              # Chat operations with verification
│   ├── test_file_operations.py         # File upload and processing
│   ├── test_data_room_operations.py    # Data room management
│   └── test_error_scenarios.py         # Error handling and edge cases
└── utils/
    └── cleanup.py          # Resource cleanup utilities
```

## Test Categories

### 1. Basic Connectivity Tests
- API client initialization
- Token authentication
- Network connectivity
- Health checks
- Error handling for auth failures

### 2. Chat Flow Tests
- Simple chat interactions
- Context-aware conversations
- Conversation continuity
- File integration in chat
- Response quality verification

### 3. File Operations Tests
- File upload (text, JSON, markdown)
- Upload status tracking
- File processing verification
- Multiple file handling
- File-chat integration

### 4. Data Room Tests
- Room creation and deletion
- Context management
- LLM model changes
- Room listing and search
- Lifecycle management

### 5. Error Scenario Tests
- Invalid authentication
- Network timeouts
- Malformed requests
- Edge case inputs
- Rate limiting
- Recovery testing

## Test Verification Pattern

Each test follows the **Execute → GET Verify → Cleanup** pattern:

1. **Execute**: Perform operation (POST/PUT/PATCH)
2. **GET Verify**: Use GET requests to confirm operation succeeded
3. **Cleanup**: Remove test resources and verify cleanup

Example:
```python
import uuid

# Execute: Create data room
session_id = str(uuid.uuid4())
bot_id = "your_bot_id_here"  # Use your actual bot ID
room = api_client.core.create_data_room("TEST_ROOM", session_id, bot_id)

# Extract room ID (handle nested response structure)
room_id = (
    room.get("id")
    or room.get("convoId")
    or room.get("dataRoomId")
    or room.get("body", {}).get("dataRoomId")
    or room.get("body", {}).get("_id")
)

# GET Verify: Confirm room exists
room_details = api_client.core.get_data_room(room_id)
room_data = room_details.get("body", room_details)
actual_room_id = room_data.get("_id") or room_data.get("id") or room_details.get("id")
assert actual_room_id == room_id

# Cleanup: Remove room and verify deletion
api_client.core.delete_data_room(room_id)
deleted_check = api_client.core.get_data_room(room_id)
assert "error" in deleted_check
```

## Running Tests

### Prerequisites

Set environment variables for live API testing:
```bash
export BLOCKBRAIN_TOKEN="your_api_token"
export BLOCKBRAIN_BOT_ID="your_bot_id"
export BLOCKBRAIN_BASE_URL="https://blocky.theblockbrain.ai"  # optional
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Only E2E Tests
```bash
pytest tests/e2e/ -v -m e2e
```

### Skip E2E Tests (Unit Tests Only)
```bash
pytest tests/ -v -m "not e2e"
```

### Run Specific Test Categories
```bash
# Connectivity tests only
pytest tests/e2e/test_basic_connectivity.py -v

# Chat tests only
pytest tests/e2e/test_chat_flows.py -v

# File operation tests only
pytest tests/e2e/test_file_operations.py -v
```

### Run with Timeout Protection
```bash
pytest tests/e2e/ -v --timeout=300
```

## CI/CD Integration

### GitHub Actions Secrets

For E2E tests to run in CI/CD, set these repository secrets:

1. **BLOCKBRAIN_TOKEN**: Your API authentication token
2. **BLOCKBRAIN_BOT_ID**: Your bot ID for chat operations
3. **BLOCKBRAIN_BASE_URL**: API base URL (optional, defaults to production)

### GitHub Actions Workflow

The workflow automatically:
- Runs unit tests for all Python versions (3.8-3.12)
- Runs E2E tests only when secrets are available
- Skips E2E tests for external PRs (security)
- Continues deployment even if some tests fail (with warnings)

## Test Resource Management

### Automatic Cleanup
- All test resources are prefixed with `E2E_TEST_`
- Resources are tracked during creation
- Automatic cleanup after each test
- Session-level cleanup for failed tests

### Manual Cleanup
```python
from tests.utils.cleanup import cleanup_test_resources_by_prefix

# Clean up any leftover test resources
cleanup_test_resources_by_prefix(api_client, "E2E_TEST_")
```

## Test Data

### Sample Files
- **sample.txt**: Multi-line text with various topics
- **sample.json**: Structured data with metrics and features
- **sample.md**: Markdown with headers, tables, and code blocks

### Generated Test Names
Tests use unique identifiers to prevent conflicts:
```python
# Format: E2E_TEST_{timestamp}_{random_id}
# Example: E2E_TEST_1703123456_7892
```

## Debugging Tests

### Verbose Output
```bash
pytest tests/e2e/ -v -s --tb=long
```

### Debug Specific Test
```bash
pytest tests/e2e/test_chat_flows.py::TestChatFlows::test_simple_chat_flow -v -s
```

### Enable API Logging
Tests automatically enable debug logging when running with credentials.

### Test Failure Analysis
- Check API credentials are valid
- Verify network connectivity
- Review cleanup logs for resource conflicts
- Check rate limiting if multiple failures

## Contributing Tests

### Adding New Tests
1. Follow the existing test structure
2. Use provided fixtures (`api_client`, `resource_tracker`, etc.)
3. Implement proper cleanup
4. Add GET verification for operations
5. Handle errors gracefully

### Test Naming Convention
- Test classes: `TestFeatureName`
- Test methods: `test_specific_behavior`
- Test resources: `E2E_TEST_` prefix

### Fixture Usage
```python
def test_example(api_client, resource_tracker, test_data_room):
    # api_client: Authenticated API client
    # resource_tracker: Automatic cleanup tracking
    # test_data_room: Pre-created data room for testing
    pass
```

## Performance Considerations

- Tests include delays between requests (rate limit friendly)
- Timeout protection prevents hanging tests
- Parallel execution avoided for API stability
- Resource limits prevent excessive API usage

## Security Notes

- API credentials never logged or exposed
- Test resources isolated with unique prefixes
- Automatic cleanup prevents data leakage
- Error messages sanitized in CI logs
