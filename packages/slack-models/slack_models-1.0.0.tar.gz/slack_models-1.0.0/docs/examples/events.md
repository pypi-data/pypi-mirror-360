# Event Handling Examples

This guide provides comprehensive examples for handling different types of Slack events using slack-models.

## Event Router Implementation

### Basic Event Router

```python
from slack_models import (
    parse_event, SlackEventCallback, MessageEvent,
    ReactionAddedEvent, ChannelCreatedEvent, TeamJoinEvent
)

class SlackEventRouter:
    def __init__(self):
        self.handlers = {}

    def register(self, event_type, handler):
        """Register a handler for a specific event type."""
        self.handlers[event_type] = handler

    def route(self, payload: dict):
        """Route incoming webhook payload to appropriate handler."""
        try:
            event = parse_event(payload)

            if isinstance(event, SlackEventCallback):
                event_type = type(event.event)
                handler = self.handlers.get(event_type)

                if handler:
                    return handler(event.event)
                else:
                    print(f"No handler for event type: {event_type.__name__}")

        except Exception as e:
            print(f"Error processing event: {e}")
            return None

# Usage
router = SlackEventRouter()
router.register(MessageEvent, handle_message)
router.register(ReactionAddedEvent, handle_reaction)
router.register(ChannelCreatedEvent, handle_channel_created)

# Process webhook
router.route(webhook_payload)
```

### Decorator-Based Event Router

```python
from typing import Dict, Type, Callable
from slack_models import BaseSlackEvent, SlackEventCallback, parse_event

class EventRouter:
    def __init__(self):
        self.handlers: Dict[Type[BaseSlackEvent], Callable] = {}

    def handle(self, event_type: Type[BaseSlackEvent]):
        """Decorator to register event handlers."""
        def decorator(func):
            self.handlers[event_type] = func
            return func
        return decorator

    def process(self, payload: dict):
        """Process webhook payload."""
        event = parse_event(payload)

        if isinstance(event, SlackEventCallback):
            handler = self.handlers.get(type(event.event))
            if handler:
                return handler(event.event)

# Usage
router = EventRouter()

@router.handle(MessageEvent)
def handle_message(message: MessageEvent):
    print(f"Message: {message.text}")

@router.handle(ReactionAddedEvent)
def handle_reaction(reaction: ReactionAddedEvent):
    print(f"Reaction: {reaction.reaction}")

# Process events
router.process(webhook_payload)
```

## Message Event Handling

### Comprehensive Message Handler

```python
from slack_models import MessageEvent, MessageItem

def handle_message_event(message: MessageEvent):
    """Handle message events with various subtypes."""
    print(f"Message from {message.user}: {message.text}")

    # Handle message subtypes
    if message.subtype == "bot_message":
        print(f"Bot message from {message.username}")
    elif message.subtype == "file_share":
        print("File shared in message")
    elif message.subtype == "message_changed":
        print("Message was edited")
    elif message.subtype == "message_deleted":
        print("Message was deleted")

    # Handle threaded messages
    if message.thread_ts:
        print(f"Thread reply to: {message.thread_ts}")

    # Handle edited messages
    if message.edited:
        print(f"Message edited at: {message.edited.ts}")
        print(f"Edited by: {message.edited.user}")

    # Handle file attachments
    if message.files:
        print(f"Message has {len(message.files)} file(s)")
        for file in message.files:
            print(f"  - {file.name} ({file.pretty_type})")

    # Handle message reactions
    if message.reactions:
        print("Message reactions:")
        for reaction in message.reactions:
            print(f"  - {reaction.name}: {reaction.count} users")
```

### Message Filtering

```python
from slack_models import MessageEvent

class MessageFilter:
    def __init__(self):
        self.filters = []

    def add_filter(self, filter_func):
        """Add a filter function."""
        self.filters.append(filter_func)

    def should_process(self, message: MessageEvent) -> bool:
        """Check if message should be processed."""
        return all(f(message) for f in self.filters)

# Filter functions
def not_bot_message(message: MessageEvent) -> bool:
    return message.subtype != "bot_message"

def has_text(message: MessageEvent) -> bool:
    return bool(message.text and message.text.strip())

def not_thread_reply(message: MessageEvent) -> bool:
    return message.thread_ts is None

def from_human_user(message: MessageEvent) -> bool:
    return message.user is not None

# Usage
message_filter = MessageFilter()
message_filter.add_filter(not_bot_message)
message_filter.add_filter(has_text)
message_filter.add_filter(not_thread_reply)
message_filter.add_filter(from_human_user)

def process_message(message: MessageEvent):
    if message_filter.should_process(message):
        print(f"Processing message: {message.text}")
    else:
        print("Message filtered out")
```

