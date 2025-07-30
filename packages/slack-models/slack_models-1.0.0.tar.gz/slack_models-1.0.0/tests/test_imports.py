"""Tests for top-level imports and __all__ exports."""

import unittest

import pydantic

import slack_models


class TestTopLevelImports(unittest.TestCase):
    """Test that all models and utilities are importable from slack_models."""

    def test_basic_model_imports(self) -> None:
        """Test basic model classes are importable."""
        self.assertTrue(hasattr(slack_models, 'Channel'))
        self.assertTrue(hasattr(slack_models, 'User'))
        self.assertTrue(hasattr(slack_models, 'UserProfile'))
        self.assertTrue(hasattr(slack_models, 'EnterpriseUser'))
        self.assertTrue(hasattr(slack_models, 'File'))
        self.assertTrue(hasattr(slack_models, 'FileContent'))
        self.assertTrue(hasattr(slack_models, 'ChatMessage'))
        self.assertTrue(hasattr(slack_models, 'Reaction'))
        self.assertTrue(hasattr(slack_models, 'MessageItem'))
        self.assertTrue(hasattr(slack_models, 'MessageEdited'))
        self.assertTrue(hasattr(slack_models, 'Authorization'))
        self.assertTrue(hasattr(slack_models, 'BaseSlackEvent'))

    def test_event_model_imports(self) -> None:
        """Test event model classes are importable."""
        self.assertTrue(hasattr(slack_models, 'MessageEvent'))
        self.assertTrue(hasattr(slack_models, 'AppMentionEvent'))
        self.assertTrue(hasattr(slack_models, 'ReactionAddedEvent'))
        self.assertTrue(hasattr(slack_models, 'ReactionRemovedEvent'))
        self.assertTrue(hasattr(slack_models, 'TeamJoinEvent'))
        self.assertTrue(hasattr(slack_models, 'FileCreatedEvent'))
        self.assertTrue(hasattr(slack_models, 'FileDeletedEvent'))
        self.assertTrue(hasattr(slack_models, 'ChannelCreatedEvent'))
        self.assertTrue(hasattr(slack_models, 'ChannelDeletedEvent'))
        self.assertTrue(hasattr(slack_models, 'ChannelRenameEvent'))

    def test_webhook_payload_imports(self) -> None:
        """Test webhook payload classes are importable."""
        self.assertTrue(hasattr(slack_models, 'SlackEventCallback'))
        self.assertTrue(hasattr(slack_models, 'SlackUrlVerification'))
        self.assertTrue(hasattr(slack_models, 'SlackAppRateLimited'))

    def test_union_type_imports(self) -> None:
        """Test union type imports."""
        self.assertTrue(hasattr(slack_models, 'SlackEvent'))
        self.assertTrue(hasattr(slack_models, 'SlackWebhookPayload'))

    def test_utility_imports(self) -> None:
        """Test utility function and constant imports."""
        self.assertTrue(hasattr(slack_models, 'EVENT_MAP'))
        self.assertTrue(hasattr(slack_models, 'parse_event'))
        self.assertTrue(hasattr(slack_models, 'version'))

    def test_imported_classes_are_pydantic_models(self) -> None:
        """Test that imported classes are Pydantic models."""
        # Test basic models
        self.assertTrue(issubclass(slack_models.Channel, pydantic.BaseModel))
        self.assertTrue(issubclass(slack_models.User, pydantic.BaseModel))
        self.assertTrue(
            issubclass(slack_models.UserProfile, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.EnterpriseUser, pydantic.BaseModel)
        )
        self.assertTrue(issubclass(slack_models.File, pydantic.BaseModel))
        self.assertTrue(
            issubclass(slack_models.FileContent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ChatMessage, pydantic.BaseModel)
        )
        self.assertTrue(issubclass(slack_models.Reaction, pydantic.BaseModel))
        self.assertTrue(
            issubclass(slack_models.MessageItem, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.MessageEdited, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.Authorization, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.BaseSlackEvent, pydantic.BaseModel)
        )

        # Test event models
        self.assertTrue(
            issubclass(slack_models.MessageEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.AppMentionEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ReactionAddedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ReactionRemovedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.TeamJoinEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.FileCreatedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.FileDeletedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ChannelCreatedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ChannelDeletedEvent, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.ChannelRenameEvent, pydantic.BaseModel)
        )

        # Test webhook payload models
        self.assertTrue(
            issubclass(slack_models.SlackEventCallback, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.SlackUrlVerification, pydantic.BaseModel)
        )
        self.assertTrue(
            issubclass(slack_models.SlackAppRateLimited, pydantic.BaseModel)
        )

    def test_event_models_inherit_from_base_slack_event(self) -> None:
        """Test that event models inherit from BaseSlackEvent."""
        self.assertTrue(
            issubclass(slack_models.MessageEvent, slack_models.BaseSlackEvent)
        )
        self.assertTrue(
            issubclass(
                slack_models.AppMentionEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.ReactionAddedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.ReactionRemovedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(slack_models.TeamJoinEvent, slack_models.BaseSlackEvent)
        )
        self.assertTrue(
            issubclass(
                slack_models.FileCreatedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.FileDeletedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.ChannelCreatedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.ChannelDeletedEvent, slack_models.BaseSlackEvent
            )
        )
        self.assertTrue(
            issubclass(
                slack_models.ChannelRenameEvent, slack_models.BaseSlackEvent
            )
        )

    def test_parse_event_function_is_callable(self) -> None:
        """Test parse_event function is callable."""
        self.assertTrue(callable(slack_models.parse_event))

    def test_event_map_is_dict(self) -> None:
        """Test EVENT_MAP is a dictionary."""
        self.assertIsInstance(slack_models.EVENT_MAP, dict)
        self.assertGreater(len(slack_models.EVENT_MAP), 0)

    def test_version_is_string(self) -> None:
        """Test version is a string."""
        self.assertIsInstance(slack_models.version, str)


class TestAllExports(unittest.TestCase):
    """Test __all__ exports match available attributes."""

    def test_all_exports_are_available(self) -> None:
        """Test all items in __all__ are available as attributes."""
        for name in slack_models.__all__:
            self.assertTrue(
                hasattr(slack_models, name),
                f'{name} in __all__ but not available as attribute',
            )

    def test_all_exports_completeness(self) -> None:
        """Test __all__ includes all expected exports."""
        expected_exports = {
            # Basic models
            'Channel',
            'User',
            'UserProfile',
            'EnterpriseUser',
            'File',
            'FileContent',
            'ChatMessage',
            'Reaction',
            'MessageItem',
            'MessageEdited',
            'Authorization',
            'BaseSlackEvent',
            # Event models
            'MessageEvent',
            'AppMentionEvent',
            'ReactionAddedEvent',
            'ReactionRemovedEvent',
            'TeamJoinEvent',
            'FileCreatedEvent',
            'FileDeletedEvent',
            'ChannelCreatedEvent',
            'ChannelDeletedEvent',
            'ChannelRenameEvent',
            # Webhook payload models
            'SlackEventCallback',
            'SlackUrlVerification',
            'SlackAppRateLimited',
            # Union types
            'SlackEvent',
            'SlackWebhookPayload',
            # Utilities
            'EVENT_MAP',
            'parse_event',
            'version',
        }

        actual_exports = set(slack_models.__all__)
        self.assertEqual(actual_exports, expected_exports)

    def test_all_exports_are_unique(self) -> None:
        """Test __all__ contains no duplicates."""
        all_exports = slack_models.__all__
        self.assertEqual(len(all_exports), len(set(all_exports)))

    def test_all_exports_are_strings(self) -> None:
        """Test all items in __all__ are strings."""
        for name in slack_models.__all__:
            self.assertIsInstance(name, str)

    def test_no_private_exports(self) -> None:
        """Test __all__ doesn't export private attributes."""
        for name in slack_models.__all__:
            self.assertFalse(
                name.startswith('_'),
                f'{name} is private but exported in __all__',
            )

    def test_all_model_classes_exported(self) -> None:
        """Test all model classes are exported in __all__."""
        # Get all classes from the module that are Pydantic models
        model_classes = []
        for name in dir(slack_models):
            attr = getattr(slack_models, name)
            if (
                isinstance(attr, type)
                and issubclass(attr, pydantic.BaseModel)
                and not name.startswith('_')
            ):
                model_classes.append(name)

        # Check that all model classes are in __all__
        for class_name in model_classes:
            self.assertIn(
                class_name,
                slack_models.__all__,
                f'Model class {class_name} not exported in __all__',
            )


class TestDirectImports(unittest.TestCase):
    """Test direct imports work correctly."""

    def test_direct_import_syntax(self) -> None:
        """Test direct import syntax works."""
        # Test importing individual classes
        from slack_models import Channel, MessageEvent, User

        self.assertTrue(issubclass(Channel, pydantic.BaseModel))
        self.assertTrue(issubclass(User, pydantic.BaseModel))
        self.assertTrue(issubclass(MessageEvent, pydantic.BaseModel))

    def test_star_import_syntax(self) -> None:
        """Test star import syntax works."""
        # This would normally be dangerous, but we'll test it exists
        # by checking that __all__ is properly defined
        self.assertTrue(hasattr(slack_models, '__all__'))
        self.assertIsInstance(slack_models.__all__, list)
        self.assertGreater(len(slack_models.__all__), 0)

    def test_module_has_proper_structure(self) -> None:
        """Test module has proper structure for imports."""
        self.assertTrue(hasattr(slack_models, '__name__'))
        self.assertTrue(hasattr(slack_models, '__all__'))
        self.assertTrue(
            hasattr(slack_models, '__version__')
            or hasattr(slack_models, 'version')
        )

    def test_import_from_private_modules_fails(self) -> None:
        """Test that imports from private modules are not accessible."""
        # The _models module should not be importable directly from public API
        # but may be accessible via internal mechanisms
        # Test that we can't import from slack_models.models (old path)
        with self.assertRaises(AttributeError):
            _ = slack_models.models  # This should fail

        # But the models themselves should be available
        self.assertTrue(hasattr(slack_models, 'Channel'))
        self.assertTrue(hasattr(slack_models, 'User'))


class TestCircularImports(unittest.TestCase):
    """Test there are no circular import issues."""

    def test_reimport_module(self) -> None:
        """Test reimporting the module doesn't cause issues."""
        import slack_models as sm1
        import slack_models as sm2

        # Should be the same module
        self.assertIs(sm1, sm2)

        # Should have all the same attributes
        self.assertEqual(sm1.__all__, sm2.__all__)
        self.assertEqual(sm1.EVENT_MAP, sm2.EVENT_MAP)

    def test_import_submodules_directly(self) -> None:
        """Test importing submodules directly works."""
        # We should be able to import the utility function directly
        from slack_models import parse_event

        self.assertTrue(callable(parse_event))

        # Test it works
        event = parse_event(
            {
                'type': 'message',
                'channel': 'C1234567890',
                'user': 'U1234567890',
                'text': 'Hello!',
                'ts': '1640995200.000100',
            }
        )

        self.assertIsInstance(event, slack_models.MessageEvent)


if __name__ == '__main__':
    unittest.main()
