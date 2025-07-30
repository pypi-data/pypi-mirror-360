# Changelog

All notable changes to the StockAlert Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-01-07

### Added
- CLI tool for command-line usage (`stockalert` command)
- GitHub issue and PR templates
- Contributing guidelines
- Code of Conduct
- Pre-commit hooks for code quality
- Support for all alert operations via CLI

### Features
- List, create, get, update, and delete alerts from command line
- JSON output format for scripting
- Environment variable support for API key
- Interactive confirmations for destructive operations

## [1.1.1] - 2024-01-07

### Added
- CHANGELOG.md to track version history
- Enhanced README with more examples
- py.typed for PEP 561 compliance
- Logging module with configurable levels
- More tests (coverage increased to 46.71%)

- Comprehensive test suite

### Features
- Create, read, update, and delete alerts
- List alerts with filtering and pagination
- Webhook management
- API key management (coming soon)
- Support for all notification channels (email, SMS)

[1.1.0]: https://github.com/stockalert-pro/python-sdk/releases/tag/v1.1.0
