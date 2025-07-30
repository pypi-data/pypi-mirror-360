# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of slack-models library
- Comprehensive Pydantic models for Slack API objects
- Support for all major Slack event types:
  - Message events (including subtypes and threaded messages)
  - Reaction events (added and removed)
  - Channel events (created, deleted, renamed)
  - Team events (member join)
  - File events (created and deleted)
  - App mention events
- Webhook payload models:
  - Event callbacks
  - URL verification
  - App rate limiting
- Core Slack object models:
  - User and UserProfile
  - Channel following official Slack API specification
  - File and FileContent
  - EnterpriseUser
  - Authorization
  - ChatMessage
- Utility functions:
  - `parse_event()` for parsing webhook payloads
  - `EVENT_MAP` for event type mapping
- Union types for type-safe event handling:
  - `SlackEvent` union of all event types
  - `SlackWebhookPayload` union of all webhook payload types
- Python 3.12+ support with modern type hints
- Comprehensive type annotations with `py.typed` marker
- Pydantic 2.x compatibility
- Comprehensive MkDocs documentation with Material theme
- API reference documentation with mkdocstrings
- Usage examples for basic operations and event handling
- Development guide with contributing guidelines and testing documentation

### Technical Details
- Built on Pydantic 2.11.3+ for robust data validation
- Uses Python 3.10+ union syntax (`|` operator)
- Comprehensive docstrings with Slack API references
- Source layout packaging structure
- Hatchling build system
- Pre-commit hooks with ruff formatting and linting
- MyPy type checking support
- BSD-3-Clause license

### Development Infrastructure
- GitHub Actions CI/CD pipeline
- Automated testing with pytest (140 tests with 99% coverage)
- Code coverage reporting
- Documentation generation with MkDocs
- Pre-commit hooks for code quality
- Ruff linting and formatting
- MyPy static type checking

### API Compliance
- Strict adherence to official Slack API specifications
- All models match official Slack object structures
- Comprehensive validation and type safety
- EVENT_MAP dictionary for efficient event type resolution

### Documentation
- Comprehensive API documentation
- Usage examples and best practices
- Development and contribution guidelines
- Testing documentation and examples

## Development History

The slack-models library was developed internally at AWeber to support Slack bot projects. Key development milestones included:

- **Initial Design**: Core model architecture based on Slack API documentation
- **Pydantic Integration**: Implementation using Pydantic 2.x for enhanced validation
- **Type Safety**: Implementation of comprehensive type annotations
- **Testing Framework**: Development of extensive test coverage
- **Documentation**: Creation of comprehensive documentation system
- **CI/CD Pipeline**: Implementation of automated testing and deployment

### Future Compatibility
- The library follows semantic versioning
- Minor version updates will add new features without breaking changes
- Major version updates may include breaking changes with migration guides
- Deprecated features will be marked and supported for at least one major version

### Acknowledgments

This library was developed to support Slack bot projects at AWeber. Special thanks to:

- The Slack API team for comprehensive documentation
- The Pydantic team for the excellent validation framework
- The Python community for typing and tooling improvements

### Support

For questions, issues, or contributions:
- **GitHub Issues**: [https://github.com/gmr/slack-models/issues](https://github.com/gmr/slack-models/issues)
- **Documentation**: [https://gmr.github.io/slack-models/](https://gmr.github.io/slack-models/)
- **Source Code**: [https://github.com/gmr/slack-models](https://github.com/gmr/slack-models)
