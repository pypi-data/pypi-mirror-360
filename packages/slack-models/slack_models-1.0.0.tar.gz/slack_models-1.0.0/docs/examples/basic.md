# Basic Usage Examples

This guide provides practical examples of using slack-models in common scenarios.

## Simple Event Parsing

### Basic Message Event

```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

# Example webhook payload from Slack
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

# Parse the event
event = parse_event(webhook_payload)

# Type-safe handling
if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        message = event.event
        print(f"Message: {message.text}")
        print(f"Channel: {message.channel}")
        print(f"User: {message.user}")
        print(f"Timestamp: {message.ts}")
```

### URL Verification

```python
from slack_models import parse_event, SlackUrlVerification

# URL verification challenge from Slack
verification_payload = {
    "type": "url_verification",
    "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"
}

event = parse_event(verification_payload)

if isinstance(event, SlackUrlVerification):
    # Return the challenge for verification
    challenge_response = event.challenge
    print(f"Challenge: {challenge_response}")
```

## Working with Core Models

### User Information

```python
from slack_models import User, UserProfile

# Create a user with profile information
user_data = {
    "id": "U1234567890",
    "name": "john.doe",
    "real_name": "John Doe",
    "profile": {
        "email": "john.doe@example.com",
        "display_name": "John",
        "first_name": "John",
        "last_name": "Doe",
        "title": "Software Engineer",
        "phone": "+1-555-123-4567",
        "status_text": "Working remotely",
        "status_emoji": ":house_with_garden:",
        "image_72": "https://avatars.slack-edge.com/2023-01-01/72x72.jpg"
    },
    "is_admin": False,
    "is_owner": False,
    "is_bot": False,
    "updated": 1234567890
}

user = User(**user_data)

# Access user information
print(f"User: {user.name} ({user.real_name})")
print(f"Email: {user.profile.email}")
print(f"Title: {user.profile.title}")
print(f"Status: {user.profile.status_text} {user.profile.status_emoji}")
print(f"Is admin: {user.is_admin}")
```

### Channel Information

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
    "is_member": True,
    "is_archived": False,
    "topic": {
        "value": "General discussion",
        "creator": "U1234567890",
        "last_set": 1234567890
    },
    "purpose": {
        "value": "Company-wide announcements and general chat",
        "creator": "U1234567890",
        "last_set": 1234567890
    },
    "members": ["U1234567890", "U0987654321"],
    "unread_count": 5,
    "unread_count_display": 5
}

channel = Channel(**channel_data)

# Access channel information
print(f"Channel: #{channel.name}")
print(f"Created: {channel.created}")
print(f"Is member: {channel.is_member}")
print(f"Unread count: {channel.unread_count}")
print(f"Members: {len(channel.members) if channel.members else 0}")
```

## Event Type Handling

### Message Events with Subtype

```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

# Message with subtype (bot message)
bot_message_payload = {
    "type": "event_callback",
    "event": {
        "type": "message",
        "subtype": "bot_message",
        "channel": "C1234567890",
        "bot_id": "B1234567890",
        "username": "testbot",
        "text": "This is a bot message",
        "ts": "1234567890.123456"
    },
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}

event = parse_event(bot_message_payload)

if isinstance(event, SlackEventCallback):
    if isinstance(event.event, MessageEvent):
        message = event.event
        print(f"Message: {message.text}")
        print(f"Subtype: {message.subtype}")
        print(f"Bot ID: {message.bot_id}")
        print(f"Username: {message.username}")
```

### Reaction Events

```python
from slack_models import parse_event, SlackEventCallback, ReactionAddedEvent

# Reaction added event
reaction_payload = {
    "type": "event_callback",
    "event": {
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
    },
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}

event = parse_event(reaction_payload)

if isinstance(event, SlackEventCallback):
    if isinstance(event.event, ReactionAddedEvent):
        reaction = event.event
        print(f"Reaction: {reaction.reaction}")
        print(f"User: {reaction.user}")
        print(f"Item type: {reaction.item.type}")
        print(f"Channel: {reaction.item.channel}")
        print(f"Message timestamp: {reaction.item.ts}")
```

## Error Handling

### Validation Errors

```python
from pydantic import ValidationError
from slack_models import parse_event

