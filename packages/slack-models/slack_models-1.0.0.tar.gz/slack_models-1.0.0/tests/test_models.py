"""Comprehensive tests for all slack-models Pydantic models."""

import datetime
import unittest

import pydantic

import slack_models

from .test_data import (
    AUTHORIZATION_DATA,
    CHANNEL_DATA,
    CHAT_MESSAGE_DATA,
    ENTERPRISE_USER_DATA,
    FILE_CONTENT_DATA,
    FILE_DATA,
    MESSAGE_EDITED_DATA,
    MESSAGE_ITEM_DATA,
    MINIMAL_AUTHORIZATION_DATA,
    MINIMAL_CHANNEL_DATA,
    MINIMAL_FILE_DATA,
    MINIMAL_USER_DATA,
    REACTION_DATA,
    USER_DATA,
    USER_PROFILE_DATA,
)


class TestUserProfile(unittest.TestCase):
    """Test UserProfile model."""

    def test_user_profile_full_data(self) -> None:
        """Test UserProfile with all fields."""
        profile = slack_models.UserProfile(**USER_PROFILE_DATA)

        self.assertEqual(profile.title, 'Senior Developer')
        self.assertEqual(profile.email, 'john.doe@example.com')
        self.assertEqual(profile.real_name, 'John Doe')
        self.assertEqual(profile.display_name, 'John')
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.status_text, 'Working from home')
        self.assertEqual(profile.status_emoji, ':house:')
        self.assertEqual(profile.avatar_hash, 'abc123')
        self.assertFalse(profile.always_active)

    def test_user_profile_minimal_data(self) -> None:
        """Test UserProfile with minimal data."""
        profile = slack_models.UserProfile()

        self.assertIsNone(profile.title)
        self.assertIsNone(profile.email)
        self.assertIsNone(profile.real_name)
        self.assertIsNone(profile.display_name)
        self.assertFalse(profile.always_active)

    def test_user_profile_optional_fields(self) -> None:
        """Test UserProfile optional fields."""
        profile = slack_models.UserProfile(
            title='Developer',
            email='test@example.com',
            status_text='Away',
            status_emoji=':zzz:',
            always_active=True,
        )

        self.assertEqual(profile.title, 'Developer')
        self.assertEqual(profile.email, 'test@example.com')
        self.assertEqual(profile.status_text, 'Away')
        self.assertEqual(profile.status_emoji, ':zzz:')
        self.assertTrue(profile.always_active)


class TestEnterpriseUser(unittest.TestCase):
    """Test EnterpriseUser model."""

    def test_enterprise_user_full_data(self) -> None:
        """Test EnterpriseUser with all fields."""
        enterprise_user = slack_models.EnterpriseUser(**ENTERPRISE_USER_DATA)

        self.assertEqual(enterprise_user.enterprise_id, 'E1234567890')
        self.assertEqual(enterprise_user.enterprise_name, 'Test Enterprise')
        self.assertTrue(enterprise_user.is_admin)
        self.assertFalse(enterprise_user.is_owner)
        self.assertEqual(enterprise_user.teams, ['T1234567890', 'T0987654321'])

    def test_enterprise_user_minimal_data(self) -> None:
        """Test EnterpriseUser with minimal required fields."""
        enterprise_user = slack_models.EnterpriseUser(
            enterprise_id='E1234567890',
            enterprise_name='Test Enterprise',
            is_admin=False,
            is_owner=False,
        )

        self.assertEqual(enterprise_user.enterprise_id, 'E1234567890')
        self.assertEqual(enterprise_user.enterprise_name, 'Test Enterprise')
        self.assertFalse(enterprise_user.is_admin)
        self.assertFalse(enterprise_user.is_owner)
        self.assertIsNone(enterprise_user.teams)


