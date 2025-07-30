# Contributing to slack-models

Thank you for your interest in contributing to slack-models! This guide will help you get started with contributing to the project.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- Basic understanding of Pydantic models
- Familiarity with the Slack API

### Development Setup

1. **Fork and Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/slack-models.git
   cd slack-models
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**

   ```bash
   pip install -e '.[dev]'
   ```

4. **Install Pre-commit Hooks**

   ```bash
   pre-commit install
   ```

5. **Verify Installation**

   ```bash
   # Run tests
   pytest

   # Run linting
   ruff check .

   # Run type checking
   mypy src/slack_models

   # Build documentation
   mkdocs build
   ```

## Development Workflow

### Code Style

The project follows strict code style guidelines:

- **Line Length**: 79 characters maximum
- **Quotes**: Single quotes for strings
- **Type Annotations**: Required for all functions and methods
- **Python Version**: Python 3.12+ features are encouraged

### Linting and Formatting

We use `ruff` for both linting and formatting:

```bash
# Format code
ruff format .

# Check for linting issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### Type Checking

All code must pass mypy type checking:

```bash
mypy src/slack_models
```

### Testing

Tests are written using pytest and should achieve high coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=slack_models --cov-report=html

# Run specific test file
pytest tests/test_models.py
```

## Contributing Guidelines

### Bug Reports

When reporting bugs, please include:

1. **Python Version**: Output of `python --version`
2. **slack-models Version**: Output of `python -c "import slack_models; print(slack_models.version)"`
3. **Error Details**: Complete error message and traceback
4. **Reproduction Steps**: Minimal code example that reproduces the issue
5. **Expected Behavior**: What you expected to happen
6. **Actual Behavior**: What actually happened

### Feature Requests

For new features, please:

1. **Check Existing Issues**: Ensure the feature hasn't been requested
2. **Provide Use Case**: Explain why this feature would be valuable
3. **Propose Implementation**: If possible, suggest how it might be implemented
4. **Consider Backwards Compatibility**: Ensure it doesn't break existing code

### Pull Requests

#### Before Submitting

1. **Create an Issue**: For significant changes, create an issue first
2. **Fork the Repository**: Work on your own fork
3. **Create a Feature Branch**: Use descriptive branch names
4. **Write Tests**: Ensure your changes are well-tested
5. **Update Documentation**: Add or update relevant documentation
6. **Check Style**: Ensure code follows project style guidelines

#### Pull Request Process

1. **Commit Messages**: Write clear, descriptive commit messages
2. **Small Commits**: Make small, focused commits
3. **Test Coverage**: Maintain or improve test coverage
4. **Documentation**: Update documentation as needed
5. **Changelog**: Add entry to changelog if applicable

#### Example Pull Request

```bash
# Create feature branch
git checkout -b feature/add-new-event-type

# Make your changes
# ... edit files ...

# Add tests
# ... add test files ...

# Update documentation
# ... update docs ...

# Commit changes
git add .
git commit -m "Add support for new_event_type

- Add NewEventType model to _models.py
- Update EVENT_MAP with new event type
- Add comprehensive tests for new event type
- Update documentation with usage examples"

# Push branch
git push origin feature/add-new-event-type

# Create pull request on GitHub
```

## Code Organization

### Project Structure

```
slack-models/
├── src/slack_models/          # Main package
│   ├── __init__.py           # Package exports
│   ├── _models.py            # Pydantic models
│   ├── _utils.py             # Utility functions
│   └── py.typed              # Type annotations marker
├── tests/                    # Test files
│   ├── __init__.py
│   ├── test_models.py        # Model tests
│   ├── test_utils.py         # Utility tests
│   └── test_data.py          # Test data
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── examples/             # Usage examples
│   └── development/          # Development guides
├── pyproject.toml            # Project configuration
├── mkdocs.yml               # Documentation config
└── CLAUDE.md                # AI assistant guide
```

