"""Comprehensive tests for all slack-models event classes."""

import unittest

import pydantic

import slack_models

from .test_data import (
    APP_MENTION_EVENT_DATA,
    CHANNEL_CREATED_EVENT_DATA,
    CHANNEL_DELETED_EVENT_DATA,
    CHANNEL_RENAME_EVENT_DATA,
    FILE_CREATED_EVENT_DATA,
    FILE_DELETED_EVENT_DATA,
    MESSAGE_EVENT_DATA,
    MINIMAL_MESSAGE_EVENT_DATA,
    REACTION_ADDED_EVENT_DATA,
    REACTION_REMOVED_EVENT_DATA,
    TEAM_JOIN_EVENT_DATA,
)


class TestMessageEvent(unittest.TestCase):
    """Test MessageEvent model."""

    def test_message_event_full_data(self) -> None:
        """Test MessageEvent with all fields."""
        event = slack_models.MessageEvent(**MESSAGE_EVENT_DATA)

        self.assertEqual(event.type, 'message')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, 'Hello, world!')
        self.assertEqual(event.ts, '1640995200.000100')
        self.assertEqual(event.thread_ts, '1640995200.000100')
        self.assertIsNone(event.subtype)
        self.assertIsInstance(event.edited, slack_models.MessageEdited)
        self.assertEqual(len(event.files), 1)
        self.assertIsInstance(event.files[0], slack_models.File)
        self.assertEqual(len(event.reactions), 1)
        self.assertIsInstance(event.reactions[0], slack_models.Reaction)
        self.assertFalse(event.is_starred)
        self.assertEqual(event.pinned_to, ['C1234567890'])
        self.assertEqual(event.reply_count, 5)
        self.assertEqual(event.reply_users, ['U1234567890', 'U0987654321'])
        self.assertEqual(event.reply_users_count, 2)
        self.assertEqual(event.latest_reply, '1640995200.000200')
        self.assertFalse(event.hidden)
        self.assertIsNone(event.deleted_ts)

    def test_message_event_minimal_data(self) -> None:
        """Test MessageEvent with minimal required fields."""
        event = slack_models.MessageEvent(**MINIMAL_MESSAGE_EVENT_DATA)

        self.assertEqual(event.type, 'message')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, 'Hello, world!')
        self.assertEqual(event.ts, '1640995200.000100')
        self.assertIsNone(event.thread_ts)
        self.assertIsNone(event.subtype)
        self.assertIsNone(event.edited)
        self.assertIsNone(event.files)
        self.assertIsNone(event.reactions)
        self.assertIsNone(event.is_starred)
        self.assertIsNone(event.pinned_to)
        self.assertIsNone(event.reply_count)
        self.assertIsNone(event.reply_users)
        self.assertIsNone(event.reply_users_count)
        self.assertIsNone(event.latest_reply)
        self.assertIsNone(event.hidden)
        self.assertIsNone(event.deleted_ts)

    def test_message_event_with_subtype(self) -> None:
        """Test MessageEvent with subtype."""
        event = slack_models.MessageEvent(
            type='message',
            channel='C1234567890',
            user='U1234567890',
            text='Hello, world!',
            ts='1640995200.000100',
            subtype='bot_message',
        )

        self.assertEqual(event.subtype, 'bot_message')

    def test_message_event_missing_required_fields(self) -> None:
        """Test MessageEvent validation fails for missing required fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.MessageEvent()

        with self.assertRaises(pydantic.ValidationError):
            slack_models.MessageEvent(type='message')

        with self.assertRaises(pydantic.ValidationError):
            slack_models.MessageEvent(type='message', channel='C1234567890')


class TestAppMentionEvent(unittest.TestCase):
    """Test AppMentionEvent model."""

    def test_app_mention_event_full_data(self) -> None:
        """Test AppMentionEvent with all fields."""
        event = slack_models.AppMentionEvent(**APP_MENTION_EVENT_DATA)

        self.assertEqual(event.type, 'app_mention')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, '<@U0987654321> Hello!')
        self.assertEqual(event.ts, '1640995200.000100')
        self.assertEqual(event.thread_ts, '1640995200.000100')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_app_mention_event_minimal_data(self) -> None:
        """Test AppMentionEvent with minimal required fields."""
        event = slack_models.AppMentionEvent(
            type='app_mention',
            channel='C1234567890',
            user='U1234567890',
            text='<@U0987654321> Hello!',
            ts='1640995200.000100',
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'app_mention')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, '<@U0987654321> Hello!')
        self.assertEqual(event.ts, '1640995200.000100')
        self.assertIsNone(event.thread_ts)
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_app_mention_event_missing_required_fields(self) -> None:
        """Test AppMentionEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.AppMentionEvent()


