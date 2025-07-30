# Changelog

All notable changes to the Ophelos Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.1] - 2025-01-27

### Fixed
- Fixed ContactDetail.value field to accept both string and dictionary values from API responses

## [1.3.0] - 2025-01-27

### Added
- **ContactDetailsResource**: New resource manager for customer contact information management
  - `create()` - Create new contact details for customers
  - `get()` - Retrieve specific contact details by ID
  - `update()` - Update existing contact details
  - `list()` - List all contact details for a customer with pagination
  - `delete()` - Soft delete contact details (mark as deleted)

### Enhanced
- **Examples**: All debt examples now use `account_number` instead of `reference_code`

## [1.2.0] - 2025-01-27

### Added
- **Comprehensive Error Handling**: Full request/response debugging interface for all error types
  - `TimeoutError` with request context even when no response received
  - `ParseError` with debugging details when response parsing fails
  - `UnexpectedError` wrapping any unexpected exceptions with request context
  - All exceptions now provide unified debugging interface: `request_info`, `response_info`, `response_raw`
- **Enhanced HTTP Client**: Unified error handling
  - Improved timeout detection and proper exception classification

### Enhanced
- **Error Transparency**: Request/response debugging now available for all error scenarios, not just successful requests

## [1.1.0] - 2025-06-29

### Added
- **Request/Response Transparency**: Access complete HTTP details on all model instances
  - `model.request_info`, `model.response_info`, `model.response_raw`
  - Enables debugging, performance monitoring, and audit trails


## [1.0.6] - 2025-06-27

### Added
- **Thread Safety**: HTTPClient is now fully thread-safe using thread-local storage
  - Each thread gets its own `requests.Session` instance
  - Eliminates connection pool corruption and race conditions

## [1.0.5] - 2025-06-26

### Added
- **API Versioning Support**: Added `version` parameter to `OphelosClient` constructor
  - Default version: `"2025-04-01"` for all new client instances
  - Custom version: Pass any version string (e.g., `version="2024-12-01"`)
  - No version: Set `version=None` to omit the `Ophelos-Version` header entirely

### Changed
- **Default Behavior**: New clients now include `Ophelos-Version: 2025-04-01` header by default
- **User-Agent**: Updated to `ophelos-python-sdk/1.0.5`

## [1.0.4] - 2025-06-26

### Fixed
- **Pagination Issue**: Fixed `has_more` always returning `False` in paginated responses
  - Extract pagination from response headers per [Ophelos API specification](https://ophelos-api.readme.io/reference/pagination)
  - Parse Link header for `next`, `prev`, `first` relations with cursor extraction
  - Extract `X-Total-Count` header for total count information
  - Added `pagination` field to `PaginatedResponse` for easy cursor navigation

### Enhanced
- **Development Toolchain**: Added autoflake for code cleanup and improved requirements structure
- **Code Quality**: Applied Black formatting to entire codebase (27 files)
- **Documentation**: Enhanced README.md and USAGE.md with accurate pagination examples

### Added
- **Pagination Examples**: `examples/enhanced_pagination_demo.py` with cursor-based navigation
- **Test Coverage**: Comprehensive pagination tests for Link header parsing and edge cases

### Changed
- **BREAKING CHANGE**: Package renamed from `ophelos` to `ophelos_sdk`
- Import statements now use `from ophelos_sdk import OphelosClient`

## [1.0.3] - 2025-06-24

### Added
- **Access Token Authentication**: Direct access token support alongside OAuth2
- **Model-First API**: `to_api_body()` method with intelligent field management

### Enhanced
- **Model Organization**: Separate files for each model type
- **Error Handling**: Graceful fallback for invalid API responses
- **Code Quality**: Black, isort, mypy, flake8 compliance

### Fixed
- **JSON Serialization**: Date/datetime handling in API bodies
- **Type Safety**: mypy annotation errors
- **Import Organization**: Standardized across 60 files

## [1.0.2] - 2025-06-14

### Added
- **Multi-tenant Support**: `tenant_id` parameter with automatic header injection
- **Thread Safety**: Thread-safe OAuth2 token management
- **Concurrent Examples**: ThreadPoolExecutor usage patterns

### Enhanced
- **Authentication**: Thread-safe token caching
- **Retry Logic**: Jittered retry with 0-1.5s additive jitter
- **Documentation**: Multi-tenant usage patterns

## [1.0.0] - 2025-06-09

### Added
- Initial release with complete Ophelos API coverage
- OAuth2 client credentials authentication
- Type-safe Pydantic models
- Resource managers for all endpoints
- Webhook signature validation
- Built-in pagination support
- Comprehensive documentation

### Security
- HMAC-SHA256 webhook verification
- Secure credential handling
- Automatic token refresh

## [Unreleased]

### Planned
- Async client support
- Enhanced error messages
- CLI tool for API testing
- Performance optimizations