## Reaction Event Handling

### Reaction Tracking

```python
from slack_models import ReactionAddedEvent, ReactionRemovedEvent
from collections import defaultdict

class ReactionTracker:
    def __init__(self):
        self.reactions = defaultdict(lambda: defaultdict(set))

    def add_reaction(self, event: ReactionAddedEvent):
        """Track reaction addition."""
        key = (event.item.channel, event.item.ts)
        self.reactions[key][event.reaction].add(event.user)
        print(f"Reaction {event.reaction} added by {event.user}")

    def remove_reaction(self, event: ReactionRemovedEvent):
        """Track reaction removal."""
        key = (event.item.channel, event.item.ts)
        self.reactions[key][event.reaction].discard(event.user)
        print(f"Reaction {event.reaction} removed by {event.user}")

    def get_reactions(self, channel: str, ts: str):
        """Get reactions for a specific message."""
        key = (channel, ts)
        return dict(self.reactions[key])

# Usage
tracker = ReactionTracker()

def handle_reaction_added(reaction: ReactionAddedEvent):
    tracker.add_reaction(reaction)

def handle_reaction_removed(reaction: ReactionRemovedEvent):
    tracker.remove_reaction(reaction)
```

### Popular Reaction Analysis

```python
from slack_models import ReactionAddedEvent
from collections import Counter

class ReactionAnalyzer:
    def __init__(self):
        self.reaction_counts = Counter()
        self.user_reactions = defaultdict(Counter)

    def analyze_reaction(self, event: ReactionAddedEvent):
        """Analyze reaction patterns."""
        # Track overall reaction popularity
        self.reaction_counts[event.reaction] += 1

        # Track user reaction patterns
        self.user_reactions[event.user][event.reaction] += 1

        # Log popular reactions
        if self.reaction_counts[event.reaction] % 10 == 0:
            print(f"Reaction {event.reaction} has been used {self.reaction_counts[event.reaction]} times!")

    def get_popular_reactions(self, limit: int = 10):
        """Get most popular reactions."""
        return self.reaction_counts.most_common(limit)

    def get_user_favorite_reactions(self, user: str, limit: int = 5):
        """Get a user's favorite reactions."""
        return self.user_reactions[user].most_common(limit)

# Usage
analyzer = ReactionAnalyzer()

def handle_reaction_added(reaction: ReactionAddedEvent):
    analyzer.analyze_reaction(reaction)

    # Print popular reactions periodically
    popular = analyzer.get_popular_reactions(5)
    print(f"Top reactions: {popular}")
```

## Channel Event Handling

### Channel Lifecycle Tracking

```python
from slack_models import (
    ChannelCreatedEvent, ChannelDeletedEvent,
    ChannelRenameEvent, Channel
)

class ChannelTracker:
    def __init__(self):
        self.channels = {}
        self.channel_history = []

    def channel_created(self, event: ChannelCreatedEvent):
        """Track channel creation."""
        channel = event.channel
        self.channels[channel.id] = channel
        self.channel_history.append({
            "action": "created",
            "channel_id": channel.id,
            "channel_name": channel.name,
            "creator": channel.creator,
            "timestamp": channel.created
        })
        print(f"Channel #{channel.name} created by {channel.creator}")

    def channel_deleted(self, event: ChannelDeletedEvent):
        """Track channel deletion."""
        channel_id = event.channel
        if channel_id in self.channels:
            channel = self.channels[channel_id]
            del self.channels[channel_id]
            self.channel_history.append({
                "action": "deleted",
                "channel_id": channel_id,
                "channel_name": channel.name,
                "timestamp": event.event_ts
            })
            print(f"Channel #{channel.name} deleted")

    def channel_renamed(self, event: ChannelRenameEvent):
        """Track channel renaming."""
        channel = event.channel
        old_name = self.channels[channel.id].name if channel.id in self.channels else "unknown"

        self.channels[channel.id] = channel
        self.channel_history.append({
            "action": "renamed",
            "channel_id": channel.id,
            "old_name": old_name,
            "new_name": channel.name,
            "timestamp": channel.created
        })
        print(f"Channel renamed from #{old_name} to #{channel.name}")

    def get_channel_stats(self):
        """Get channel statistics."""
        return {
            "total_channels": len(self.channels),
            "total_events": len(self.channel_history),
            "recent_activity": self.channel_history[-5:]
        }

# Usage
tracker = ChannelTracker()

def handle_channel_created(event: ChannelCreatedEvent):
    tracker.channel_created(event)

def handle_channel_deleted(event: ChannelDeletedEvent):
    tracker.channel_deleted(event)

def handle_channel_renamed(event: ChannelRenameEvent):
    tracker.channel_renamed(event)
```

