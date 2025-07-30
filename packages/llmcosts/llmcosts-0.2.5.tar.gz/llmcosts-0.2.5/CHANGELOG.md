# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5] - 2025-Jul-08

0.2.3/0.2.4 bad releases.

### Added
- **Auto-extraction of `base_url` from OpenAI clients**: The `LLMTrackingProxy` now automatically extracts the `base_url` from OpenAI client instances, eliminating the need for manual specification in most cases
- **Enhanced DeepSeek support**: Improved integration with DeepSeek API by automatically detecting custom base URLs from client configuration
- **Comprehensive end-to-end testing**: Added robust test coverage for `base_url` functionality including integration tests with real API calls

### Changed
- **Improved user experience**: Users no longer need to manually specify `base_url` when using standard OpenAI clients or providers with custom endpoints
- **Enhanced proxy initialization**: `LLMTrackingProxy` now intelligently handles `base_url` extraction with fallback to explicit parameter if provided
- **Better error handling**: Graceful handling of `base_url` extraction with proper string conversion to avoid JSON serialization issues

### Fixed
- **Dependency management**: Moved provider-specific SDKs (`openai`, `anthropic`, etc.) from main dependencies to optional extras, reducing core package size
- **Test reliability**: Updated DeepSeek tests to use real API calls and verify `base_url` functionality end-to-end
- **JSON serialization**: Fixed potential issues with `base_url` serialization in usage payloads

### Technical Details
- **Auto-detection**: `base_url` is automatically extracted from `client.base_url` attribute when available
- **Fallback behavior**: Explicit `base_url` parameter still takes precedence over auto-extracted values
- **String conversion**: Ensures `base_url` is always a string to prevent JSON serialization errors
- **Backward compatibility**: All existing code continues to work without changes

## [0.2.2] - 2025-01-06

### Added
- New comprehensive SDK helper functions documentation (`docs/sdk-functions.md`)
- Enhanced events management with filtering, search, and export capabilities (`list_events`, `search_events`, `export_events`)
- Added `list_threshold_events()` function for managing active threshold events
- Network resilience in tests with retry logic and extended timeout handling (30s)
- New `@pytest.mark.network` test marker for network-dependent tests

### Changed
- **BREAKING**: Restructured SDK helper functions to accurately match LLMCosts API endpoints
- Enhanced `events.py` with rich filtering, search, and export functionality matching OpenAPI spec
- Improved test reliability with extended timeouts for network calls
- Updated main README with link to new SDK functions reference guide

