"""Comprehensive tests for all slack-models webhook payload classes."""

import unittest

import pydantic

import slack_models

from .test_data import (
    MINIMAL_SLACK_EVENT_CALLBACK_DATA,
    SLACK_APP_RATE_LIMITED_DATA,
    SLACK_EVENT_CALLBACK_DATA,
    SLACK_URL_VERIFICATION_DATA,
)


class TestSlackEventCallback(unittest.TestCase):
    """Test SlackEventCallback model."""

    def test_slack_event_callback_full_data(self) -> None:
        """Test SlackEventCallback with all fields."""
        callback = slack_models.SlackEventCallback(**SLACK_EVENT_CALLBACK_DATA)

        self.assertEqual(callback.token, 'verification_token')
        self.assertEqual(callback.team_id, 'T1234567890')
        self.assertEqual(callback.api_app_id, 'A1234567890')
        self.assertIsInstance(callback.event, slack_models.MessageEvent)
        self.assertEqual(callback.event.type, 'message')
        self.assertEqual(callback.event.channel, 'C1234567890')
        self.assertEqual(callback.event.user, 'U1234567890')
        self.assertEqual(callback.event.text, 'Hello, world!')
        self.assertEqual(callback.type, 'event_callback')
        self.assertEqual(callback.event_id, 'Ev1234567890')
        self.assertEqual(callback.event_time, 1640995200)
        self.assertEqual(callback.event_context, 'EC1234567890')
        self.assertEqual(len(callback.authorizations), 1)
        self.assertIsInstance(
            callback.authorizations[0], slack_models.Authorization
        )

    def test_slack_event_callback_minimal_data(self) -> None:
        """Test SlackEventCallback with minimal required fields."""
        callback = slack_models.SlackEventCallback(
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA
        )

        self.assertEqual(callback.token, 'verification_token')
        self.assertEqual(callback.team_id, 'T1234567890')
        self.assertEqual(callback.api_app_id, 'A1234567890')
        self.assertIsInstance(callback.event, slack_models.MessageEvent)
        self.assertEqual(callback.type, 'event_callback')
        self.assertEqual(callback.event_id, 'Ev1234567890')
        self.assertEqual(callback.event_time, 1640995200)
        self.assertIsNone(callback.event_context)
        self.assertIsNone(callback.authorizations)

    def test_slack_event_callback_different_event_types(self) -> None:
        """Test SlackEventCallback with different event types."""
        # Test with AppMentionEvent
        callback_data = {
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA,
            'event': {
                'type': 'app_mention',
                'channel': 'C1234567890',
                'user': 'U1234567890',
                'text': '<@U0987654321> Hello!',
                'ts': '1640995200.000100',
                'event_ts': '1640995200.000100',
            },
        }
        callback = slack_models.SlackEventCallback(**callback_data)

        self.assertIsInstance(callback.event, slack_models.AppMentionEvent)
        self.assertEqual(callback.event.type, 'app_mention')
        self.assertEqual(callback.event.text, '<@U0987654321> Hello!')

        # Test with ReactionAddedEvent
        callback_data = {
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA,
            'event': {
                'type': 'reaction_added',
                'user': 'U1234567890',
                'reaction': 'thumbsup',
                'item': {
                    'type': 'message',
                    'channel': 'C1234567890',
                    'ts': '1640995200.000100',
                },
                'event_ts': '1640995200.000100',
            },
        }
        callback = slack_models.SlackEventCallback(**callback_data)

        self.assertIsInstance(callback.event, slack_models.ReactionAddedEvent)
        self.assertEqual(callback.event.type, 'reaction_added')
        self.assertEqual(callback.event.reaction, 'thumbsup')

    def test_slack_event_callback_extra_fields_allowed(self) -> None:
        """Test SlackEventCallback allows extra fields."""
        callback_data = {
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA,
            'extra_field': 'extra_value',
            'another_field': 123,
        }
        callback = slack_models.SlackEventCallback(**callback_data)

        self.assertEqual(callback.token, 'verification_token')
        # Note: extra fields are allowed but not accessible as attributes
        # due to extra='allow' configuration

    def test_slack_event_callback_missing_required_fields(self) -> None:
        """Test SlackEventCallback validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback()

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback(token='verification_token')  # noqa: S106

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback(
                token='verification_token',  # noqa: S106
                team_id='T1234567890',
            )


class TestSlackUrlVerification(unittest.TestCase):
    """Test SlackUrlVerification model."""

    def test_slack_url_verification_full_data(self) -> None:
        """Test SlackUrlVerification with all fields."""
        verification = slack_models.SlackUrlVerification(
            **SLACK_URL_VERIFICATION_DATA
        )

        self.assertEqual(verification.token, 'verification_token')
        self.assertEqual(verification.challenge, 'challenge_string')
        self.assertEqual(verification.type, 'url_verification')

    def test_slack_url_verification_minimal_data(self) -> None:
        """Test SlackUrlVerification with minimal required fields."""
        verification = slack_models.SlackUrlVerification(
            token='verification_token',  # noqa: S106
            challenge='challenge_string',
            type='url_verification',
        )

        self.assertEqual(verification.token, 'verification_token')
        self.assertEqual(verification.challenge, 'challenge_string')
        self.assertEqual(verification.type, 'url_verification')

    def test_slack_url_verification_type_literal(self) -> None:
        """Test SlackUrlVerification type field is literal."""
        verification = slack_models.SlackUrlVerification(
            token='verification_token',  # noqa: S106
            challenge='challenge_string',
        )

        self.assertEqual(verification.type, 'url_verification')

    def test_slack_url_verification_missing_required_fields(self) -> None:
        """Test SlackUrlVerification validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackUrlVerification()

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackUrlVerification(token='verification_token')  # noqa: S106