class TestUser(unittest.TestCase):
    """Test User model."""

    def test_user_full_data(self) -> None:
        """Test User with all fields."""
        user = slack_models.User(**USER_DATA)

        self.assertEqual(user.id, 'U1234567890')
        self.assertEqual(user.team_id, 'T1234567890')
        self.assertEqual(user.name, 'john.doe')
        self.assertFalse(user.deleted)
        self.assertEqual(user.color, '9f69e7')
        self.assertEqual(user.real_name, 'John Doe')
        self.assertEqual(user.tz, 'America/New_York')
        self.assertEqual(user.tz_offset, -18000)
        self.assertIsInstance(user.profile, slack_models.UserProfile)
        self.assertIsInstance(
            user.enterprise_user, slack_models.EnterpriseUser
        )
        self.assertTrue(user.is_email_confirmed)

    def test_user_minimal_data(self) -> None:
        """Test User with minimal required fields."""
        user = slack_models.User(**MINIMAL_USER_DATA)

        self.assertEqual(user.id, 'U1234567890')
        self.assertIsNone(user.team_id)
        self.assertIsNone(user.name)
        self.assertFalse(user.deleted)
        self.assertFalse(user.is_bot)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_owner)
        self.assertFalse(user.is_primary_owner)
        self.assertFalse(user.is_restricted)
        self.assertFalse(user.is_ultra_restricted)
        self.assertFalse(user.is_app_user)

    def test_user_display_name_property(self) -> None:
        """Test User display_name property logic."""
        # Test with profile display_name
        user = slack_models.User(
            id='U1234567890',
            name='john.doe',
            profile=slack_models.UserProfile(display_name='John'),
        )
        self.assertEqual(user.display_name, 'John')

        # Test with profile first_name (no display_name)
        user = slack_models.User(
            id='U1234567890',
            name='john.doe',
            profile=slack_models.UserProfile(first_name='John'),
        )
        self.assertEqual(user.display_name, 'John')

        # Test with name (no profile display_name or first_name)
        user = slack_models.User(
            id='U1234567890',
            name='john.doe',
            profile=slack_models.UserProfile(),
        )
        self.assertEqual(user.display_name, 'john.doe')

        # Test with no profile
        user = slack_models.User(id='U1234567890', name='john.doe')
        self.assertEqual(user.display_name, 'john.doe')

        # Test fallback to ID
        user = slack_models.User(id='U1234567890')
        self.assertEqual(user.display_name, 'U1234567890')


class TestChannel(unittest.TestCase):
    """Test Channel model."""

    def test_channel_full_data(self) -> None:
        """Test Channel with all fields."""
        channel = slack_models.Channel(**CHANNEL_DATA)

        self.assertEqual(channel.id, 'C1234567890')
        self.assertEqual(channel.name, 'general')
        self.assertTrue(channel.is_channel)
        self.assertEqual(channel.created, 1640995200)
        self.assertEqual(channel.creator, 'U1234567890')
        self.assertFalse(channel.is_archived)
        self.assertTrue(channel.is_general)
        self.assertEqual(channel.name_normalized, 'general')
        self.assertFalse(channel.is_shared)
        self.assertTrue(channel.is_member)
        self.assertFalse(channel.is_private)

    def test_channel_minimal_data(self) -> None:
        """Test Channel with minimal required fields."""
        channel = slack_models.Channel(**MINIMAL_CHANNEL_DATA)

        self.assertEqual(channel.id, 'C1234567890')
        self.assertEqual(channel.name, '')
        self.assertIsNone(channel.is_channel)
        self.assertIsNone(channel.created)
        self.assertFalse(channel.is_archived)
        self.assertFalse(channel.is_org_shared)
        self.assertFalse(channel.is_im)
        self.assertEqual(channel.unread_count, 0)
        self.assertEqual(channel.unread_count_display, 0)


class TestFile(unittest.TestCase):
    """Test File model."""

    def test_file_full_data(self) -> None:
        """Test File with all fields."""
        file = slack_models.File(**FILE_DATA)

        self.assertEqual(file.id, 'F1234567890')
        self.assertEqual(file.name, 'example.txt')
        self.assertEqual(file.title, 'Example File')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file.size, 1024)
        self.assertEqual(file.mode, 'hosted')
        self.assertEqual(
            file.url_private,
            'https://files.slack.com/files-pri/T1234567890-F1234567890/example.txt',
        )
        self.assertEqual(
            file.url_private_download,
            'https://files.slack.com/files-pri/T1234567890-F1234567890/download/example.txt',
        )

    def test_file_minimal_data(self) -> None:
        """Test File with minimal required fields."""
        file = slack_models.File(**MINIMAL_FILE_DATA)

        self.assertEqual(file.id, 'F1234567890')
        self.assertEqual(file.name, 'example.txt')
        self.assertEqual(file.title, 'Example File')
        self.assertEqual(file.mimetype, 'text/plain')
        self.assertEqual(file.size, 1024)
        self.assertEqual(file.mode, 'hosted')
        self.assertEqual(
            file.url_private,
            'https://files.slack.com/files-pri/T1234567890-F1234567890/example.txt',
        )
        self.assertIsNone(file.url_private_download)

    def test_file_extra_fields_ignored(self) -> None:
        """Test File ignores extra fields due to extra='ignore'."""
        file_data = {**FILE_DATA, 'extra_field': 'ignored'}
        file = slack_models.File(**file_data)

        self.assertEqual(file.id, 'F1234567890')
        self.assertFalse(hasattr(file, 'extra_field'))


