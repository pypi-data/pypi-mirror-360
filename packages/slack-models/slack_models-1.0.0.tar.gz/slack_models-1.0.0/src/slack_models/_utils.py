from slack_models import _models


def parse_event(event: dict) -> _models.SlackEvent:
    """Build a Pydantic model from a Slack event dictionary.

    Args:
        event: Raw Slack event dictionary

    Returns:
        Parsed Slack event model

    Raises:
        pydantic.ValidationError: If event cannot be parsed
        ValueError: If event type is unknown

    """
    event_type = event.get('type')
    if event_type is None:
        raise ValueError('Event type is missing')
    model_class = _models.EVENT_MAP.get(event_type)
    if not model_class:
        raise ValueError(f'Unknown event type: {event_type}')
    return model_class.model_validate(event)  # type: ignore[attr-defined]