### Removed
- **BREAKING**: Removed `limits.py` module (functionality consolidated into `thresholds.py`)
- **BREAKING**: Removed `customers.py` module (endpoints don't exist in actual API)
- **BREAKING**: Removed `alerts.py` module (functionality handled by thresholds with `type='alert'`)

### Fixed
- Network timeout issues in OpenAI Responses API tests
- Test flakiness due to TLS handshake timeouts in network-dependent tests
- Import errors and module dependencies after SDK restructuring
- Legacy CRUD operations in events now properly raise `NotImplementedError` with helpful messages

### Migration Guide
- **Import Changes**: Remove imports for `limits`, `customers`, and `alerts` modules
- **Events API**: Use new filtering capabilities in `list_events()` instead of basic CRUD operations
- **Thresholds**: Use `list_threshold_events()` for active events, existing threshold functions unchanged
- **Testing**: Network-dependent tests now more resilient with automatic retry logic

## [0.2.1] - 2024-01-15

### Changed
- Updated GitHub organization from `keytonweissinger/llmcosts` to `llmcosts/llmcosts-python`
- Updated maintainer email to `keyton@llmcosts.com`
- Updated all project URLs and documentation links

### Fixed
- Added quotes to all pip install commands for zsh shell compatibility (e.g., `pip install "llmcosts[openai]"`)
- Fixed installation instructions to prevent "no matches found" errors in zsh

## [0.2.0] - 2024-01-15

### Changed
- **BREAKING**: Restructured dependencies to reduce installation footprint
- Core dependencies now only include: `requests`, `PyJWT`, `cryptography`, `environs`
- Provider-specific dependencies moved to optional extras:
  - `pip install "llmcosts[openai]"` for OpenAI support
  - `pip install "llmcosts[anthropic]"` for Anthropic support
  - `pip install "llmcosts[google]"` for Google Gemini support
  - `pip install "llmcosts[bedrock]"` for AWS Bedrock support
  - `pip install "llmcosts[langchain]"` for LangChain integration
  - `pip install "llmcosts[all]"` for all providers

### Migration Guide
- **Before**: `pip install llmcosts` installed all provider dependencies
- **After**: Install only what you need (use quotes for zsh compatibility):
  - `pip install "llmcosts[openai]"` for OpenAI support
  - `pip install "llmcosts[anthropic]"` for Anthropic support
  - `pip install "llmcosts[google]"` for Google Gemini support
  - `pip install "llmcosts[bedrock]"` for AWS Bedrock support
  - `pip install "llmcosts[langchain]"` for LangChain integration
  - `pip install "llmcosts[all]"` for all providers (like before)
- **Impact**: Significantly reduced installation size for users who only need specific providers

## [0.1.2] - 2024-01-15

### Fixed
- Improved PyPI package deployment and dependency resolution
- Fixed version management for TestPyPI compatibility
- Enhanced build process and distribution artifacts

### Changed
- Updated packaging configuration for better PyPI compatibility
- Improved documentation for installation and testing

## [0.1.1] - 2024-01-15

### Added
- Enhanced TestPyPI testing capabilities
- Improved package building and distribution

## [0.1.0] - 2024-01-15

### Added
- Initial release of LLMCosts Python SDK
- Universal LLM provider support (OpenAI, Anthropic, Google Gemini, AWS Bedrock, DeepSeek, Grok/xAI)
- Automatic usage tracking with structured JSON output
- LLMTrackingProxy for seamless integration with existing LLM clients
- Built-in response callbacks (SQLite, text file)
- Custom context tracking for user/session data
- LangChain integration with automatic compatibility mode
- Comprehensive test suite with provider-specific tests
- Debug mode for development and testing
- Thread-safe global tracker management
- Resilient background delivery with retry logic
- Dynamic configuration with property setters
- Customer key support for multi-tenant applications
- Streaming support for all compatible providers
- Type hints with py.typed marker file
- Extensive documentation with usage examples

### Features
- **Universal Compatibility**: Works with all major LLM providers
- **Zero Code Changes**: Drop-in replacement for existing LLM clients
- **Automatic Usage Tracking**: Captures tokens, costs, model info, and timestamps
- **Dynamic Configuration**: Change settings on-the-fly without restarting
- **Smart Delivery**: Resilient background delivery with retry logic
- **Custom Context**: Add user/session tracking data to every request
- **Response Callbacks**: Built-in SQLite/text file callbacks plus custom handlers
- **Debug Mode**: Synchronous operation for testing and debugging
- **Structured Output**: Clean JSON format for easy parsing
- **Auto-Recovery**: Automatically restarts failed delivery threads
- **Non-Intrusive**: Original API responses remain completely unchanged

### Supported Providers
- OpenAI (GPT-4, GPT-3.5, etc.)
- Anthropic (Claude-3, Claude-2, etc.)
- Google Gemini (Gemini Pro, etc.)
- AWS Bedrock (Claude, Titan, etc.)
- DeepSeek (DeepSeek models)
- Grok/xAI (Grok models)
- LangChain (via OpenAI integration)

### Technical Details
- Python 3.9+ support
- Type hints with mypy compatibility
- Thread-safe implementation
- Comprehensive test coverage
- Apache 2.0 license
- Built with modern Python packaging (pyproject.toml)

[0.2.3]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.2.3
[0.2.2]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.2.2
[0.2.1]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.2.1
[0.2.0]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.2.0
[0.1.2]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.1.2
[0.1.1]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.1.1
[0.1.0]: https://github.com/llmcosts/llmcosts-python/releases/tag/v0.1.0 