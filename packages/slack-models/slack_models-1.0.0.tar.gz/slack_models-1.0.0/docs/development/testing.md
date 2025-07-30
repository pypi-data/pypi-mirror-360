# Testing Guide

This guide covers testing practices and guidelines for the slack-models library.

## Test Structure

### Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── test_models.py      # Model validation tests
├── test_utils.py       # Utility function tests
├── test_events.py      # Event parsing tests
└── test_data.py        # Test data fixtures
```

### Test Framework

We use pytest for testing with the following key features:

- **Fixtures**: Reusable test data
- **Parametrized Tests**: Multiple test cases from single test function
- **Coverage**: Test coverage reporting
- **Assertions**: Rich assertion information

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestMessageEvent

# Run specific test method
pytest tests/test_models.py::TestMessageEvent::test_basic_creation
```

### Test with Coverage

```bash
# Run tests with coverage
pytest --cov=slack_models

# Generate HTML coverage report
pytest --cov=slack_models --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=slack_models --cov-report=xml
```

### Verbose Output

```bash
# Run with verbose output
pytest -v

# Run with even more verbose output
pytest -vv

# Show print statements
pytest -s
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from pydantic import ValidationError
from slack_models import MessageEvent, parse_event

class TestMessageEvent:
    """Test cases for MessageEvent model."""

    def test_basic_creation(self):
        """Test basic message event creation."""
        event_data = {
            "type": "message",
            "channel": "C1234567890",
            "user": "U1234567890",
            "text": "Hello, world!",
            "ts": "1234567890.123456"
        }

        event = MessageEvent(**event_data)

        assert event.type == "message"
        assert event.channel == "C1234567890"
        assert event.user == "U1234567890"
        assert event.text == "Hello, world!"
        assert event.ts == "1234567890.123456"

    def test_optional_fields(self):
        """Test optional field handling."""
        event_data = {
            "type": "message",
            "channel": "C1234567890",
            "user": "U1234567890",
            "text": "Hello, world!",
            "ts": "1234567890.123456"
        }

        event = MessageEvent(**event_data)

        # Test optional fields have default values
        assert event.subtype is None
        assert event.thread_ts is None
        assert event.edited is None
        assert event.reactions is None

    def test_validation_error(self):
        """Test validation error for missing required fields."""
        event_data = {
            "type": "message",
            # Missing required fields
        }

        with pytest.raises(ValidationError) as exc_info:
            MessageEvent(**event_data)

        # Check specific validation errors
        errors = exc_info.value.errors()
        error_fields = [error["loc"][0] for error in errors]

        assert "channel" in error_fields
        assert "user" in error_fields
        assert "ts" in error_fields
```

### Fixtures

Create reusable test data using fixtures:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_message_event():
    """Sample message event data."""
    return {
        "type": "message",
        "channel": "C1234567890",
        "user": "U1234567890",
        "text": "Hello, world!",
        "ts": "1234567890.123456"
    }

@pytest.fixture
def sample_webhook_payload():
    """Sample webhook payload data."""
    return {
        "type": "event_callback",
        "event": {
            "type": "message",
            "channel": "C1234567890",
            "user": "U1234567890",
            "text": "Hello, world!",
            "ts": "1234567890.123456"
        },
        "team_id": "T1234567890",
        "api_app_id": "A1234567890"
    }

# Usage in tests
def test_message_event_creation(sample_message_event):
    """Test message event creation using fixture."""
    event = MessageEvent(**sample_message_event)
    assert event.text == "Hello, world!"
```

### Parametrized Tests

Test multiple scenarios with parametrized tests:

```python
@pytest.mark.parametrize("event_type,expected_class", [
    ("message", MessageEvent),
    ("app_mention", AppMentionEvent),
    ("reaction_added", ReactionAddedEvent),
    ("reaction_removed", ReactionRemovedEvent),
    ("team_join", TeamJoinEvent),
])
def test_event_type_mapping(event_type, expected_class):
    """Test event type to class mapping."""
    from slack_models import EVENT_MAP

    assert EVENT_MAP[event_type] == expected_class

