# slack-models

Comprehensive Pydantic models for working with the Slack API, providing type-safe, validated data structures for Slack API integration.

## Project Overview

**Library Type**: Python package providing Pydantic models for Slack API data structures
**Language**: Python 3.12+
**License**: BSD-3-Clause
**Package Name**: slack-models
**Version**: 1.0.0
**Author**: Gavin M. Roy <gavinr@aweber.com>

## Architecture

### Core Components
- **Private Modules**: `_models.py` (221 statements), `_utils.py` (7 statements)
- **Public API**: All models exported through `__init__.py` with comprehensive `__all__` list
- **Event System**: `EVENT_MAP` dictionary for type-based event model selection
- **Parser Utility**: `parse_event()` function for webhook payload parsing

### Key Models (26 total)
**Event Models**: `MessageEvent`, `AppMentionEvent`, `ReactionAddedEvent`, `ReactionRemovedEvent`, `ChannelCreatedEvent`, `ChannelDeletedEvent`, `ChannelRenameEvent`, `TeamJoinEvent`, `FileCreatedEvent`, `FileDeletedEvent`

**Core Objects**: `Channel`, `User`, `UserProfile`, `EnterpriseUser`, `File`, `FileContent`, `Authorization`, `ChatMessage`

**Webhook Models**: `SlackEventCallback`, `SlackUrlVerification`, `SlackAppRateLimited`, `SlackWebhookPayload`

**Supporting Models**: `Reaction`, `MessageItem`, `MessageEdited`, `BaseSlackEvent`

**Union Types**: `SlackEvent` (all event types), `SlackWebhookPayload` (all webhook payloads)

### API Compliance
- **Standards Compliant**: Strict adherence to official Slack API specifications
- **Channel Model**: Follows legacy Slack API Channel object exactly (20+ fields)
- **No Custom Fields**: Removed all custom AJ bot fields to maintain API compliance
- **Validated Models**: All models match official Slack object structures

## Dependencies

### Core Dependencies
```toml
requires-python = ">=3.12"
dependencies = ["pydantic>=2.11.3,<3"]
```

### Development Dependencies
- **Build**: `hatchling` (build system)
- **Testing**: `pytest`, `pytest-cov`, `coverage>=7.6.10,<8`
- **Code Quality**: `ruff>=0.9.5,<0.12.0`, `mypy`, `pre-commit>=4.1.0,<5`
- **Documentation**: `mkdocs>=1.5,<2`, `mkdocs-material>9.5,<10`, `mkdocstrings[python]>=0.26,<0.27`

## Development Workflow

### Setup Commands
```bash
# Clone and setup environment
git clone https://github.com/gmr/slack-models.git
cd slack-models
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e '.[dev]'

# Install pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run full test suite (140 tests, 99% coverage)
pytest

# Run with coverage report
pytest --cov=slack_models --cov-report=html

# Current status: 140 tests, 0.19s execution time, 99% coverage
# Missing coverage: lines 44-46 in __init__.py (version fallback)
```

### Code Quality
```bash
# Run linting
ruff check .

# Run formatting
ruff format .

# Run type checking
mypy src/slack_models

# Run pre-commit hooks
pre-commit run --all-files
```

### Documentation
```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Documentation structure:
# - index.md, installation.md, quickstart.md
# - examples/basic.md, examples/events.md
# - api/models.md, api/utils.md
# - development/contributing.md, development/testing.md, development/changelog.md
```

### Building and Publishing
```bash
# Build wheel
python -m build

# Build artifacts: build/ and dist/ directories
```

## Configuration

### Project Configuration (`pyproject.toml`)
- **Build System**: `hatchling` with src-layout packaging
- **Version Management**: Direct version string in `project.version`
- **Line Length**: 79 characters (ruff configuration)
- **Quote Style**: Single quotes
- **Coverage Minimum**: 90% (currently 99%)

### Ruff Configuration
```toml
line-length = 79
target-version = "py312"
select = ["ANN", "ASYNC", "B", "BLE", "C4", "DTZ", "E", "W", "F", "G", "I", "S", "T20", "UP", "F401", "F841", "B027", "B905"]
ignore = ["ANN401", "RSE"]
```