class TestFileContent(unittest.TestCase):
    """Test FileContent model."""

    def test_file_content_string(self) -> None:
        """Test FileContent with string content."""
        file_content = slack_models.FileContent(**FILE_CONTENT_DATA)

        self.assertEqual(file_content.mimetype, 'text/plain')
        self.assertEqual(file_content.content, 'Hello, world!')

    def test_file_content_bytes(self) -> None:
        """Test FileContent with bytes content."""
        file_content = slack_models.FileContent(
            mimetype='image/png', content=b'\\x89PNG\\r\\n\\x1a\\n'
        )

        self.assertEqual(file_content.mimetype, 'image/png')
        self.assertEqual(file_content.content, b'\\x89PNG\\r\\n\\x1a\\n')


class TestChatMessage(unittest.TestCase):
    """Test ChatMessage model."""

    def test_chat_message_full_data(self) -> None:
        """Test ChatMessage with all fields."""
        chat_message = slack_models.ChatMessage(**CHAT_MESSAGE_DATA)

        self.assertIsInstance(chat_message.user, slack_models.User)
        self.assertEqual(chat_message.content, 'Hello, world!')
        self.assertEqual(len(chat_message.files), 1)
        self.assertIsInstance(chat_message.files[0], slack_models.File)
        self.assertEqual(chat_message.ts, '1640995200.000100')
        self.assertEqual(chat_message.thread_ts, '1640995200.000100')
        self.assertIsInstance(chat_message.timestamp, datetime.datetime)

    def test_chat_message_minimal_data(self) -> None:
        """Test ChatMessage with minimal required fields."""
        chat_message = slack_models.ChatMessage(
            user=slack_models.User(id='U1234567890'),
            content='Hello!',
            ts='1640995200.000100',
            thread_ts='1640995200.000100',
            timestamp=datetime.datetime.fromtimestamp(
                1640995200, tz=datetime.UTC
            ),
        )

        self.assertEqual(chat_message.user.id, 'U1234567890')
        self.assertEqual(chat_message.content, 'Hello!')
        self.assertIsNone(chat_message.files)


class TestReaction(unittest.TestCase):
    """Test Reaction model."""

    def test_reaction_data(self) -> None:
        """Test Reaction with all fields."""
        reaction = slack_models.Reaction(**REACTION_DATA)

        self.assertEqual(reaction.name, 'thumbsup')
        self.assertEqual(reaction.count, 2)
        self.assertEqual(reaction.users, ['U1234567890', 'U0987654321'])

    def test_reaction_minimal_data(self) -> None:
        """Test Reaction with minimal data."""
        reaction = slack_models.Reaction(
            name='heart', count=1, users=['U1234567890']
        )

        self.assertEqual(reaction.name, 'heart')
        self.assertEqual(reaction.count, 1)
        self.assertEqual(reaction.users, ['U1234567890'])


class TestMessageItem(unittest.TestCase):
    """Test MessageItem model."""

    def test_message_item_full_data(self) -> None:
        """Test MessageItem with all fields."""
        message_item = slack_models.MessageItem(**MESSAGE_ITEM_DATA)

        self.assertEqual(message_item.type, 'message')
        self.assertEqual(message_item.channel, 'C1234567890')
        self.assertEqual(message_item.ts, '1640995200.000100')
        self.assertEqual(message_item.thread_ts, '1640995200.000100')

    def test_message_item_minimal_data(self) -> None:
        """Test MessageItem with minimal required fields."""
        message_item = slack_models.MessageItem(
            channel='C1234567890', ts='1640995200.000100'
        )

        self.assertEqual(message_item.type, 'message')  # default value
        self.assertEqual(message_item.channel, 'C1234567890')
        self.assertEqual(message_item.ts, '1640995200.000100')
        self.assertIsNone(message_item.thread_ts)