# Invalid payload (missing required fields)
invalid_payload = {
    "type": "event_callback",
    "event": {
        "type": "message",
        # Missing required fields like channel, user, ts
        "text": "Hello"
    }
}

try:
    event = parse_event(invalid_payload)
    print("Event parsed successfully")
except ValidationError as e:
    print("Validation errors:")
    for error in e.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        print(f"  {field}: {message}")
```

### Safe Parsing

```python
from slack_models import parse_event

def safe_parse_event(payload: dict):
    """Safely parse an event with error handling."""
    try:
        return parse_event(payload)
    except Exception as e:
        print(f"Failed to parse event: {e}")
        return None

# Usage
event = safe_parse_event(webhook_payload)
if event:
    print(f"Successfully parsed: {type(event).__name__}")
else:
    print("Failed to parse event")
```

## Working with Files

### File Events

```python
from slack_models import parse_event, SlackEventCallback, FileCreatedEvent

# File created event
file_payload = {
    "type": "event_callback",
    "event": {
        "type": "file_created",
        "file": {
            "id": "F1234567890",
            "name": "example.txt",
            "title": "Example File",
            "mimetype": "text/plain",
            "filetype": "text",
            "pretty_type": "Plain Text",
            "user": "U1234567890",
            "size": 1024,
            "mode": "snippet",
            "is_external": False,
            "external_type": "",
            "is_public": True,
            "public_url_shared": False,
            "display_as_bot": False,
            "username": "",
            "url_private": "https://files.slack.com/files-pri/T1234567890-F1234567890/example.txt",
            "url_private_download": "https://files.slack.com/files-pri/T1234567890-F1234567890/download/example.txt",
            "permalink": "https://example.slack.com/files/U1234567890/F1234567890/example.txt",
            "permalink_public": "https://slack-files.com/T1234567890-F1234567890-abc123",
            "created": 1234567890,
            "timestamp": 1234567890
        }
    },
    "team_id": "T1234567890",
    "api_app_id": "A1234567890"
}

event = parse_event(file_payload)

if isinstance(event, SlackEventCallback):
    if isinstance(event.event, FileCreatedEvent):
        file_event = event.event
        file_info = file_event.file
        print(f"File created: {file_info.name}")
        print(f"Type: {file_info.pretty_type}")
        print(f"Size: {file_info.size} bytes")
        print(f"User: {file_info.user}")
        print(f"Public: {file_info.is_public}")
```

## Type Checking Examples

### Runtime Type Checking

```python
from slack_models import (
    parse_event, SlackEventCallback, SlackUrlVerification,
    MessageEvent, ReactionAddedEvent
)

def handle_webhook(payload: dict):
    """Handle webhook with comprehensive type checking."""
    event = parse_event(payload)

    # Check webhook type
    if isinstance(event, SlackEventCallback):
        # Check event type
        if isinstance(event.event, MessageEvent):
            handle_message_event(event.event)
        elif isinstance(event.event, ReactionAddedEvent):
            handle_reaction_event(event.event)
        else:
            print(f"Unhandled event type: {type(event.event).__name__}")

    elif isinstance(event, SlackUrlVerification):
        return event.challenge

    else:
        print(f"Unhandled webhook type: {type(event).__name__}")

def handle_message_event(message: MessageEvent):
    """Handle message event with type safety."""
    print(f"Message: {message.text}")
    print(f"Channel: {message.channel}")

def handle_reaction_event(reaction: ReactionAddedEvent):
    """Handle reaction event with type safety."""
    print(f"Reaction: {reaction.reaction}")
    print(f"User: {reaction.user}")
```

### Generic Event Handler

```python
from typing import TypeVar, Type
from slack_models import BaseSlackEvent, SlackEventCallback

T = TypeVar('T', bound=BaseSlackEvent)

def handle_event_type(event: SlackEventCallback, event_type: Type[T]) -> T | None:
    """Generic event handler with type checking."""
    if isinstance(event.event, event_type):
        return event.event
    return None

# Usage
event = parse_event(webhook_payload)
if isinstance(event, SlackEventCallback):
    message = handle_event_type(event, MessageEvent)
    if message:
        print(f"Message: {message.text}")
```