class TestReactionAddedEvent(unittest.TestCase):
    """Test ReactionAddedEvent model."""

    def test_reaction_added_event_full_data(self) -> None:
        """Test ReactionAddedEvent with all fields."""
        event = slack_models.ReactionAddedEvent(**REACTION_ADDED_EVENT_DATA)

        self.assertEqual(event.type, 'reaction_added')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)
        self.assertEqual(event.item.channel, 'C1234567890')
        self.assertEqual(event.item.ts, '1640995200.000100')
        self.assertEqual(event.item_user, 'U0987654321')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_reaction_added_event_minimal_data(self) -> None:
        """Test ReactionAddedEvent with minimal required fields."""
        event = slack_models.ReactionAddedEvent(
            type='reaction_added',
            user='U1234567890',
            reaction='thumbsup',
            item=slack_models.MessageItem(
                channel='C1234567890', ts='1640995200.000100'
            ),
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'reaction_added')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)
        self.assertIsNone(event.item_user)
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_reaction_added_event_missing_required_fields(self) -> None:
        """Test ReactionAddedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ReactionAddedEvent()


class TestReactionRemovedEvent(unittest.TestCase):
    """Test ReactionRemovedEvent model."""

    def test_reaction_removed_event_full_data(self) -> None:
        """Test ReactionRemovedEvent with all fields."""
        event = slack_models.ReactionRemovedEvent(
            **REACTION_REMOVED_EVENT_DATA
        )

        self.assertEqual(event.type, 'reaction_removed')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)
        self.assertEqual(event.item.channel, 'C1234567890')
        self.assertEqual(event.item.ts, '1640995200.000100')
        self.assertEqual(event.item_user, 'U0987654321')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_reaction_removed_event_minimal_data(self) -> None:
        """Test ReactionRemovedEvent with minimal required fields."""
        event = slack_models.ReactionRemovedEvent(
            type='reaction_removed',
            user='U1234567890',
            reaction='thumbsup',
            item=slack_models.MessageItem(
                channel='C1234567890', ts='1640995200.000100'
            ),
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'reaction_removed')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)
        self.assertIsNone(event.item_user)
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_reaction_removed_event_missing_required_fields(self) -> None:
        """Test ReactionRemovedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ReactionRemovedEvent()


