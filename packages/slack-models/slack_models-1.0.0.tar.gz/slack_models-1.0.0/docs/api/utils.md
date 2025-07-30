# Utilities API Reference

This page provides documentation for utility functions provided by slack-models.

## Event Parsing

### parse_event

::: slack_models.parse_event
    options:
      show_root_heading: true
      show_source: true

The `parse_event` function is the main utility for parsing Slack webhook payloads into typed Pydantic models.

#### Usage Examples

##### Basic Event Parsing

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
print(f"Parsed event type: {type(event).__name__}")
```

##### URL Verification

```python
from slack_models import parse_event, SlackUrlVerification

# URL verification payload
verification_data = {
    "type": "url_verification",
    "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P"
}

event = parse_event(verification_data)
if isinstance(event, SlackUrlVerification):
    print(f"Challenge: {event.challenge}")
```

##### Rate Limiting

```python
from slack_models import parse_event, SlackAppRateLimited

# Rate limiting payload
rate_limit_data = {
    "type": "app_rate_limited",
    "minute_rate_limited": 1
}

event = parse_event(rate_limit_data)
if isinstance(event, SlackAppRateLimited):
    print(f"Rate limited for {event.minute_rate_limited} minutes")
```

##### Error Handling

```python
from pydantic import ValidationError
from slack_models import parse_event

try:
    event = parse_event(webhook_data)
    # Process the event
except ValidationError as e:
    print(f"Validation error: {e}")
    # Handle invalid data
except KeyError as e:
    print(f"Missing required field: {e}")
```

## Event Mapping

### EVENT_MAP

::: slack_models.EVENT_MAP
    options:
      show_root_heading: true
      show_source: true

The `EVENT_MAP` dictionary maps Slack event type strings to their corresponding Pydantic model classes.

#### Usage Examples

##### Direct Event Type Mapping

```python
from slack_models import EVENT_MAP, MessageEvent

# Get the model class for a specific event type
event_type = "message"
model_class = EVENT_MAP.get(event_type)

if model_class:
    print(f"Event type '{event_type}' maps to {model_class.__name__}")

# Example: MessageEvent
assert EVENT_MAP["message"] == MessageEvent
```

##### Dynamic Event Processing

```python
from slack_models import EVENT_MAP

def process_event_data(event_data: dict):
    """Process event data using EVENT_MAP for dynamic model selection."""
    event_type = event_data.get("type")

    if event_type in EVENT_MAP:
        model_class = EVENT_MAP[event_type]
        try:
            event = model_class(**event_data)
            return event
        except ValidationError as e:
            print(f"Failed to parse {event_type}: {e}")
            return None
    else:
        print(f"Unknown event type: {event_type}")
        return None

# Usage
event_data = {
    "type": "message",
    "channel": "C1234567890",
    "user": "U1234567890",
    "text": "Hello!",
    "ts": "1234567890.123456"
}

event = process_event_data(event_data)
if event:
    print(f"Processed event: {type(event).__name__}")
```

##### Available Event Types

The `EVENT_MAP` contains mappings for the following event types:

```python
EVENT_MAP = {
    "message": MessageEvent,
    "app_mention": AppMentionEvent,
    "reaction_added": ReactionAddedEvent,
    "reaction_removed": ReactionRemovedEvent,
    "team_join": TeamJoinEvent,
    "file_created": FileCreatedEvent,
    "file_deleted": FileDeletedEvent,
    "channel_created": ChannelCreatedEvent,
    "channel_deleted": ChannelDeletedEvent,
    "channel_rename": ChannelRenameEvent,
}
```

## Utility Patterns

### Custom Event Handler

```python
from slack_models import parse_event, EVENT_MAP, SlackEventCallback

class EventHandler:
    def __init__(self):
        self.handlers = {}

    def register(self, event_type: str, handler_func):
        """Register a handler for a specific event type."""
        self.handlers[event_type] = handler_func

    def handle(self, payload: dict):
        """Handle a webhook payload."""
        event = parse_event(payload)

        if isinstance(event, SlackEventCallback):
            event_type = event.event.type
            handler = self.handlers.get(event_type)

            if handler:
                handler(event.event)
            else:
                print(f"No handler registered for event type: {event_type}")

# Usage
handler = EventHandler()
handler.register("message", lambda msg: print(f"Message: {msg.text}"))
handler.handle(webhook_data)
```

### Type-Safe Event Router

```python
from typing import TypeVar, Type, Callable
from slack_models import parse_event, SlackEventCallback, BaseSlackEvent

T = TypeVar('T', bound=BaseSlackEvent)

class TypedEventRouter:
    def __init__(self):
        self.routes = {}

    def route(self, event_class: Type[T]) -> Callable[[Callable[[T], None]], None]:
        """Decorator for registering type-safe event handlers."""
        def decorator(handler_func: Callable[[T], None]):
            self.routes[event_class] = handler_func
            return handler_func
        return decorator

    def handle(self, payload: dict):
        """Handle a webhook payload with type-safe routing."""
        event = parse_event(payload)

        if isinstance(event, SlackEventCallback):
            handler = self.routes.get(type(event.event))
            if handler:
                handler(event.event)

# Usage
router = TypedEventRouter()

@router.route(MessageEvent)
def handle_message(message: MessageEvent):
    print(f"Message: {message.text}")

@router.route(ReactionAddedEvent)
def handle_reaction(reaction: ReactionAddedEvent):
    print(f"Reaction: {reaction.reaction}")

router.handle(webhook_data)
```

## Error Handling Utilities

### Validation Error Helper

```python
from pydantic import ValidationError
from slack_models import parse_event

def safe_parse_event(payload: dict):
    """Safely parse an event with detailed error reporting."""
    try:
        return parse_event(payload)
    except ValidationError as e:
        print("Validation errors:")
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            message = error["msg"]
            print(f"  {field}: {message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
event = safe_parse_event(webhook_data)
if event:
    print("Event parsed successfully")
```
