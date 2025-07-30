# Models API Reference

This page provides comprehensive documentation for all Pydantic models provided by slack-models.

## Core Models

### User Models

::: slack_models.User
    options:
      show_root_heading: true
      show_source: true

::: slack_models.UserProfile
    options:
      show_root_heading: true
      show_source: true

::: slack_models.EnterpriseUser
    options:
      show_root_heading: true
      show_source: true

### Channel Models

::: slack_models.Channel
    options:
      show_root_heading: true
      show_source: true

### File Models

::: slack_models.File
    options:
      show_root_heading: true
      show_source: true

::: slack_models.FileContent
    options:
      show_root_heading: true
      show_source: true

## Event Models

### Message Events

::: slack_models.MessageEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.MessageItem
    options:
      show_root_heading: true
      show_source: true

::: slack_models.MessageEdited
    options:
      show_root_heading: true
      show_source: true

::: slack_models.AppMentionEvent
    options:
      show_root_heading: true
      show_source: true

### Reaction Events

::: slack_models.ReactionAddedEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.ReactionRemovedEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.Reaction
    options:
      show_root_heading: true
      show_source: true

### Channel Events

::: slack_models.ChannelCreatedEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.ChannelDeletedEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.ChannelRenameEvent
    options:
      show_root_heading: true
      show_source: true

### Team Events

::: slack_models.TeamJoinEvent
    options:
      show_root_heading: true
      show_source: true

### File Events

::: slack_models.FileCreatedEvent
    options:
      show_root_heading: true
      show_source: true

::: slack_models.FileDeletedEvent
    options:
      show_root_heading: true
      show_source: true

## Webhook Models

### Event Callbacks

::: slack_models.SlackEventCallback
    options:
      show_root_heading: true
      show_source: true

::: slack_models.BaseSlackEvent
    options:
      show_root_heading: true
      show_source: true

### Verification and Rate Limiting

::: slack_models.SlackUrlVerification
    options:
      show_root_heading: true
      show_source: true

::: slack_models.SlackAppRateLimited
    options:
      show_root_heading: true
      show_source: true

## Supporting Models

### Authorization

::: slack_models.Authorization
    options:
      show_root_heading: true
      show_source: true

### Chat Messages

::: slack_models.ChatMessage
    options:
      show_root_heading: true
      show_source: true

## Union Types

### SlackEvent

A union type representing all possible Slack event types:

```python
SlackEvent = Union[
    MessageEvent,
    AppMentionEvent,
    ReactionAddedEvent,
    ReactionRemovedEvent,
    TeamJoinEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    ChannelCreatedEvent,
    ChannelDeletedEvent,
    ChannelRenameEvent,
]
```

### SlackWebhookPayload

A union type representing all possible webhook payload types:

```python
SlackWebhookPayload = Union[
    SlackEventCallback,
    SlackUrlVerification,
    SlackAppRateLimited,
]
```

## Model Relationships

### Event Hierarchy

```
BaseSlackEvent
├── MessageEvent
├── AppMentionEvent
├── ReactionAddedEvent
├── ReactionRemovedEvent
├── TeamJoinEvent
├── FileCreatedEvent
├── FileDeletedEvent
├── ChannelCreatedEvent
├── ChannelDeletedEvent
└── ChannelRenameEvent
```

### Webhook Payload Structure

```
SlackWebhookPayload
├── SlackEventCallback
│   ├── event: SlackEvent
│   ├── team_id: str
│   └── api_app_id: str
├── SlackUrlVerification
│   ├── challenge: str
│   └── type: Literal["url_verification"]
└── SlackAppRateLimited
    ├── minute_rate_limited: int
    └── type: Literal["app_rate_limited"]
```

## Usage Examples

### Type-Safe Event Handling

```python
from slack_models import parse_event, SlackEventCallback, MessageEvent

def handle_event(payload: dict):
    event = parse_event(payload)

    if isinstance(event, SlackEventCallback):
        if isinstance(event.event, MessageEvent):
            # TypeScript-style type narrowing
            message: MessageEvent = event.event
            print(f"Message: {message.text}")
```

### Working with Union Types

```python
from slack_models import SlackEvent, MessageEvent, ReactionAddedEvent

def process_event(event: SlackEvent):
    if isinstance(event, MessageEvent):
        print(f"Message: {event.text}")
    elif isinstance(event, ReactionAddedEvent):
        print(f"Reaction: {event.reaction}")
```

### Channel Objects

```python
from slack_models import Channel

# Standard Slack channel
channel = Channel(
    id="C1234567890",
    name="general",
    is_channel=True,
    created=1640995200,
    creator="U1234567890",
    is_archived=False,
    is_general=True,
    is_member=True
)

print(f"Channel: #{channel.name}")
print(f"Is general channel: {channel.is_general}")
```