## Team Event Handling

### New Member Onboarding

```python
from slack_models import TeamJoinEvent, User

class OnboardingBot:
    def __init__(self):
        self.new_members = []
        self.welcome_message = "Welcome to the team! 🎉"

    def handle_team_join(self, event: TeamJoinEvent):
        """Handle new team member joining."""
        user = event.user
        self.new_members.append(user)

        print(f"New team member: {user.real_name} ({user.name})")
        print(f"Email: {user.profile.email}")
        print(f"Title: {user.profile.title}")

        # Send welcome message (simulated)
        self.send_welcome_message(user)

        # Notify admins if needed
        if self.should_notify_admins(user):
            self.notify_admins(user)

    def send_welcome_message(self, user: User):
        """Send welcome message to new member."""
        message = f"Hi {user.profile.first_name or user.name}! {self.welcome_message}"
        print(f"Sending welcome message: {message}")

    def should_notify_admins(self, user: User) -> bool:
        """Check if admins should be notified."""
        # Notify for external or guest users
        return user.is_restricted or user.is_ultra_restricted

    def notify_admins(self, user: User):
        """Notify admins about new member."""
        user_type = "restricted" if user.is_restricted else "ultra_restricted"
        print(f"Notifying admins: New {user_type} user {user.name} joined")

    def get_recent_members(self, limit: int = 10):
        """Get recently joined members."""
        return self.new_members[-limit:]

# Usage
onboarding = OnboardingBot()

def handle_team_join(event: TeamJoinEvent):
    onboarding.handle_team_join(event)
```

## File Event Handling

### File Activity Monitoring

```python
from slack_models import FileCreatedEvent, FileDeletedEvent, File

class FileMonitor:
    def __init__(self):
        self.files = {}
        self.file_activity = []

    def file_created(self, event: FileCreatedEvent):
        """Monitor file creation."""
        file = event.file
        self.files[file.id] = file

        activity = {
            "action": "created",
            "file_id": file.id,
            "file_name": file.name,
            "file_type": file.pretty_type,
            "user": file.user,
            "size": file.size,
            "timestamp": file.created
        }
        self.file_activity.append(activity)

        print(f"File created: {file.name} ({file.pretty_type})")
        print(f"Size: {file.size} bytes")
        print(f"User: {file.user}")

        # Check for large files
        if file.size > 10 * 1024 * 1024:  # 10MB
            print(f"⚠️  Large file detected: {file.name} ({file.size} bytes)")

        # Check for sensitive file types
        sensitive_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx']
        if file.filetype in sensitive_types:
            print(f"📄 Sensitive file type: {file.filetype}")

    def file_deleted(self, event: FileDeletedEvent):
        """Monitor file deletion."""
        file_id = event.file_id

        if file_id in self.files:
            file = self.files[file_id]
            del self.files[file_id]

            activity = {
                "action": "deleted",
                "file_id": file_id,
                "file_name": file.name,
                "timestamp": event.event_ts
            }
            self.file_activity.append(activity)

            print(f"File deleted: {file.name}")

    def get_file_stats(self):
        """Get file activity statistics."""
        total_size = sum(f.size for f in self.files.values())
        file_types = {}

        for file in self.files.values():
            file_types[file.filetype] = file_types.get(file.filetype, 0) + 1

        return {
            "total_files": len(self.files),
            "total_size": total_size,
            "file_types": file_types,
            "recent_activity": self.file_activity[-10:]
        }

# Usage
monitor = FileMonitor()

def handle_file_created(event: FileCreatedEvent):
    monitor.file_created(event)

def handle_file_deleted(event: FileDeletedEvent):
    monitor.file_deleted(event)
```

