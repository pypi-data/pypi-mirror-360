# slack-models

Welcome to slack-models, a comprehensive Python library providing type-safe Pydantic models for working with the Slack API. This library offers structured data models for Slack events, webhooks, users, channels, files, and other API objects.

## Overview

slack-models is designed to make working with Slack API data easier and more reliable by providing:

- **Type Safety**: Comprehensive Pydantic models with full type annotations
- **Event Processing**: Models for all major Slack event types including messages, reactions, and channel events
- **Webhook Support**: Complete webhook payload models for event callbacks and verifications
- **Data Validation**: Automatic validation and parsing of Slack API responses
- **Modern Python**: Built for Python 3.12+ with modern type hints

## Key Features

### 🎯 Complete Coverage
- **Core Objects**: User, Channel, File, and other fundamental Slack objects
- **Event Models**: Message, reaction, channel, and team events
- **Webhook Models**: Event callbacks, URL verification, and rate limiting
- **Supporting Models**: Reactions, message items, authorizations, and more

### 🔧 Developer Friendly
- **Type Hints**: Full type annotation support with `py.typed`
- **Documentation**: Comprehensive docstrings with Slack API references
- **IDE Support**: Excellent autocomplete and type checking
- **Testing**: Ready for comprehensive test coverage

### 🚀 Modern Architecture
- **Pydantic 2.x**: Built on the latest Pydantic for performance and features
- **Union Types**: Type-safe event handling with discriminated unions
- **Flexible Parsing**: Robust parsing with the `parse_event` utility
- **Standards Compliant**: Strict adherence to official Slack API specifications

## Quick Example

```python
from slack_models import parse_event, MessageEvent, SlackEventCallback

# Parse a webhook payload
webhook_data = {
    "type": "event_callback",
    "event": {
        "type": "message",
        "channel": "C1234567890",
        "user": "U1234567890",
        "text": "Hello, world!",
        "ts": "1234567890.123456"
    }
}

# Parse and validate
event = parse_event(webhook_data)
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        print(f"Message: {event.event.text}")
        print(f"Channel: {event.event.channel}")
```

## Installation

Install slack-models using pip:

```bash
pip install slack-models
```

## Requirements

- Python 3.12+
- pydantic >=2.11.3,<3

## License

This project is licensed under the BSD-3-Clause License. See the [LICENSE](https://github.com/gmr/slack-models/blob/main/LICENSE) file for details.

## Getting Started

Ready to start using slack-models? Check out our [Quick Start](quickstart.md) guide or explore the [API Reference](api/models.md) for detailed model documentation.

## Support

- **Documentation**: [https://gmr.github.io/slack-models/](https://gmr.github.io/slack-models/)
- **Source Code**: [https://github.com/gmr/slack-models](https://github.com/gmr/slack-models)
- **Issues**: [https://github.com/gmr/slack-models/issues](https://github.com/gmr/slack-models/issues)
