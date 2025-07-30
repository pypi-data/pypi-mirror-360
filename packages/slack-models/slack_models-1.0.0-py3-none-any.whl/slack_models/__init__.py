"""
# slack-models

Pydantic Models for working with the Slack API

"""

from importlib import metadata

from ._models import (
    EVENT_MAP,
    AppMentionEvent,
    Authorization,
    BaseSlackEvent,
    Channel,
    ChannelCreatedEvent,
    ChannelDeletedEvent,
    ChannelRenameEvent,
    ChatMessage,
    EnterpriseUser,
    File,
    FileContent,
    FileCreatedEvent,
    FileDeletedEvent,
    MessageEdited,
    MessageEvent,
    MessageItem,
    Reaction,
    ReactionAddedEvent,
    ReactionRemovedEvent,
    SlackAppRateLimited,
    SlackEvent,
    SlackEventCallback,
    SlackUrlVerification,
    SlackWebhookPayload,
    TeamJoinEvent,
    User,
    UserProfile,
)
from ._utils import parse_event

try:
    version = metadata.version('slack-models')
except metadata.PackageNotFoundError:
    # Fallback when running from source without installation
    version = '0.0.0-dev'

__all__ = [
    'EVENT_MAP',
    'AppMentionEvent',
    'Authorization',
    'BaseSlackEvent',
    'Channel',
    'ChannelCreatedEvent',
    'ChannelDeletedEvent',
    'ChannelRenameEvent',
    'ChatMessage',
    'EnterpriseUser',
    'File',
    'FileContent',
    'FileCreatedEvent',
    'FileDeletedEvent',
    'MessageEdited',
    'MessageEvent',
    'MessageItem',
    'Reaction',
    'ReactionAddedEvent',
    'ReactionRemovedEvent',
    'SlackAppRateLimited',
    'SlackEvent',
    'SlackEventCallback',
    'SlackUrlVerification',
    'SlackWebhookPayload',
    'TeamJoinEvent',
    'User',
    'UserProfile',
    'parse_event',
    'version',
]