## Advanced Event Processing

### Event Correlation

```python
from slack_models import MessageEvent, ReactionAddedEvent
from datetime import datetime, timedelta

class EventCorrelator:
    def __init__(self):
        self.message_reactions = {}
        self.correlation_window = timedelta(hours=1)

    def correlate_message_reactions(self, message: MessageEvent):
        """Start tracking reactions for a message."""
        key = (message.channel, message.ts)
        self.message_reactions[key] = {
            "message": message,
            "reactions": [],
            "created_at": datetime.now()
        }
        print(f"Started tracking reactions for message: {message.text[:50]}...")

    def correlate_reaction(self, reaction: ReactionAddedEvent):
        """Correlate reaction with original message."""
        key = (reaction.item.channel, reaction.item.ts)

        if key in self.message_reactions:
            self.message_reactions[key]["reactions"].append(reaction)
            print(f"Reaction {reaction.reaction} correlated with message")

            # Analyze reaction patterns
            self.analyze_reaction_patterns(key)

    def analyze_reaction_patterns(self, key):
        """Analyze reaction patterns for a message."""
        data = self.message_reactions[key]
        message = data["message"]
        reactions = data["reactions"]

        if len(reactions) >= 3:
            reaction_types = [r.reaction for r in reactions]
            print(f"Popular message (3+ reactions): {message.text[:50]}...")
            print(f"Reactions: {', '.join(reaction_types)}")

    def cleanup_old_correlations(self):
        """Clean up old correlation data."""
        cutoff = datetime.now() - self.correlation_window

        old_keys = [
            key for key, data in self.message_reactions.items()
            if data["created_at"] < cutoff
        ]

        for key in old_keys:
            del self.message_reactions[key]

        print(f"Cleaned up {len(old_keys)} old correlations")

# Usage
correlator = EventCorrelator()

def handle_message_for_correlation(message: MessageEvent):
    correlator.correlate_message_reactions(message)

def handle_reaction_for_correlation(reaction: ReactionAddedEvent):
    correlator.correlate_reaction(reaction)
```

### Event Batching

```python
from slack_models import BaseSlackEvent
from typing import List
import asyncio

class EventBatcher:
    def __init__(self, batch_size: int = 10, batch_timeout: float = 5.0):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.batch = []
        self.batch_timer = None

    def add_event(self, event: BaseSlackEvent):
        """Add event to batch."""
        self.batch.append(event)

        # Reset timer
        if self.batch_timer:
            self.batch_timer.cancel()

        # Process batch if full
        if len(self.batch) >= self.batch_size:
            self.process_batch()
        else:
            # Set timer for timeout
            self.batch_timer = asyncio.create_task(
                self.batch_timeout_handler()
            )

    async def batch_timeout_handler(self):
        """Handle batch timeout."""
        await asyncio.sleep(self.batch_timeout)
        if self.batch:
            self.process_batch()

    def process_batch(self):
        """Process the current batch."""
        if not self.batch:
            return

        print(f"Processing batch of {len(self.batch)} events")

        # Group events by type
        event_types = {}
        for event in self.batch:
            event_type = type(event).__name__
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print(f"Event types in batch: {event_types}")

        # Process events
        for event in self.batch:
            self.process_single_event(event)

        # Clear batch
        self.batch.clear()

        if self.batch_timer:
            self.batch_timer.cancel()
            self.batch_timer = None

    def process_single_event(self, event: BaseSlackEvent):
        """Process a single event."""
        print(f"Processing {type(event).__name__}")

# Usage
batcher = EventBatcher(batch_size=5, batch_timeout=3.0)

def handle_any_event(event: BaseSlackEvent):
    batcher.add_event(event)
```
