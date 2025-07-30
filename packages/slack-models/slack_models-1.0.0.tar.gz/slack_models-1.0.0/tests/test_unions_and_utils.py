"""Tests for union types, EVENT_MAP, and utility functions."""

import unittest
from typing import get_args

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
    REACTION_ADDED_EVENT_DATA,
    REACTION_REMOVED_EVENT_DATA,
    SLACK_APP_RATE_LIMITED_DATA,
    SLACK_EVENT_CALLBACK_DATA,
    SLACK_URL_VERIFICATION_DATA,
    TEAM_JOIN_EVENT_DATA,
)


class TestSlackEventUnion(unittest.TestCase):
    """Test SlackEvent union type."""

    def test_slack_event_union_includes_all_event_types(self) -> None:
        """Test SlackEvent union includes all event model types."""
        event_types = get_args(slack_models.SlackEvent)

        expected_types = {
            slack_models.MessageEvent,
            slack_models.AppMentionEvent,
            slack_models.ReactionAddedEvent,
            slack_models.ReactionRemovedEvent,
            slack_models.TeamJoinEvent,
            slack_models.FileCreatedEvent,
            slack_models.FileDeletedEvent,
            slack_models.ChannelCreatedEvent,
            slack_models.ChannelDeletedEvent,
            slack_models.ChannelRenameEvent,
        }

        self.assertEqual(set(event_types), expected_types)

    def test_slack_event_union_accepts_all_event_types(self) -> None:
        """Test SlackEvent union accepts all event model instances."""
        # Test with MessageEvent
        message_event = slack_models.MessageEvent(**MESSAGE_EVENT_DATA)
        self.assertIsInstance(message_event, slack_models.MessageEvent)

        # Test with AppMentionEvent
        app_mention_event = slack_models.AppMentionEvent(
            **APP_MENTION_EVENT_DATA
        )
        self.assertIsInstance(app_mention_event, slack_models.AppMentionEvent)

        # Test with ReactionAddedEvent
        reaction_added_event = slack_models.ReactionAddedEvent(
            **REACTION_ADDED_EVENT_DATA
        )
        self.assertIsInstance(
            reaction_added_event, slack_models.ReactionAddedEvent
        )

        # Test with ReactionRemovedEvent
        reaction_removed_event = slack_models.ReactionRemovedEvent(
            **REACTION_REMOVED_EVENT_DATA
        )
        self.assertIsInstance(
            reaction_removed_event, slack_models.ReactionRemovedEvent
        )

        # Test with TeamJoinEvent
        team_join_event = slack_models.TeamJoinEvent(**TEAM_JOIN_EVENT_DATA)
        self.assertIsInstance(team_join_event, slack_models.TeamJoinEvent)

        # Test with FileCreatedEvent
        file_created_event = slack_models.FileCreatedEvent(
            **FILE_CREATED_EVENT_DATA
        )
        self.assertIsInstance(
            file_created_event, slack_models.FileCreatedEvent
        )

        # Test with FileDeletedEvent
        file_deleted_event = slack_models.FileDeletedEvent(
            **FILE_DELETED_EVENT_DATA
        )
        self.assertIsInstance(
            file_deleted_event, slack_models.FileDeletedEvent
        )

        # Test with ChannelCreatedEvent
        channel_created_event = slack_models.ChannelCreatedEvent(
            **CHANNEL_CREATED_EVENT_DATA
        )
        self.assertIsInstance(
            channel_created_event, slack_models.ChannelCreatedEvent
        )

        # Test with ChannelDeletedEvent
        channel_deleted_event = slack_models.ChannelDeletedEvent(
            **CHANNEL_DELETED_EVENT_DATA
        )
        self.assertIsInstance(
            channel_deleted_event, slack_models.ChannelDeletedEvent
        )

        # Test with ChannelRenameEvent
        channel_rename_event = slack_models.ChannelRenameEvent(
            **CHANNEL_RENAME_EVENT_DATA
        )
        self.assertIsInstance(
            channel_rename_event, slack_models.ChannelRenameEvent
        )