class TestTeamJoinEvent(unittest.TestCase):
    """Test TeamJoinEvent model."""

    def test_team_join_event_full_data(self) -> None:
        """Test TeamJoinEvent with all fields."""
        event = slack_models.TeamJoinEvent(**TEAM_JOIN_EVENT_DATA)

        self.assertEqual(event.type, 'team_join')
        self.assertIsInstance(event.user, slack_models.User)
        self.assertEqual(event.user.id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_team_join_event_minimal_data(self) -> None:
        """Test TeamJoinEvent with minimal required fields."""
        event = slack_models.TeamJoinEvent(
            type='team_join',
            user={'id': 'U1234567890', 'name': 'john.doe'},
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'team_join')
        self.assertIsInstance(event.user, slack_models.User)
        self.assertEqual(event.user.id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_team_join_event_missing_required_fields(self) -> None:
        """Test TeamJoinEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.TeamJoinEvent()


class TestFileCreatedEvent(unittest.TestCase):
    """Test FileCreatedEvent model."""

    def test_file_created_event_full_data(self) -> None:
        """Test FileCreatedEvent with all fields."""
        event = slack_models.FileCreatedEvent(**FILE_CREATED_EVENT_DATA)

        self.assertEqual(event.type, 'file_created')
        self.assertEqual(event.file_id, 'F1234567890')
        self.assertIsInstance(event.file, dict)
        self.assertEqual(event.file['id'], 'F1234567890')
        self.assertEqual(event.user_id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_file_created_event_minimal_data(self) -> None:
        """Test FileCreatedEvent with minimal required fields."""
        event = slack_models.FileCreatedEvent(
            type='file_created',
            file_id='F1234567890',
            file={'id': 'F1234567890', 'name': 'test.txt'},
            user_id='U1234567890',
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'file_created')
        self.assertEqual(event.file_id, 'F1234567890')
        self.assertIsInstance(event.file, dict)
        self.assertEqual(event.file['id'], 'F1234567890')
        self.assertEqual(event.user_id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_file_created_event_missing_required_fields(self) -> None:
        """Test FileCreatedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.FileCreatedEvent()


class TestFileDeletedEvent(unittest.TestCase):
    """Test FileDeletedEvent model."""

    def test_file_deleted_event_full_data(self) -> None:
        """Test FileDeletedEvent with all fields."""
        event = slack_models.FileDeletedEvent(**FILE_DELETED_EVENT_DATA)

        self.assertEqual(event.type, 'file_deleted')
        self.assertEqual(event.file_id, 'F1234567890')
        self.assertEqual(event.user_id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_file_deleted_event_minimal_data(self) -> None:
        """Test FileDeletedEvent with minimal required fields."""
        event = slack_models.FileDeletedEvent(
            type='file_deleted',
            file_id='F1234567890',
            user_id='U1234567890',
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'file_deleted')
        self.assertEqual(event.file_id, 'F1234567890')
        self.assertEqual(event.user_id, 'U1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_file_deleted_event_missing_required_fields(self) -> None:
        """Test FileDeletedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.FileDeletedEvent()


class TestChannelCreatedEvent(unittest.TestCase):
    """Test ChannelCreatedEvent model."""

    def test_channel_created_event_full_data(self) -> None:
        """Test ChannelCreatedEvent with all fields."""
        event = slack_models.ChannelCreatedEvent(**CHANNEL_CREATED_EVENT_DATA)

        self.assertEqual(event.type, 'channel_created')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_created_event_minimal_data(self) -> None:
        """Test ChannelCreatedEvent with minimal required fields."""
        event = slack_models.ChannelCreatedEvent(
            type='channel_created',
            channel={'id': 'C1234567890', 'name': 'general'},
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'channel_created')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_created_event_missing_required_fields(self) -> None:
        """Test ChannelCreatedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ChannelCreatedEvent()


class TestChannelDeletedEvent(unittest.TestCase):
    """Test ChannelDeletedEvent model."""

    def test_channel_deleted_event_full_data(self) -> None:
        """Test ChannelDeletedEvent with all fields."""
        event = slack_models.ChannelDeletedEvent(**CHANNEL_DELETED_EVENT_DATA)

        self.assertEqual(event.type, 'channel_deleted')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_deleted_event_minimal_data(self) -> None:
        """Test ChannelDeletedEvent with minimal required fields."""
        event = slack_models.ChannelDeletedEvent(
            type='channel_deleted',
            channel='C1234567890',
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'channel_deleted')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_deleted_event_missing_required_fields(self) -> None:
        """Test ChannelDeletedEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ChannelDeletedEvent()


class TestChannelRenameEvent(unittest.TestCase):
    """Test ChannelRenameEvent model."""

    def test_channel_rename_event_full_data(self) -> None:
        """Test ChannelRenameEvent with all fields."""
        event = slack_models.ChannelRenameEvent(**CHANNEL_RENAME_EVENT_DATA)

        self.assertEqual(event.type, 'channel_rename')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_rename_event_minimal_data(self) -> None:
        """Test ChannelRenameEvent with minimal required fields."""
        event = slack_models.ChannelRenameEvent(
            type='channel_rename',
            channel={'id': 'C1234567890', 'name': 'new-name'},
            event_ts='1640995200.000100',
        )

        self.assertEqual(event.type, 'channel_rename')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')
        self.assertEqual(event.event_ts, '1640995200.000100')

    def test_channel_rename_event_missing_required_fields(self) -> None:
        """Test ChannelRenameEvent validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.ChannelRenameEvent()


class TestEventInheritance(unittest.TestCase):
    """Test that all event models inherit from BaseSlackEvent."""

    def test_message_event_inherits_from_base(self) -> None:
        """Test MessageEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(slack_models.MessageEvent, slack_models.BaseSlackEvent)
        )

    def test_app_mention_event_inherits_from_base(self) -> None:
        """Test AppMentionEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.AppMentionEvent, slack_models.BaseSlackEvent
            )
        )

    def test_reaction_added_event_inherits_from_base(self) -> None:
        """Test ReactionAddedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.ReactionAddedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_reaction_removed_event_inherits_from_base(self) -> None:
        """Test ReactionRemovedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.ReactionRemovedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_team_join_event_inherits_from_base(self) -> None:
        """Test TeamJoinEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(slack_models.TeamJoinEvent, slack_models.BaseSlackEvent)
        )

    def test_file_created_event_inherits_from_base(self) -> None:
        """Test FileCreatedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.FileCreatedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_file_deleted_event_inherits_from_base(self) -> None:
        """Test FileDeletedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.FileDeletedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_channel_created_event_inherits_from_base(self) -> None:
        """Test ChannelCreatedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.ChannelCreatedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_channel_deleted_event_inherits_from_base(self) -> None:
        """Test ChannelDeletedEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.ChannelDeletedEvent, slack_models.BaseSlackEvent
            )
        )

    def test_channel_rename_event_inherits_from_base(self) -> None:
        """Test ChannelRenameEvent inherits from BaseSlackEvent."""
        self.assertTrue(
            issubclass(
                slack_models.ChannelRenameEvent, slack_models.BaseSlackEvent
            )
        )


if __name__ == '__main__':
    unittest.main()