class TestSlackAppRateLimited(unittest.TestCase):
    """Test SlackAppRateLimited model."""

    def test_slack_app_rate_limited_full_data(self) -> None:
        """Test SlackAppRateLimited with all fields."""
        rate_limited = slack_models.SlackAppRateLimited(
            **SLACK_APP_RATE_LIMITED_DATA
        )

        self.assertEqual(rate_limited.token, 'verification_token')
        self.assertEqual(rate_limited.team_id, 'T1234567890')
        self.assertEqual(rate_limited.minute_rate_limited, 30000)
        self.assertEqual(rate_limited.api_app_id, 'A1234567890')
        self.assertEqual(rate_limited.type, 'app_rate_limited')

    def test_slack_app_rate_limited_minimal_data(self) -> None:
        """Test SlackAppRateLimited with minimal required fields."""
        rate_limited = slack_models.SlackAppRateLimited(
            token='verification_token',  # noqa: S106
            team_id='T1234567890',
            minute_rate_limited=30000,
            api_app_id='A1234567890',
            type='app_rate_limited',
        )

        self.assertEqual(rate_limited.token, 'verification_token')
        self.assertEqual(rate_limited.team_id, 'T1234567890')
        self.assertEqual(rate_limited.minute_rate_limited, 30000)
        self.assertEqual(rate_limited.api_app_id, 'A1234567890')
        self.assertEqual(rate_limited.type, 'app_rate_limited')

    def test_slack_app_rate_limited_type_literal(self) -> None:
        """Test SlackAppRateLimited type field is literal."""
        rate_limited = slack_models.SlackAppRateLimited(
            token='verification_token',  # noqa: S106
            team_id='T1234567890',
            minute_rate_limited=30000,
            api_app_id='A1234567890',
        )

        self.assertEqual(rate_limited.type, 'app_rate_limited')

    def test_slack_app_rate_limited_missing_required_fields(self) -> None:
        """Test SlackAppRateLimited validation fails for missing fields."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackAppRateLimited()

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackAppRateLimited(token='verification_token')  # noqa: S106

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackAppRateLimited(
                token='verification_token',  # noqa: S106
                team_id='T1234567890',
            )


class TestWebhookPayloadValidation(unittest.TestCase):
    """Test webhook payload validation and error handling."""

    def test_invalid_event_type_in_callback(self) -> None:
        """Test SlackEventCallback with invalid event type."""
        callback_data = {
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA,
            'event': {
                'type': 'invalid_event_type',
                'channel': 'C1234567890',
                'user': 'U1234567890',
                'text': 'Hello, world!',
                'ts': '1640995200.000100',
            },
        }

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback(**callback_data)

    def test_missing_required_event_fields(self) -> None:
        """Test SlackEventCallback with missing required event fields."""
        callback_data = {
            **MINIMAL_SLACK_EVENT_CALLBACK_DATA,
            'event': {
                'type': 'message',
                'channel': 'C1234567890',
                # Missing required 'user', 'text', 'ts' fields
            },
        }

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback(**callback_data)

    def test_invalid_data_types_in_webhooks(self) -> None:
        """Test webhook validation fails for invalid data types."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackEventCallback(
                token='verification_token',  # noqa: S106
                team_id='T1234567890',
                api_app_id='A1234567890',
                event=MINIMAL_SLACK_EVENT_CALLBACK_DATA['event'],
                type='event_callback',
                event_id='Ev1234567890',
                event_time='invalid_timestamp',  # should be int
            )

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackAppRateLimited(
                token='verification_token',  # noqa: S106
                team_id='T1234567890',
                minute_rate_limited='invalid_number',  # should be int
                api_app_id='A1234567890',
                type='app_rate_limited',
            )

    def test_wrong_type_literal_values(self) -> None:
        """Test webhook validation fails for wrong type literal values."""
        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackUrlVerification(
                token='verification_token',  # noqa: S106
                challenge='challenge_string',
                type='wrong_type',  # should be 'url_verification'
            )

        with self.assertRaises(pydantic.ValidationError):
            slack_models.SlackAppRateLimited(
                token='verification_token',  # noqa: S106
                team_id='T1234567890',
                minute_rate_limited=30000,
                api_app_id='A1234567890',
                type='wrong_type',  # should be 'app_rate_limited'
            )


if __name__ == '__main__':
    unittest.main()
