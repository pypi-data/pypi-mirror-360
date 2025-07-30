# Quick Start

This guide will help you get started with slack-models quickly. We'll cover the basics of using the library to parse Slack events and work with Slack API data.

## Basic Usage

### Importing Models

```python
from slack_models import (
    User, Channel, MessageEvent,
    SlackEventCallback, parse_event
)
```

### Parsing Events

The `parse_event` function is the main entry point for parsing Slack webhook payloads:

```python
from slack_models import parse_event

# Example webhook payload
webhook_data = {
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

# Parse the event
event = parse_event(webhook_data)
print(f"Event type: {type(event).__name__}")
```

### Working with Specific Events

#### Message Events

```python
from slack_models import MessageEvent, SlackEventCallback

# Parse a message event
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        message = event.event
        print(f"Message: {message.text}")
        print(f"Channel: {message.channel}")
        print(f"User: {message.user}")
        print(f"Timestamp: {message.ts}")
```

#### Reaction Events

```python
from slack_models import ReactionAddedEvent, ReactionRemovedEvent

# Handle reaction events
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, ReactionAddedEvent):
        reaction = event.event
        print(f"Reaction added: {reaction.reaction}")
        print(f"User: {reaction.user}")
        print(f"Item: {reaction.item}")

    elif isinstance(event.event, ReactionRemovedEvent):
        reaction = event.event
        print(f"Reaction removed: {reaction.reaction}")
```

#### Channel Events

```python
from slack_models import ChannelCreatedEvent, ChannelDeletedEvent

# Handle channel events
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, ChannelCreatedEvent):
        channel_event = event.event
        print(f"Channel created: {channel_event.channel.name}")

    elif isinstance(event.event, ChannelDeletedEvent):
        channel_event = event.event
        print(f"Channel deleted: {channel_event.channel}")
```

### Working with Core Objects

#### User Objects

```python
from slack_models import User

# Create a user object
user_data = {
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

user = User(**user_data)
print(f"User: {user.name} ({user.real_name})")
print(f"Email: {user.profile.email}")
```

#### Channel Objects

```python
from slack_models import Channel

# Create a channel object
channel_data = {
    "id": "C1234567890",
    "name": "general",
    "created": 1234567890,
    "creator": "U1234567890",
    "is_channel": True,
    "is_general": True,
    "is_member": True
}

channel = Channel(**channel_data)
print(f"Channel: #{channel.name}")
print(f"Created by: {channel.creator}")
print(f"Is member: {channel.is_member}")
```

### Error Handling

slack-models uses Pydantic for validation, so you should handle validation errors:

```python
from pydantic import ValidationError
from slack_models import parse_event

try:
    event = parse_event(webhook_data)
    # Process the event
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle invalid data
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Type Checking

Use type checking to ensure proper handling:

```python
from slack_models import (
    SlackEventCallback, SlackUrlVerification,
    SlackAppRateLimited, MessageEvent
)

event = parse_event(webhook_data)

# Type-safe event handling
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        # TypeScript-style type narrowing
        message: MessageEvent = event.event
        print(f"Message: {message.text}")

elif isinstance(event, SlackUrlVerification):
    # Handle URL verification
    print(f"Challenge: {event.challenge}")

elif isinstance(event, SlackAppRateLimited):
    # Handle rate limiting
    print(f"Rate limited for {event.minute_rate_limited} minutes")
```

## Common Patterns

### Webhook Handler

```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

def handle_webhook(payload: dict):
    """Handle incoming Slack webhook payload."""
    try:
        event = parse_event(payload)

        if isinstance(event, SlackEventCallback):
            if isinstance(event.event, MessageEvent):
                handle_message(event.event)
            # Handle other event types...

    except Exception as e:
        print(f"Error handling webhook: {e}")

def handle_message(message: MessageEvent):
    """Handle a message event."""
    print(f"New message in {message.channel}: {message.text}")
```

### Event Router

```python
from slack_models import (
    parse_event, SlackEventCallback,
    MessageEvent, ReactionAddedEvent, ChannelCreatedEvent
)

def route_event(payload: dict):
    """Route events to appropriate handlers."""
    event = parse_event(payload)

    if isinstance(event, SlackEventCallback):
        event_handlers = {
            MessageEvent: handle_message,
            ReactionAddedEvent: handle_reaction,
            ChannelCreatedEvent: handle_channel_created,
        }

        handler = event_handlers.get(type(event.event))
        if handler:
            handler(event.event)
        else:
            print(f"No handler for event type: {type(event.event)}")
```

## Next Steps

- Explore the [API Reference](api/models.md) for detailed model documentation
- Check out [Examples](examples/basic.md) for more complex usage patterns
- Learn about [Event Handling](examples/events.md) for comprehensive event processing
