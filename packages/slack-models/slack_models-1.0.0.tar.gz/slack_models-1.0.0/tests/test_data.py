"""Test data fixtures for slack-models tests."""

import datetime

# User and Profile test data
USER_PROFILE_DATA = {
    'title': 'Senior Developer',
    'phone': '+1-555-123-4567',
    'skype': 'john.doe',
    'email': 'john.doe@example.com',
    'real_name': 'John Doe',
    'display_name': 'John',
    'first_name': 'John',
    'last_name': 'Doe',
    'real_name_normalized': 'john doe',
    'display_name_normalized': 'john',
    'status_text': 'Working from home',
    'status_emoji': ':house:',
    'status_expiration': 1640995200,
    'avatar_hash': 'abc123',
    'always_active': False,
    'image_24': 'https://example.com/avatar_24.jpg',
    'image_32': 'https://example.com/avatar_32.jpg',
    'image_48': 'https://example.com/avatar_48.jpg',
    'image_72': 'https://example.com/avatar_72.jpg',
    'image_192': 'https://example.com/avatar_192.jpg',
    'image_512': 'https://example.com/avatar_512.jpg',
    'image_1024': 'https://example.com/avatar_1024.jpg',
    'image_original': 'https://example.com/avatar_original.jpg',
    'status_text_canonical': 'Working from home',
    'team': 'T1234567890',
}

ENTERPRISE_USER_DATA = {
    'enterprise_id': 'E1234567890',
    'enterprise_name': 'Test Enterprise',
    'is_admin': True,
    'is_owner': False,
    'teams': ['T1234567890', 'T0987654321'],
}

USER_DATA = {
    'id': 'U1234567890',
    'team_id': 'T1234567890',
    'name': 'john.doe',
    'deleted': False,
    'color': '9f69e7',
    'real_name': 'John Doe',
    'tz': 'America/New_York',
    'tz_label': 'Eastern Standard Time',
    'tz_offset': -18000,
    'profile': USER_PROFILE_DATA,
    'is_bot': False,
    'is_admin': False,
    'is_owner': False,
    'is_primary_owner': False,
    'is_restricted': False,
    'is_ultra_restricted': False,
    'is_app_user': False,
    'enterprise_user': ENTERPRISE_USER_DATA,
    'updated': 1640995200,
    'is_email_confirmed': True,
    'who_can_share_contact_card': 'EVERYONE',
}

# Channel test data
CHANNEL_DATA = {
    'id': 'C1234567890',
    'name': 'general',
    'is_channel': True,
    'created': 1640995200,
    'creator': 'U1234567890',
    'is_archived': False,
    'is_general': True,
    'name_normalized': 'general',
    'is_shared': False,
    'is_org_shared': False,
    'is_member': True,
    'is_private': False,
    'is_mpim': False,
    'is_im': False,
    'last_read': '1640995200.000100',
    'latest': {'type': 'message', 'text': 'Hello world'},
    'unread_count': 0,
    'unread_count_display': 0,
    'members': ['U1234567890', 'U0987654321'],
    'topic': {'value': 'General discussion', 'creator': 'U1234567890'},
    'purpose': {
        'value': 'Company-wide announcements',
        'creator': 'U1234567890',
    },
    'previous_names': ['old-general'],
}

# File test data
FILE_DATA = {
    'id': 'F1234567890',
    'name': 'example.txt',
    'title': 'Example File',
    'mimetype': 'text/plain',
    'size': 1024,
    'mode': 'hosted',
    'url_private': 'https://files.slack.com/files-pri/T1234567890-F1234567890/example.txt',
    'url_private_download': 'https://files.slack.com/files-pri/T1234567890-F1234567890/download/example.txt',
}

FILE_CONTENT_DATA = {'mimetype': 'text/plain', 'content': 'Hello, world!'}

# Reaction test data
REACTION_DATA = {
    'name': 'thumbsup',
    'count': 2,
    'users': ['U1234567890', 'U0987654321'],
}

# Message components test data
MESSAGE_ITEM_DATA = {
    'type': 'message',
    'channel': 'C1234567890',
    'ts': '1640995200.000100',
    'thread_ts': '1640995200.000100',
}

MESSAGE_EDITED_DATA = {'user': 'U1234567890', 'ts': '1640995200.000200'}

# Chat message test data
CHAT_MESSAGE_DATA = {
    'user': USER_DATA,
    'content': 'Hello, world!',
    'files': [FILE_DATA],
    'ts': '1640995200.000100',
    'thread_ts': '1640995200.000100',
    'timestamp': datetime.datetime.fromtimestamp(1640995200, tz=datetime.UTC),
}

# Authorization test data
AUTHORIZATION_DATA = {
    'enterprise_id': 'E1234567890',
    'team_id': 'T1234567890',
    'user_id': 'U1234567890',
    'is_bot': False,
    'is_enterprise_install': False,
}