### Adding New Models

When adding new Slack event or object models:

1. **Add to `_models.py`**: Define the Pydantic model
2. **Update `__init__.py`**: Add to exports
3. **Update `EVENT_MAP`**: If it's an event type
4. **Add Tests**: Comprehensive test coverage
5. **Update Documentation**: Add to API docs and examples

#### Example: Adding a New Event Type

```python
# In _models.py
class NewEventType(BaseSlackEvent):
    """Documentation for the new event type.

    Include purpose, required OAuth scopes, and key characteristics.
    """

    type: typing.Literal["new_event_type"]
    user: str
    timestamp: str
    # ... other fields

# In EVENT_MAP
EVENT_MAP = {
    # ... existing events
    "new_event_type": NewEventType,
}

# In __init__.py
__all__ = [
    # ... existing exports
    "NewEventType",
]
```

### Documentation Guidelines

#### Docstrings

All models and functions must have comprehensive docstrings:

```python
class ExampleModel(pydantic.BaseModel):
    """Brief description of the model.

    Longer description including:
    - Purpose and use cases
    - Required OAuth scopes (if applicable)
    - Key characteristics
    - Relationship to other models

    Example:
        ```python
        model = ExampleModel(
            field1="value1",
            field2="value2"
        )
        ```
    """

    field1: str
    field2: str | None = None
```

#### API Documentation

- Use mkdocstrings for auto-generated API docs
- Include usage examples in docstrings
- Link to official Slack API documentation
- Provide type annotations for all parameters

#### Examples

- Create practical, real-world examples
- Include error handling
- Show best practices
- Cover common use cases

## Testing Guidelines

### Test Structure

```python
import pytest
from slack_models import ModelName

class TestModelName:
    """Test cases for ModelName."""

    def test_basic_creation(self):
        """Test basic model creation."""
        model = ModelName(field1="value1")
        assert model.field1 == "value1"

    def test_validation_error(self):
        """Test validation error handling."""
        with pytest.raises(ValidationError):
            ModelName(invalid_field="invalid")

    def test_optional_fields(self):
        """Test optional field handling."""
        model = ModelName(field1="value1")
        assert model.field2 is None
```

### Test Data

Create reusable test data:

```python
# tests/test_data.py
SAMPLE_MESSAGE_EVENT = {
    "type": "message",
    "channel": "C1234567890",
    "user": "U1234567890",
    "text": "Hello, world!",
    "ts": "1234567890.123456"
}

SAMPLE_WEBHOOK_PAYLOAD = {
    "type": "event_callback",
    "event": SAMPLE_MESSAGE_EVENT,
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}
```

### Coverage Requirements

- Maintain minimum 90% test coverage
- Test all validation branches
- Test error conditions
- Test edge cases and boundary conditions

## Release Process

### Version Management

- Version is stored in `pyproject.toml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version for releases

### Changelog

Maintain a changelog in `docs/development/changelog.md`:

```markdown
## [1.1.0] - 2024-01-15

### Added
- New event type support
- Additional utility functions

### Changed
- Updated documentation structure

### Fixed
- Validation error in Channel model

### Deprecated
- Old utility function (will be removed in 2.0.0)
```

### Release Checklist

1. **Update Version**: Increment version in `pyproject.toml`
2. **Update Changelog**: Add release notes
3. **Run Tests**: Ensure all tests pass
4. **Build Documentation**: Update and build docs
5. **Create Release**: Tag and create GitHub release
6. **Publish Package**: Upload to PyPI

## Getting Help

### Community Resources

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Comprehensive guides and examples

### Communication Guidelines

- Be respectful and constructive
- Provide detailed information
- Search existing issues before creating new ones
- Follow up on your contributions

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Please read and follow it in all interactions.

## Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes
- Documentation credits

Thank you for contributing to slack-models! Your contributions help make Slack API integration easier for everyone.