class TestSlackWebhookPayloadUnion(unittest.TestCase):
    """Test SlackWebhookPayload union type."""

    def test_slack_webhook_payload_union_includes_all_webhook_types(
        self,
    ) -> None:
        """Test SlackWebhookPayload union includes all webhook model types."""
        webhook_types = get_args(slack_models.SlackWebhookPayload)

        expected_types = {
            slack_models.SlackEventCallback,
            slack_models.SlackUrlVerification,
            slack_models.SlackAppRateLimited,
        }

        self.assertEqual(set(webhook_types), expected_types)

    def test_slack_webhook_payload_union_accepts_all_webhook_types(
        self,
    ) -> None:
        """Test SlackWebhookPayload union accepts all webhook types."""
        # Test with SlackEventCallback
        event_callback = slack_models.SlackEventCallback(
            **SLACK_EVENT_CALLBACK_DATA
        )
        self.assertIsInstance(event_callback, slack_models.SlackEventCallback)

        # Test with SlackUrlVerification
        url_verification = slack_models.SlackUrlVerification(
            **SLACK_URL_VERIFICATION_DATA
        )
        self.assertIsInstance(
            url_verification, slack_models.SlackUrlVerification
        )

        # Test with SlackAppRateLimited
        rate_limited = slack_models.SlackAppRateLimited(
            **SLACK_APP_RATE_LIMITED_DATA
        )
        self.assertIsInstance(rate_limited, slack_models.SlackAppRateLimited)


