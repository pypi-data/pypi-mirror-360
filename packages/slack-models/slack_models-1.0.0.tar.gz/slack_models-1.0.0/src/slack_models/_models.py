import datetime
import typing

import pydantic


class Channel(pydantic.BaseModel):
    """A legacy object that contains information about a workspace channel.

    Represents a communication space within Slack containing metadata like
    channel ID, name, creation timestamp, creator, and membership status.
    Includes details such as whether the channel is archived, general,
    shared, or private, and tracks information like last read message,
    unread message count, and channel topic/purpose.

    Note: This is different from private channels (which are group objects).
    """

    id: str
    name: str = ''
    is_channel: bool | None = None
    created: int | None = None
    creator: str | None = None
    is_archived: bool = False
    is_general: bool | None = None
    name_normalized: str | None = None
    is_shared: bool | None = None
    is_org_shared: bool = False
    is_member: bool | None = None
    is_private: bool | None = None
    is_mpim: bool | None = None
    is_im: bool = False
    last_read: str | None = None
    latest: dict | None = None
    unread_count: int = 0
    unread_count_display: int = 0
    members: list[str] | None = None
    topic: dict | None = None
    purpose: dict | None = None
    previous_names: list[str] | None = None


class UserProfile(pydantic.BaseModel):
    """Contains detailed profile information for a Slack user.

    Stores both standard and custom profile fields including user status,
    contact information, display names, and profile images. Profile
    composition can vary and not all fields will be present for every user.
    """

    title: str | None = None
    phone: str | None = None
    skype: str | None = None
    email: str | None = None
    real_name: str | None = None
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    real_name_normalized: str | None = None
    display_name_normalized: str | None = None
    fields: list[dict] | None = None
    status_text: str | None = None
    status_emoji: str | None = None
    status_expiration: int | None = None
    avatar_hash: str | None = None
    always_active: bool | None = False
    image_original: str | None = None
    image_24: str | None = None
    image_32: str | None = None
    image_48: str | None = None
    image_72: str | None = None
    image_192: str | None = None
    image_512: str | None = None
    image_1024: str | None = None
    status_text_canonical: str | None = None
    team: str | None = None


class EnterpriseUser(pydantic.BaseModel):
    """Contains Enterprise Grid-specific user information.

    Provides details about a user's enterprise identity including
    enterprise ID, name, administrative roles, and team memberships
    within the Enterprise Grid structure.
    """

    enterprise_id: str
    enterprise_name: str
    is_admin: bool
    is_owner: bool
    teams: list[str] | None = None


class User(pydantic.BaseModel):
    """A comprehensive representation of a Slack workspace user.

    Provides detailed information about a user within a Slack workspace,
    including profile details, workspace roles, and account settings.
    Contains workspace-specific information and may include Enterprise Grid
    user data. User object composition can vary and not all fields will be
    present for every user.
    """

    id: str
    team_id: str | None = None
    name: str | None = None
    deleted: bool = False
    color: str | None = None
    real_name: str | None = None
    tz: str | None = None
    tz_label: str | None = None
    tz_offset: int | None = None
    profile: UserProfile | None = None
    is_bot: bool = False
    is_admin: bool = False
    is_owner: bool = False
    is_primary_owner: bool = False
    is_restricted: bool = False
    is_ultra_restricted: bool = False
    is_app_user: bool = False
    enterprise_user: EnterpriseUser | None = None
    updated: int | None = None
    is_email_confirmed: bool | None = None
    who_can_share_contact_card: str | None = None

    @property
    def display_name(self) -> str:
        """Return the name to display"""
        if not self.profile:
            return self.name or self.id
        return (
            self.profile.display_name
            or self.profile.first_name
            or self.name
            or self.id
        )


class File(pydantic.BaseModel):
    """A file object contains information about a file shared with a workspace.

    Represents a file shared within a Slack workspace, including unique
    identifier, creation timestamp, file metadata like name, type, and size,
    user who uploaded the file, sharing information, and thumbnail/preview
    URLs.
    Authentication is required to access file URLs.
    """

    model_config = pydantic.ConfigDict(extra='ignore')

    id: str
    name: str
    title: str
    mimetype: str
    size: int
    mode: str
    url_private: str
    url_private_download: str | None = None


class FileContent(pydantic.BaseModel):
    """Represents downloaded file content with MIME type information.

    Contains the actual file data (as bytes) along with its MIME type,
    used for processing file attachments from Slack messages.
    """

    mimetype: str
    content: str | bytes


