# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-04-30

### Added
- New search API functionality with methods:
  - `create_search_request`: Create search requests with customizable options
  - `monitor_search_request`: Monitor the progress of search operations
  - `get_search_request`: Retrieve details of a search request
  - `stop_search_request`: Cancel an ongoing search operation
- Comprehensive test suite for all search-related API methods
- Enhanced error handling and retry mechanisms for more reliable API interactions
- Better diagnostic capabilities for API errors
- Updated documentation with complete examples of all API methods

### Changed
- Improved test suite with better error handling, diagnostic information, and retry logic
- Enhanced documentation with comprehensive examples in README

### Deprecated
- None

### Removed
- None

### Fixed
- Fixed sitemap-related tests to handle actual API responses correctly

### Security
- None

## [0.6.1] - 2025-04-20

### Added
- Added support for specifying `page_number` and `page_size` parameters to results endpoints for improved pagination and control over result sets.

### Changed
- None

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- None

## [0.6.0] - 2025-04-20

### Added
- New methods: `download_sitemap`, `download_sitemap_graph`, and `download_sitemap_markdown` for retrieving various sitemap formats and representations from a crawl request.
- Helper method `__get_crawl_request_for_sitemap` for internal crawl request validation and normalization.
- Unit tests for all new sitemap-related methods and error handling.

### Changed
- None

### Deprecated
- Marked `download_result` as deprecated. A deprecation warning is now shown when this method is used and the docstring has been updated to reflect its deprecation status.

### Removed
- None

### Fixed
- None

### Security
- None

## [0.1.0] - 2024-12-29

### Added
- Initial release of the WaterCrawl Python client
- Basic API client functionality with request handling
- Support for synchronous and asynchronous crawling
- Comprehensive crawling options and configurations
- Built-in request monitoring and result downloading
- Session management and request handling
- MIT License
- Basic documentation

### Changed
- None (initial release)

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- Basic API key authentication
- Secure request handling with HTTPS
