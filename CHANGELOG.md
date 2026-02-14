# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-02-14

### Added

#### Major Refactor & Modernization
- **True Async I/O**: Migrated from `requests` to `httpx.AsyncClient` for non-blocking HTTP operations
- **Comprehensive Test Suite**: Added 34 automated tests with HTTP mocking (no live API dependency)
  - Contract tests ensuring API stability
  - Integration tests for all tools
  - Visualization tool tests
- **CI/CD Pipeline**: GitHub Actions workflow for automated testing across Python 3.10, 3.11, 3.12
- **Package Structure**: Reorganized into proper Python package (`datagov_mcp/`)
  - Backward-compatible entrypoint (`server.py`) maintained

#### New Visualization Tools
- **`dataset_profile`**: Profile datasets to understand structure and data quality
  - Automatic schema inference
  - Missing value detection
  - Basic statistics (min, max, mean for numeric fields)
  - Top values for categorical fields
- **`chart_generator`**: Generate Vega-Lite chart specifications
  - Support for histogram, bar, line, and scatter charts
  - Returns both JSON spec and self-contained HTML
- **`map_generator`**: Create interactive maps from geographic data
  - Automatic GeoJSON conversion
  - Leaflet-based HTML maps
  - Support for lat/lon coordinate fields

#### Infrastructure Improvements
- Centralized CKAN API helper with:
  - Consistent error handling
  - Automatic retry logic for transient failures (5xx errors)
  - Configurable timeouts
  - User-Agent headers
- HTTP client lifecycle management
- Comprehensive error messages and logging

#### Developer Experience
- Added `ruff` for linting and formatting
- Development dependencies properly organized in `pyproject.toml`
- Modular code structure for easier maintenance

### Changed
- **Dependencies**: Updated from FastMCP 2.8.1 to 2.14.x
- **All tools now properly async**: No more blocking calls in `async def` functions
- **`fetch_data` tool**: Now fully async with better error handling
- Version bumped from 0.2.0 to 0.3.0

### Fixed
- Blocking HTTP calls in async functions
- Missing error handling in several tools
- Inconsistent API response handling

## [0.2.0] - Previous Release

### Added
- Initial MCP server implementation
- Basic CKAN API tools:
  - `status_show`
  - `license_list`
  - `package_list`
  - `package_search`
  - `package_show`
  - `organization_list`
  - `organization_show`
  - `resource_search`
  - `datastore_search`
  - `fetch_data`

[0.3.0]: https://github.com/aviveldan/datagov-mcp/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aviveldan/datagov-mcp/releases/tag/v0.2.0