class ChatMessage(pydantic.BaseModel):
    """Represents a processed Slack message for bot operations.

    Used internally by the bot for conversation history and context,
    containing user information, message content, file attachments,
    and temporal data for thread organization.
    """

    user: User
    content: str
    files: list[File] | None = None
    ts: str
    thread_ts: str
    timestamp: datetime.datetime


class Reaction(pydantic.BaseModel):
    """Represents an emoji reaction on a Slack message.

    Contains the reaction emoji name, count of users who reacted,
    and list of user IDs who added this reaction to the message.
    """

    name: str
    count: int
    users: list[str]


class MessageItem(pydantic.BaseModel):
    """Represents an item referenced in a Slack event.

    Used in reaction events to identify the target item (message, file,
    or file comment) that was reacted to. Contains the item type,
    channel/location, and timestamp information.
    """

    type: str = 'message'
    channel: str
    ts: str
    thread_ts: str | None = None


class MessageEdited(pydantic.BaseModel):
    """Contains metadata about a message edit.

    Tracks who edited the message and when the edit occurred,
    used in message events to indicate post-creation modifications.
    """

    user: str
    ts: str


class Authorization(pydantic.BaseModel):
    """Contains authorization information for a Slack webhook event.

    Provides details about the app installation including enterprise ID,
    team ID, user ID, and installation type. Used by Events API to
    identify the authorization context for the event.
    """

    enterprise_id: str | None = None
    team_id: str
    user_id: str
    is_bot: bool
    is_enterprise_install: bool


class BaseSlackEvent(pydantic.BaseModel):
    """Base class for all Slack event types.

    Contains common fields shared across all Slack events including
    event type, timestamp, and event timestamp.
    All specific event types inherit from this base class.
    """

    type: str
    ts: str | None = None
    event_ts: str | None = None


class MessageEvent(BaseSlackEvent):
    """A message was sent to a channel.

    Delivered when a message is posted to a channel, containing details
    like channel ID, user ID, message text, and timestamp. Can have
    various subtypes and may include additional properties like stars,
    pins, reactions, and file attachments.
    """

    type: typing.Literal['message'] = 'message'
    channel: str
    user: str
    text: str
    ts: str
    thread_ts: str | None = None
    subtype: str | None = None
    edited: MessageEdited | None = None
    files: list[File] | None = None
    reactions: list[Reaction] | None = None
    is_starred: bool | None = None
    pinned_to: list[str] | None = None
    parent_user_id: str | None = None
    reply_count: int | None = None
    reply_users: list[str] | None = None
    reply_users_count: int | None = None
    latest_reply: str | None = None
    hidden: bool | None = None
    deleted_ts: str | None = None


class AppMentionEvent(BaseSlackEvent):
    """Subscribe to message events that directly mention your app.

    Allows a Slack app to receive messages where the app is explicitly
    mentioned. Requires the app_mentions:read scope and only includes
    messages where the app is directly mentioned, not direct messages
    to the app.
    """

    type: typing.Literal['app_mention'] = 'app_mention'
    channel: str
    user: str
    text: str
    ts: str
    thread_ts: str | None = None
    event_ts: str


class ReactionAddedEvent(BaseSlackEvent):
    """A member has added an emoji reaction to an item.

    Sent when a user adds an emoji reaction to a message, file, or other
    item. Includes details about who added the reaction, what emoji was
    used, and which item was reacted to. Requires the reactions:read scope.
    """

    type: typing.Literal['reaction_added'] = 'reaction_added'
    user: str
    reaction: str
    item: MessageItem
    item_user: str | None = None
    event_ts: str


class ReactionRemovedEvent(BaseSlackEvent):
    """A reaction is removed from an item.

    Triggered when a user removes an emoji reaction from a message, file,
    or other item. Includes details about who removed the reaction, what
    emoji was removed, and which item was affected. Requires the
    reactions:read scope.
    """

    type: typing.Literal['reaction_removed'] = 'reaction_removed'
    user: str
    reaction: str
    item: MessageItem
    item_user: str | None = None
    event_ts: str


class TeamJoinEvent(BaseSlackEvent):
    """A new member has joined the team.

    Sent to all connections for a workspace when a new member joins,
    helping clients update their local cache of members. Includes
    user object with details about the new team member. Requires
    the users:read scope.
    """

    type: typing.Literal['team_join'] = 'team_join'
    user: User  # Full user object - override base class string type
    event_ts: str