# Event test data
MESSAGE_EVENT_DATA = {
    'type': 'message',
    'channel': 'C1234567890',
    'user': 'U1234567890',
    'text': 'Hello, world!',
    'ts': '1640995200.000100',
    'thread_ts': '1640995200.000100',
    'subtype': None,
    'edited': MESSAGE_EDITED_DATA,
    'files': [FILE_DATA],
    'reactions': [REACTION_DATA],
    'is_starred': False,
    'pinned_to': ['C1234567890'],
    'parent_user_id': 'U1234567890',
    'reply_count': 5,
    'reply_users': ['U1234567890', 'U0987654321'],
    'reply_users_count': 2,
    'latest_reply': '1640995200.000200',
    'hidden': False,
    'deleted_ts': None,
    'event_ts': '1640995200.000100',
}

APP_MENTION_EVENT_DATA = {
    'type': 'app_mention',
    'channel': 'C1234567890',
    'user': 'U1234567890',
    'text': '<@U0987654321> Hello!',
    'ts': '1640995200.000100',
    'thread_ts': '1640995200.000100',
    'event_ts': '1640995200.000100',
}

REACTION_ADDED_EVENT_DATA = {
    'type': 'reaction_added',
    'user': 'U1234567890',
    'reaction': 'thumbsup',
    'item': MESSAGE_ITEM_DATA,
    'item_user': 'U0987654321',
    'event_ts': '1640995200.000100',
}

REACTION_REMOVED_EVENT_DATA = {
    'type': 'reaction_removed',
    'user': 'U1234567890',
    'reaction': 'thumbsup',
    'item': MESSAGE_ITEM_DATA,
    'item_user': 'U0987654321',
    'event_ts': '1640995200.000100',
}

TEAM_JOIN_EVENT_DATA = {
    'type': 'team_join',
    'user': USER_DATA,
    'event_ts': '1640995200.000100',
}

FILE_CREATED_EVENT_DATA = {
    'type': 'file_created',
    'file_id': 'F1234567890',
    'file': FILE_DATA,
    'user_id': 'U1234567890',
    'event_ts': '1640995200.000100',
}

FILE_DELETED_EVENT_DATA = {
    'type': 'file_deleted',
    'file_id': 'F1234567890',
    'user_id': 'U1234567890',
    'event_ts': '1640995200.000100',
}

CHANNEL_CREATED_EVENT_DATA = {
    'type': 'channel_created',
    'channel': CHANNEL_DATA,
    'event_ts': '1640995200.000100',
}

CHANNEL_DELETED_EVENT_DATA = {
    'type': 'channel_deleted',
    'channel': 'C1234567890',
    'event_ts': '1640995200.000100',
}

CHANNEL_RENAME_EVENT_DATA = {
    'type': 'channel_rename',
    'channel': CHANNEL_DATA,
    'event_ts': '1640995200.000100',
}

# Webhook payload test data
SLACK_EVENT_CALLBACK_DATA = {
    'token': 'verification_token',  # noqa: S106
    'team_id': 'T1234567890',
    'api_app_id': 'A1234567890',
    'event': MESSAGE_EVENT_DATA,
    'type': 'event_callback',
    'event_id': 'Ev1234567890',
    'event_time': 1640995200,
    'event_context': 'EC1234567890',
    'authorizations': [AUTHORIZATION_DATA],
}

SLACK_URL_VERIFICATION_DATA = {
    'token': 'verification_token',  # noqa: S106
    'challenge': 'challenge_string',
    'type': 'url_verification',
}

SLACK_APP_RATE_LIMITED_DATA = {
    'token': 'verification_token',  # noqa: S106
    'team_id': 'T1234567890',
    'minute_rate_limited': 30000,
    'api_app_id': 'A1234567890',
    'type': 'app_rate_limited',
}

# Minimal data for testing required fields only
MINIMAL_USER_DATA = {'id': 'U1234567890'}

MINIMAL_CHANNEL_DATA = {'id': 'C1234567890'}

MINIMAL_FILE_DATA = {
    'id': 'F1234567890',
    'name': 'example.txt',
    'title': 'Example File',
    'mimetype': 'text/plain',
    'size': 1024,
    'mode': 'hosted',
    'url_private': 'https://files.slack.com/files-pri/T1234567890-F1234567890/example.txt',
}

MINIMAL_MESSAGE_EVENT_DATA = {
    'type': 'message',
    'channel': 'C1234567890',
    'user': 'U1234567890',
    'text': 'Hello, world!',
    'ts': '1640995200.000100',
}

MINIMAL_AUTHORIZATION_DATA = {
    'team_id': 'T1234567890',
    'user_id': 'U1234567890',
    'is_bot': False,
    'is_enterprise_install': False,
}

MINIMAL_SLACK_EVENT_CALLBACK_DATA = {
    'token': 'verification_token',  # noqa: S106
    'team_id': 'T1234567890',
    'api_app_id': 'A1234567890',
    'event': MINIMAL_MESSAGE_EVENT_DATA,
    'type': 'event_callback',
    'event_id': 'Ev1234567890',
    'event_time': 1640995200,
}