## Usage Patterns

### Basic Event Parsing
```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

# Parse webhook payload
event = parse_event(webhook_data)
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        print(f"Message: {event.event.text}")
```

### Direct Model Usage
```python
from slack_models import Channel, User, MessageEvent

# Create validated models
channel = Channel(id="C1234567890", name="general")
user = User(id="U1234567890", name="john.doe")
```

### Event Type Mapping
```python
from slack_models import EVENT_MAP

# Access event type mappings
model_class = EVENT_MAP.get('message')  # Returns MessageEvent
```

## Testing Strategy

### Test Organization (6 modules)
- **test_data.py**: Test fixtures and data constants
- **test_events.py**: Event model validation tests
- **test_imports.py**: Import system and module structure tests
- **test_models.py**: Core model validation tests
- **test_unions_and_utils.py**: Union types and utility function tests
- **test_webhooks.py**: Webhook payload model tests

### Coverage Details
- **Total Coverage**: 99% (236 statements, 2 missed)
- **_models.py**: 100% coverage (221 statements)
- **_utils.py**: 100% coverage (7 statements)
- **__init__.py**: 75% coverage (version fallback not tested)

### Test Execution
- **Performance**: 140 tests in 0.19 seconds
- **Framework**: pytest with unittest.TestCase patterns
- **Validation**: Comprehensive model validation and edge case testing

## Common Development Tasks

### Adding New Models
1. Add model class to `src/slack_models/_models.py`
2. Add model to `EVENT_MAP` if it's an event type
3. Export model in `src/slack_models/__init__.py` `__all__` list
4. Add comprehensive tests in appropriate test module
5. Update documentation in `docs/api/models.md`

### Updating Documentation
1. Modify relevant `.md` files in `docs/` directory
2. Run `mkdocs serve` to preview changes
3. Build with `mkdocs build` to generate static site

### Running Pre-commit
```bash
# Always run after any changes
pre-commit run --all-files

# Hooks include:
# - ruff format (code formatting)
# - ruff check (linting)
# - check-toml, check-yaml (configuration validation)
# - debug-statements (prevent debug code)
# - end-of-file-fixer, trailing-whitespace (file formatting)
```

## Architecture Decisions

### Private Module Pattern
- Models in `_models.py` to encourage import from package root
- Utilities in `_utils.py` for internal helper functions
- All public API through `__init__.py` with explicit `__all__` exports

### Type Safety
- Python 3.12+ union syntax (`|` operator) throughout
- Comprehensive type annotations with `py.typed` marker
- Pydantic 2.x for runtime validation and IDE support

### API Compliance
- Strict adherence to official Slack API specifications
- Removed all custom fields to maintain compatibility
- Official Slack API documentation referenced in model docstrings

### Event Mapping System
- `EVENT_MAP` dictionary for efficient event type resolution
- Union types (`SlackEvent`, `SlackWebhookPayload`) for type safety
- `parse_event()` utility for convenient webhook parsing

## Build and Deployment

### Package Structure
```
slack-models/
├── src/slack_models/          # Source code
│   ├── __init__.py           # Public API exports
│   ├── _models.py            # Pydantic model definitions
│   ├── _utils.py             # Utility functions
│   └── py.typed              # Type annotations marker
├── tests/                    # Test suite (6 modules)
├── docs/                     # MkDocs documentation
├── pyproject.toml           # Project configuration
└── mkdocs.yml               # Documentation configuration
```

### GitHub Integration
- **Repository**: https://github.com/gmr/slack-models
- **Documentation**: https://gmr.github.io/slack-models/
- **Issues**: https://github.com/gmr/slack-models/issues

## Performance Characteristics

- **Import Time**: Fast due to minimal dependencies
- **Validation Performance**: Pydantic 2.x optimized validation
- **Test Execution**: 140 tests in 0.19 seconds
- **Memory Usage**: Minimal runtime overhead
- **Type Checking**: mypy support for static analysis

## Future Considerations

- **Version Strategy**: Semantic versioning with backward compatibility
- **API Updates**: Track Slack API changes for model updates
- **Performance**: Monitor validation performance as models grow
- **Documentation**: Keep API documentation in sync with Slack API changes