class TestMessageEdited(unittest.TestCase):
    """Test MessageEdited model."""

    def test_message_edited_data(self) -> None:
        """Test MessageEdited with all fields."""
        message_edited = slack_models.MessageEdited(**MESSAGE_EDITED_DATA)

        self.assertEqual(message_edited.user, 'U1234567890')
        self.assertEqual(message_edited.ts, '1640995200.000200')


class TestAuthorization(unittest.TestCase):
    """Test Authorization model."""

    def test_authorization_full_data(self) -> None:
        """Test Authorization with all fields."""
        authorization = slack_models.Authorization(**AUTHORIZATION_DATA)

        self.assertEqual(authorization.enterprise_id, 'E1234567890')
        self.assertEqual(authorization.team_id, 'T1234567890')
        self.assertEqual(authorization.user_id, 'U1234567890')
        self.assertFalse(authorization.is_bot)
        self.assertFalse(authorization.is_enterprise_install)

    def test_authorization_minimal_data(self) -> None:
        """Test Authorization with minimal required fields."""
        authorization = slack_models.Authorization(
            **MINIMAL_AUTHORIZATION_DATA
        )

        self.assertIsNone(authorization.enterprise_id)
        self.assertEqual(authorization.team_id, 'T1234567890')
        self.assertEqual(authorization.user_id, 'U1234567890')
        self.assertFalse(authorization.is_bot)
        self.assertFalse(authorization.is_enterprise_install)

    def test_authorization_enterprise_install(self) -> None:
        """Test Authorization with enterprise install."""
        authorization = slack_models.Authorization(
            enterprise_id='E1234567890',
            team_id='T1234567890',
            user_id='U1234567890',
            is_bot=True,
            is_enterprise_install=True,
        )

        self.assertEqual(authorization.enterprise_id, 'E1234567890')
        self.assertTrue(authorization.is_bot)
        self.assertTrue(authorization.is_enterprise_install)


class TestBaseSlackEvent(unittest.TestCase):
    """Test BaseSlackEvent model."""

    def test_base_slack_event_full_data(self) -> None:
        """Test BaseSlackEvent with all fields."""
        event = slack_models.BaseSlackEvent(
            type='test_event',
            ts='1640995200.000100',
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'test_event')
        self.assertEqual(event.ts, '1640995200.000100')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_base_slack_event_minimal_data(self) -> None:
        """Test BaseSlackEvent with minimal required fields."""
        event = slack_models.BaseSlackEvent(type='test_event')

        self.assertEqual(event.type, 'test_event')
        self.assertIsNone(event.ts)
        self.assertIsNone(event.event_ts)


class TestValidation(unittest.TestCase):
    """Test model validation and error handling."""

    def test_user_missing_required_field(self) -> None:
        """Test User validation fails for missing required field."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.User()

    def test_channel_missing_required_field(self) -> None:
        """Test Channel validation fails for missing required field."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.Channel()

    def test_file_missing_required_fields(self) -> None:
        """Test File validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.File()

    def test_authorization_missing_required_fields(self) -> None:
        """Test Authorization validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.Authorization()

    def test_base_slack_event_missing_required_field(self) -> None:
        """Test BaseSlackEvent validation fails for missing required field."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.BaseSlackEvent()

    def test_enterprise_user_missing_required_fields(self) -> None:
        """Test EnterpriseUser validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.EnterpriseUser()

    def test_reaction_missing_required_fields(self) -> None:
        """Test Reaction validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.Reaction()

    def test_message_item_missing_required_fields(self) -> None:
        """Test MessageItem validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.MessageItem()

    def test_message_edited_missing_required_fields(self) -> None:
        """Test MessageEdited validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.MessageEdited()

    def test_file_content_missing_required_fields(self) -> None:
        """Test FileContent validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.FileContent()

    def test_chat_message_missing_required_fields(self) -> None:
        """Test ChatMessage validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ChatMessage()

    def test_invalid_data_types(self) -> None:
        """Test validation fails for invalid data types."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.User(id=123)  # should be string

        with self.assertRaises(pydantic.ValidationError):
            slack_models.Channel(
                id='C1234567890', created='invalid'
            )  # should be int

        with self.assertRaises(pydantic.ValidationError):
            slack_models.File(
                id='F1234567890',
                name='test.txt',
                title='Test',
                mimetype='text/plain',
                size='invalid',  # should be int
                mode='hosted',
                url_private='https://example.com',
            )


if __name__ == '__main__':
    unittest.main()
