# Changelog

All notable changes to the BlockBrain API Python Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-01-07

### Added
- **Model Selection & Management**: Complete model selection functionality
  - `get_available_models()` method to retrieve all available LLM models
  - `change_data_room_model()` method to change models for existing conversations
  - `default_model` parameter in `BlockBrainAPI.__init__()` for setting default model
  - `model` parameter in all chat methods for per-request model overrides
  - Model precedence system: explicit model > default_model > API default
- **Comprehensive Documentation**:
  - Model selection examples in README.md
  - Dedicated model selection example in examples.py
  - Updated API reference with model parameters
  - Complete usage patterns and scenarios
- **Enhanced Testing**:
  - 11 comprehensive E2E tests for model selection functionality
  - Tests cover model listing, defaults, overrides, precedence, and error handling
  - Improved test robustness for file upload scenarios

### Changed
- **API Enhancement**: All chat methods now accept optional `model` parameter
- **Data Room Creation**: `create_data_room()` now supports model parameter
- **Package Metadata**: Updated description to include model selection
- **Keywords**: Added "model-selection" and "llm" to package keywords
- **Documentation**: Comprehensive updates throughout README.md and examples.py

### Fixed
- **Test Robustness**: Fixed markdown file upload test to handle AI correctly identifying different file types
- **Code Quality**: Applied consistent formatting and linting across all files

## [0.1.2] - 2024-12-XX

### Added
- **End-to-End Testing Suite**: Comprehensive E2E tests with live API validation
  - 39 E2E tests covering all major functionality
  - Resource tracking and automatic cleanup
  - GitHub Actions CI/CD integration
- **Advanced Error Handling**: Improved error detection and reporting
- **File Processing Enhancements**: Better file upload status tracking and processing
- **Production Readiness**: Enhanced logging, error handling, and resource management

### Changed
- **Test Infrastructure**: Complete overhaul of testing framework
- **Code Quality**: Implemented pre-commit hooks for consistent code quality
- **Documentation**: Enhanced examples and usage patterns

### Fixed
- **File Processing**: Improved file upload and processing reliability
- **Error Handling**: Better error message extraction and handling
- **Resource Cleanup**: Enhanced cleanup mechanisms for test resources

## [0.1.1] - 2024-11-XX

### Added
- **Core API Methods**: Low-level API access through `api.core`
- **Conversation Management**: Manual conversation handling capabilities
- **File Upload Support**: Document upload and analysis functionality
- **Context Management**: AI response guidance through custom context
- **Streaming Support**: Real-time response streaming capabilities

### Changed
- **API Structure**: Introduced dual-level API (high-level + low-level)
- **Response Handling**: Improved response parsing and error detection

### Fixed
- **Connection Handling**: Enhanced HTTP request reliability
- **Response Parsing**: Better handling of various response formats

## [0.1.0] - 2024-10-XX

### Added
- **Initial Release**: Basic BlockBrain API Python client
- **Simple Chat Interface**: Single `chat()` method for all interactions
- **Authentication**: Token-based authentication with tenant support
- **Basic Configuration**: API endpoint and logging configuration
- **Documentation**: Initial README with basic usage examples

### Features
- Simple question-answering capabilities
- Basic error handling
- HTTP client with requests library
- Python 3.8+ support

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.y.z): Incompatible API changes
- **MINOR** version (x.Y.z): New functionality in a backwards compatible manner
- **PATCH** version (x.y.Z): Backwards compatible bug fixes

## Release Process

1. **Development**: New features and fixes are developed on feature branches
2. **Testing**: All changes must pass the comprehensive E2E test suite
3. **Documentation**: README.md and examples.py are updated for new features
4. **Version Bump**: Version numbers are updated in `__init__.py` and `pyproject.toml`
5. **Changelog**: This file is updated with all changes
6. **Release**: Tagged releases are created on GitHub
7. **PyPI**: New versions are published to the Python Package Index

## Contributing

When contributing to this project:

1. Add entries to this changelog under "Unreleased" section
2. Follow the established format for consistency
3. Include the type of change (Added/Changed/Deprecated/Removed/Fixed/Security)
4. Reference issue numbers where applicable
5. Update version numbers when creating releases

## Links

- [PyPI Package](https://pypi.org/project/blockbrain-api/)
- [GitHub Repository](https://github.com/blockbrain/blockbrain-api-python)
- [Documentation](https://docs.blockbrain.ai)
- [Issue Tracker](https://github.com/blockbrain/blockbrain-api-python/issues)