@pytest.mark.parametrize("invalid_data,expected_error", [
    ({}, "channel"),  # Missing channel
    ({"channel": "C123"}, "user"),  # Missing user
    ({"channel": "C123", "user": "U123"}, "ts"),  # Missing ts
])
def test_validation_errors(invalid_data, expected_error):
    """Test various validation errors."""
    invalid_data["type"] = "message"

    with pytest.raises(ValidationError) as exc_info:
        MessageEvent(**invalid_data)

    error_fields = [error["loc"][0] for error in exc_info.value.errors()]
    assert expected_error in error_fields
```

### Mock Testing

Use mocks for external dependencies:

```python
from unittest.mock import Mock, patch
import pytest

def test_event_processing_with_mock():
    """Test event processing with mocked dependencies."""
    # Mock external service
    with patch('slack_models.some_external_service') as mock_service:
        mock_service.return_value = {"status": "success"}

        # Test code that uses the external service
        result = process_event(sample_event)

        assert result["status"] == "success"
        mock_service.assert_called_once()
```

## Test Data Management

### Creating Test Data

```python
# tests/test_data.py
"""Test data fixtures for slack-models tests."""

# Message Events
SAMPLE_MESSAGE_EVENT = {
    "type": "message",
    "channel": "C1234567890",
    "user": "U1234567890",
    "text": "Hello, world!",
    "ts": "1234567890.123456"
}

SAMPLE_BOT_MESSAGE_EVENT = {
    "type": "message",
    "subtype": "bot_message",
    "channel": "C1234567890",
    "bot_id": "B1234567890",
    "username": "testbot",
    "text": "Bot message",
    "ts": "1234567890.123456"
}

SAMPLE_THREADED_MESSAGE_EVENT = {
    "type": "message",
    "channel": "C1234567890",
    "user": "U1234567890",
    "text": "Reply in thread",
    "ts": "1234567890.123456",
    "thread_ts": "1234567890.123456"
}

# Reaction Events
SAMPLE_REACTION_ADDED_EVENT = {
    "type": "reaction_added",
    "user": "U1234567890",
    "reaction": "thumbsup",
    "item": {
        "type": "message",
        "channel": "C1234567890",
        "ts": "1234567890.123456"
    },
    "item_user": "U0987654321",
    "event_ts": "1234567890.654321"
}

# Webhook Payloads
SAMPLE_EVENT_CALLBACK = {
    "type": "event_callback",
    "event": SAMPLE_MESSAGE_EVENT,
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}

SAMPLE_URL_VERIFICATION = {
    "type": "url_verification",
    "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"
}

# User and Channel Data
SAMPLE_USER = {
    "id": "U1234567890",
    "name": "john.doe",
    "real_name": "John Doe",
    "profile": {
        "email": "john.doe@example.com",
        "display_name": "John",
        "first_name": "John",
        "last_name": "Doe"
    }
}

SAMPLE_CHANNEL = {
    "id": "C1234567890",
    "name": "general",
    "created": 1234567890,
    "creator": "U1234567890",
    "is_channel": True,
    "is_general": True,
    "is_member": True
}
```

### Data Factories

Create data factories for generating test data:

```python
# tests/factories.py
"""Data factories for generating test data."""

from typing import Dict, Any
import time