class TestEventMap(unittest.TestCase):
    """Test EVENT_MAP dictionary."""

    def test_event_map_contains_all_event_types(self) -> None:
        """Test EVENT_MAP contains all event types."""
        expected_mappings = {
            'message': slack_models.MessageEvent,
            'app_mention': slack_models.AppMentionEvent,
            'reaction_added': slack_models.ReactionAddedEvent,
            'reaction_removed': slack_models.ReactionRemovedEvent,
            'team_join': slack_models.TeamJoinEvent,
            'file_created': slack_models.FileCreatedEvent,
            'file_deleted': slack_models.FileDeletedEvent,
            'channel_created': slack_models.ChannelCreatedEvent,
            'channel_deleted': slack_models.ChannelDeletedEvent,
            'channel_rename': slack_models.ChannelRenameEvent,
        }

        self.assertEqual(slack_models.EVENT_MAP, expected_mappings)

    def test_event_map_keys_match_event_type_literals(self) -> None:
        """Test EVENT_MAP keys match event type literals."""
        # Test that each key in EVENT_MAP matches the type literal
        for _event_type, event_class in slack_models.EVENT_MAP.items():
            # Create an instance and check its type field
            if _event_type == 'message':
                instance = event_class(
                    type=_event_type,
                    channel='C1234567890',
                    user='U1234567890',
                    text='Hello!',
                    ts='1640995200.000100',
                )
            elif _event_type == 'app_mention':
                instance = event_class(
                    type=_event_type,
                    channel='C1234567890',
                    user='U1234567890',
                    text='<@U0987654321> Hello!',
                    ts='1640995200.000100',
                    event_ts='1640995200.000100',
                )
            elif _event_type in ['reaction_added', 'reaction_removed']:
                instance = event_class(
                    type=_event_type,
                    user='U1234567890',
                    reaction='thumbsup',
                    item=slack_models.MessageItem(
                        channel='C1234567890', ts='1640995200.000100'
                    ),
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'team_join':
                instance = event_class(
                    type=_event_type,
                    user={'id': 'U1234567890', 'name': 'john.doe'},
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'file_created':
                instance = event_class(
                    type=_event_type,
                    file_id='F1234567890',
                    file={'id': 'F1234567890', 'name': 'test.txt'},
                    user_id='U1234567890',
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'file_deleted':
                instance = event_class(
                    type=_event_type,
                    file_id='F1234567890',
                    user_id='U1234567890',
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'channel_created':
                instance = event_class(
                    type=_event_type,
                    channel={'id': 'C1234567890', 'name': 'general'},
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'channel_deleted':
                instance = event_class(
                    type=_event_type,
                    channel='C1234567890',
                    event_ts='1640995200.000100',
                )
            elif _event_type == 'channel_rename':
                instance = event_class(
                    type=_event_type,
                    channel={'id': 'C1234567890', 'name': 'new-name'},
                    event_ts='1640995200.000100',
                )

            self.assertEqual(instance.type, _event_type)

    def test_event_map_values_are_event_classes(self) -> None:
        """Test EVENT_MAP values are event classes."""
        for _event_type, event_class in slack_models.EVENT_MAP.items():
            self.assertTrue(
                issubclass(event_class, slack_models.BaseSlackEvent)
            )
            self.assertTrue(hasattr(event_class, 'model_validate'))


class TestParseEventFunction(unittest.TestCase):
    """Test parse_event utility function."""

    def test_parse_event_message_event(self) -> None:
        """Test parse_event with MessageEvent."""
        event = slack_models.parse_event(MESSAGE_EVENT_DATA)

        self.assertIsInstance(event, slack_models.MessageEvent)
        self.assertEqual(event.type, 'message')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, 'Hello, world!')

    def test_parse_event_app_mention_event(self) -> None:
        """Test parse_event with AppMentionEvent."""
        event = slack_models.parse_event(APP_MENTION_EVENT_DATA)

        self.assertIsInstance(event, slack_models.AppMentionEvent)
        self.assertEqual(event.type, 'app_mention')
        self.assertEqual(event.channel, 'C1234567890')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.text, '<@U0987654321> Hello!')

    def test_parse_event_reaction_added_event(self) -> None:
        """Test parse_event with ReactionAddedEvent."""
        event = slack_models.parse_event(REACTION_ADDED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.ReactionAddedEvent)
        self.assertEqual(event.type, 'reaction_added')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)

    def test_parse_event_reaction_removed_event(self) -> None:
        """Test parse_event with ReactionRemovedEvent."""
        event = slack_models.parse_event(REACTION_REMOVED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.ReactionRemovedEvent)
        self.assertEqual(event.type, 'reaction_removed')
        self.assertEqual(event.user, 'U1234567890')
        self.assertEqual(event.reaction, 'thumbsup')
        self.assertIsInstance(event.item, slack_models.MessageItem)

    def test_parse_event_team_join_event(self) -> None:
        """Test parse_event with TeamJoinEvent."""
        event = slack_models.parse_event(TEAM_JOIN_EVENT_DATA)

        self.assertIsInstance(event, slack_models.TeamJoinEvent)
        self.assertEqual(event.type, 'team_join')
        self.assertIsInstance(event.user, slack_models.User)
        self.assertEqual(event.user.id, 'U1234567890')

    def test_parse_event_file_created_event(self) -> None:
        """Test parse_event with FileCreatedEvent."""
        event = slack_models.parse_event(FILE_CREATED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.FileCreatedEvent)
        self.assertEqual(event.type, 'file_created')
        self.assertEqual(event.file_id, 'F1234567890')
        self.assertIsInstance(event.file, dict)
        self.assertEqual(event.file['id'], 'F1234567890')

    def test_parse_event_file_deleted_event(self) -> None:
        """Test parse_event with FileDeletedEvent."""
        event = slack_models.parse_event(FILE_DELETED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.FileDeletedEvent)
        self.assertEqual(event.type, 'file_deleted')
        self.assertEqual(event.file_id, 'F1234567890')

    def test_parse_event_channel_created_event(self) -> None:
        """Test parse_event with ChannelCreatedEvent."""
        event = slack_models.parse_event(CHANNEL_CREATED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.ChannelCreatedEvent)
        self.assertEqual(event.type, 'channel_created')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')

    def test_parse_event_channel_deleted_event(self) -> None:
        """Test parse_event with ChannelDeletedEvent."""
        event = slack_models.parse_event(CHANNEL_DELETED_EVENT_DATA)

        self.assertIsInstance(event, slack_models.ChannelDeletedEvent)
        self.assertEqual(event.type, 'channel_deleted')
        self.assertEqual(event.channel, 'C1234567890')

    def test_parse_event_channel_rename_event(self) -> None:
        """Test parse_event with ChannelRenameEvent."""
        event = slack_models.parse_event(CHANNEL_RENAME_EVENT_DATA)

        self.assertIsInstance(event, slack_models.ChannelRenameEvent)
        self.assertEqual(event.type, 'channel_rename')
        self.assertIsInstance(event.channel, dict)
        self.assertEqual(event.channel['id'], 'C1234567890')

    def test_parse_event_unknown_event_type(self) -> None:
        """Test parse_event raises ValueError for unknown event type."""
        with self.assertRaises(ValueError) as context:
            slack_models.parse_event({'type': 'unknown_event'})

        self.assertIn(
            'Unknown event type: unknown_event', str(context.exception)
        )

    def test_parse_event_missing_type_field(self) -> None:
        """Test parse_event raises ValueError for missing type field."""
        with self.assertRaises(ValueError) as context:
            slack_models.parse_event({'channel': 'C1234567890'})

        self.assertIn('Event type is missing', str(context.exception))

    def test_parse_event_validation_error(self) -> None:
        """Test parse_event raises ValidationError for invalid event data."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.parse_event(
                {
                    'type': 'message',
                    'channel': 'C1234567890',
                    # Missing required fields: user, text, ts
                }
            )

    def test_parse_event_with_extra_fields(self) -> None:
        """Test parse_event ignores extra fields in event data."""
        event_data = {
            **MESSAGE_EVENT_DATA,
            'extra_field': 'extra_value',
            'another_field': 123,
        }

        event = slack_models.parse_event(event_data)

        self.assertIsInstance(event, slack_models.MessageEvent)
        self.assertEqual(event.type, 'message')
        self.assertEqual(event.channel, 'C1234567890')
        # Extra fields should be ignored
        self.assertFalse(hasattr(event, 'extra_field'))
        self.assertFalse(hasattr(event, 'another_field'))


if __name__ == '__main__':
    unittest.main()
