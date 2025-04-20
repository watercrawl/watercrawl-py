# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
