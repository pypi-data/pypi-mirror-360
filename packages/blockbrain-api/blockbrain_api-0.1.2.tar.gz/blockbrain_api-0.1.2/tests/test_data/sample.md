# E2E Test Document

## Overview
This is a **markdown document** for testing file processing capabilities.

## Features Being Tested
- File upload functionality
- Document parsing and analysis
- Chat integration with uploaded files
- Content extraction and summarization

## Test Data Points
| Metric | Value | Status |
|--------|-------|--------|
| Upload Speed | Fast | ✅ |
| Processing | Automated | ✅ |
| Integration | Seamless | ✅ |

## Code Example
```python
from blockbrain_api import BlockBrainAPI

api = BlockBrainAPI(token="test_token", bot_id="test_bot")
response = api.chat("Analyze this document", file_path="sample.md")
```

## Conclusion
This document should be successfully processed and its content should be accessible through the API.
