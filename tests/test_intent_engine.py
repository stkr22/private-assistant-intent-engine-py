import uuid
from unittest.mock import Mock

import pytest
import spacy
from private_assistant_commons import ClientRequest, EntityType, IntentType

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_engine import IntentEngine
from private_assistant_intent_engine.intent_patterns import load_intent_patterns

# Test data constants
EXPECTED_TEMPERATURE = 22  # Temperature value used in compound command test


@pytest.fixture
def intent_engine(mock_rooms):
    config_mock = config.Config()
    mqtt_client_mock = Mock()
    logger_mock = Mock()
    nlp_model = spacy.load("en_core_web_md")
    intent_patterns = load_intent_patterns()
    classifier = IntentClassifier(config_mock, nlp_model, intent_patterns, mock_rooms)
    return IntentEngine(config_mock, mqtt_client_mock, logger_mock, classifier)


@pytest.fixture
def client_request() -> ClientRequest:
    return ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text=f"Turn on the lights in room kitchen. In addition, Set the temperature to {EXPECTED_TEMPERATURE} degrees.",
    )


def test_classify_intent_command_split(intent_engine, client_request):
    """Test that compound commands are split and classified correctly."""
    results = intent_engine.classify_intent(client_request)
    expected_command_count = 2
    assert len(results) == expected_command_count

    # Validate first command - device on
    assert results[0].intent_type == IntentType.DEVICE_ON
    assert "kitchen" in [e.normalized_value for e in results[0].entities.get(EntityType.ROOM.value, [])]

    # Validate second command - device set
    assert results[1].intent_type == IntentType.DEVICE_SET
    numbers = [e.normalized_value for e in results[1].entities.get(EntityType.NUMBER.value, [])]
    assert EXPECTED_TEMPERATURE in numbers


def test_classify_intent_all_rooms(intent_engine):
    """Test that 'all rooms' is properly detected."""
    request = ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights in all rooms",
    )

    results = intent_engine.classify_intent(request)
    expected_result_count = 1
    assert len(results) == expected_result_count

    # Validate intent type
    assert results[0].intent_type == IntentType.DEVICE_ON

    # Validate all rooms are detected
    room_entities = results[0].entities.get(EntityType.ROOM.value, [])
    detected_rooms = {e.normalized_value for e in room_entities}
    assert detected_rooms == {"living room", "kitchen", "bathroom", "bedroom"}


def test_classify_intent_returns_classified_intent(intent_engine):
    """Test that classification returns ClassifiedIntent objects."""
    request = ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn off the lights",
    )

    results = intent_engine.classify_intent(request)

    assert results is not None
    assert len(results) == 1
    assert results[0].intent_type == IntentType.DEVICE_OFF
    assert results[0].confidence > 0.0
    assert results[0].raw_text == "Turn off the lights"