class EventFactory:
    """Factory for creating event data."""

    @staticmethod
    def message_event(**kwargs) -> Dict[str, Any]:
        """Create message event data."""
        base_data = {
            "type": "message",
            "channel": "C1234567890",
            "user": "U1234567890",
            "text": "Test message",
            "ts": str(time.time())
        }
        base_data.update(kwargs)
        return base_data

    @staticmethod
    def reaction_event(**kwargs) -> Dict[str, Any]:
        """Create reaction event data."""
        base_data = {
            "type": "reaction_added",
            "user": "U1234567890",
            "reaction": "thumbsup",
            "item": {
                "type": "message",
                "channel": "C1234567890",
                "ts": str(time.time())
            },
            "item_user": "U0987654321",
            "event_ts": str(time.time())
        }
        base_data.update(kwargs)
        return base_data

    @staticmethod
    def webhook_payload(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create webhook payload data."""
        return {
            "type": "event_callback",
            "event": event_data,
            "team_id": "T1234567890",
            "api_app_id": "A1234567890"
        }

# Usage in tests
def test_with_factory():
    """Test using data factory."""
    event_data = EventFactory.message_event(text="Custom message")
    event = MessageEvent(**event_data)
    assert event.text == "Custom message"
```

## Testing Strategies

### Model Validation Testing

```python
def test_model_validation_comprehensive():
    """Comprehensive model validation testing."""

    # Test required fields
    with pytest.raises(ValidationError):
        MessageEvent()

    # Test field types
    with pytest.raises(ValidationError):
        MessageEvent(
            type="message",
            channel=123,  # Should be string
            user="U123",
            text="Test",
            ts="123"
        )

    # Test field constraints
    with pytest.raises(ValidationError):
        MessageEvent(
            type="invalid_type",  # Should be "message"
            channel="C123",
            user="U123",
            text="Test",
            ts="123"
        )

    # Test optional fields
    event = MessageEvent(
        type="message",
        channel="C123",
        user="U123",
        text="Test",
        ts="123"
    )

    assert event.subtype is None
    assert event.thread_ts is None
```

### Integration Testing

```python
def test_full_webhook_processing():
    """Test complete webhook processing pipeline."""
    webhook_payload = {
        "type": "event_callback",
        "event": {
            "type": "message",
            "channel": "C1234567890",
            "user": "U1234567890",
            "text": "Hello, world!",
            "ts": "1234567890.123456"
        },
        "team_id": "T1234567890",
        "api_app_id": "A1234567890"
    }

    # Parse event
    event = parse_event(webhook_payload)

    # Verify event structure
    assert isinstance(event, SlackEventCallback)
    assert isinstance(event.event, MessageEvent)
    assert event.team_id == "T1234567890"
    assert event.api_app_id == "A1234567890"

    # Verify message content
    message = event.event
    assert message.text == "Hello, world!"
    assert message.channel == "C1234567890"
    assert message.user == "U1234567890"
```

### Error Handling Testing

```python
def test_error_handling():
    """Test error handling in various scenarios."""

    # Test malformed JSON
    with pytest.raises(ValidationError):
        parse_event({"invalid": "data"})

    # Test missing required fields
    with pytest.raises(ValidationError):
        parse_event({
            "type": "event_callback",
            "event": {
                "type": "message"
                # Missing required fields
            }
        })

    # Test invalid event type
    with pytest.raises(ValidationError):
        parse_event({
            "type": "event_callback",
            "event": {
                "type": "unknown_event_type"
            }
        })
```

## Coverage Guidelines

### Coverage Requirements

- **Minimum Coverage**: 90% overall
- **Statement Coverage**: All statements should be executed
- **Branch Coverage**: All conditional branches should be tested
- **Function Coverage**: All functions should be called

### Checking Coverage

```bash
# Run tests with coverage
pytest --cov=slack_models --cov-report=html

# View coverage report
open htmlcov/index.html

# Show missing lines
pytest --cov=slack_models --cov-report=term-missing
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "*/test_*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e '.[dev]'

    - name: Run tests
      run: |
        pytest --cov=slack_models --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
```

### Test Commands

```bash
# Run all quality checks
make test

# Or manually:
ruff check .
ruff format .
mypy src/slack_models
pytest --cov=slack_models --cov-report=xml
```

## Best Practices

### Test Organization

1. **One Test Class per Model**: Keep tests organized by model
2. **Descriptive Test Names**: Use clear, descriptive test method names
3. **Arrange-Act-Assert**: Follow AAA pattern in test structure
4. **Independent Tests**: Each test should be independent and isolated

### Test Data

1. **Use Fixtures**: Create reusable test data with fixtures
2. **Realistic Data**: Use realistic Slack API data structures
3. **Edge Cases**: Test boundary conditions and edge cases
4. **Error Scenarios**: Test error conditions and validation failures

### Assertions

1. **Specific Assertions**: Use specific assertions for better error messages
2. **Multiple Assertions**: It's okay to have multiple assertions per test
3. **Expected Exceptions**: Use pytest.raises for expected exceptions
4. **Custom Assertions**: Create custom assertion helpers for complex validations

### Performance

1. **Fast Tests**: Keep tests fast and efficient
2. **Minimal Setup**: Only set up what's needed for each test
3. **Parallel Execution**: Use pytest-xdist for parallel test execution
4. **Test Isolation**: Ensure tests don't interfere with each other

By following these testing guidelines, you'll help maintain the quality and reliability of the slack-models library.