class FileCreatedEvent(BaseSlackEvent):
    """A file was created.

    Sent when a user uploads a file to Slack. Contains file details
    and user information. When a file is shared with workspace members,
    a separate file_shared event is also sent. Requires the files:read
    scope.
    """

    type: typing.Literal['file_created'] = 'file_created'
    file_id: str
    file: dict  # Full file object
    user_id: str
    event_ts: str


class FileDeletedEvent(BaseSlackEvent):
    """A file was deleted.

    Sent to all connected clients in a workspace when a file is deleted.
    Contains only the file ID, not a full file object. Not raised if
    file removal is due to workspace's file retention policy. Requires
    the files:read scope.
    """

    type: typing.Literal['file_deleted'] = 'file_deleted'
    file_id: str
    user_id: str
    event_ts: str


class ChannelCreatedEvent(BaseSlackEvent):
    """A channel was created.

    Sent when a new channel is created in a workspace to help clients
    update their local cache of non-joined channels. Includes channel
    metadata such as ID, name, creation timestamp, and creator.
    Requires the channels:read scope.
    """

    type: typing.Literal['channel_created'] = 'channel_created'
    channel: dict  # Full channel object
    event_ts: str


class ChannelDeletedEvent(BaseSlackEvent):
    """A channel was deleted.

    Sent to all connections for a workspace when a channel is deleted
    to help clients update their local cache of non-joined channels.
    Contains the deleted channel's ID. Requires the channels:read scope.
    """

    type: typing.Literal['channel_deleted'] = 'channel_deleted'
    channel: str  # Channel ID
    event_ts: str


class ChannelRenameEvent(BaseSlackEvent):
    """A channel was renamed.

    Sent to all workspace connections when a channel is renamed,
    allowing clients to update their local list of channels.
    Contains the channel's new ID, name, and creation timestamp.
    Requires the channels:read scope.
    """

    type: typing.Literal['channel_rename'] = 'channel_rename'
    channel: dict  # Channel object with new name
    event_ts: str


# Union type for all possible events
SlackEvent = (
    MessageEvent
    | AppMentionEvent
    | ReactionAddedEvent
    | ReactionRemovedEvent
    | TeamJoinEvent
    | FileCreatedEvent
    | FileDeletedEvent
    | ChannelCreatedEvent
    | ChannelDeletedEvent
    | ChannelRenameEvent
)


class SlackEventCallback(pydantic.BaseModel):
    """Event callback payload from Slack Events API.

    Standard envelope for event notifications sent via HTTP endpoint.
    Contains authentication token, workspace identifier, app identifier,
    event details, and authorization context. Events are delivered with
    a 3-second response timeout and include retry mechanisms.
    """

    token: str
    team_id: str
    api_app_id: str
    event: SlackEvent
    type: typing.Literal['event_callback'] = 'event_callback'
    event_id: str
    event_time: int
    event_context: str | None = None
    authorizations: list[Authorization] | None = None

    model_config = pydantic.ConfigDict(extra='allow')


class SlackUrlVerification(pydantic.BaseModel):
    """URL verification challenge from Slack.

    Sent during Events API endpoint setup to verify endpoint ownership.
    Contains a challenge string that must be echoed back in the response
    to complete the verification process.
    """

    token: str
    challenge: str
    type: typing.Literal['url_verification'] = 'url_verification'


class SlackAppRateLimited(pydantic.BaseModel):
    """App rate limited notification from Slack.

    Sent when an app exceeds the Events API rate limit of 30,000 events
    per workspace per hour. Contains the minute-based rate limit count
    and workspace/app identifiers.
    """

    token: str
    team_id: str
    minute_rate_limited: int
    api_app_id: str
    type: typing.Literal['app_rate_limited'] = 'app_rate_limited'


# Union type for all possible webhook payloads
SlackWebhookPayload = (
    SlackEventCallback | SlackUrlVerification | SlackAppRateLimited
)

EVENT_MAP = {
    'message': MessageEvent,
    'app_mention': AppMentionEvent,
    'reaction_added': ReactionAddedEvent,
    'reaction_removed': ReactionRemovedEvent,
    'team_join': TeamJoinEvent,
    'file_created': FileCreatedEvent,
    'file_deleted': FileDeletedEvent,
    'channel_created': ChannelCreatedEvent,
    'channel_deleted': ChannelDeletedEvent,
    'channel_rename': ChannelRenameEvent,
}
