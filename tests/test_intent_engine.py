import uuid
from unittest.mock import Mock

import pytest
import spacy
from private_assistant_commons.messages import ClientRequest

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_engine import IntentEngine


@pytest.fixture
def intent_engine():
    config_mock = config.Config()
    mqtt_client_mock = Mock()
    logger_mock = Mock()
    nlp_model = spacy.load("en_core_web_md")
    return IntentEngine(config_mock, mqtt_client_mock, nlp_model, logger_mock)


@pytest.fixture
def client_request() -> ClientRequest:
    return ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights in room kitchen. In addition, Set the temperature to 22 degrees.",
    )


def test_analyze_text_command_split(intent_engine, client_request):
    results = intent_engine.analyze_text(client_request)
    assert len(results) == 2

    # Validate first command text
    assert results[0].client_request.text == "Turn on the lights in room kitchen."
    assert "turn" in results[0].verbs
    assert "lights" in results[0].nouns
    assert "kitchen" in results[0].rooms

    # Validate second command text
    assert results[1].client_request.text == "Set the temperature to 22 degrees."
    assert "set" in results[1].verbs
    assert "temperature" in results[1].nouns
    assert any(num.number_token == 22 for num in results[1].numbers)


def test_analyze_text_all_rooms(intent_engine):
    request = ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights in all rooms",
    )

    results = intent_engine.analyze_text(request)
    assert len(results) == 1

    # Validate single command text
    assert results[0].client_request.text == "Turn on the lights in all rooms"
    assert "turn" in results[0].verbs
    assert "lights" in results[0].nouns
    assert set(results[0].rooms) == {"living room", "kitchen", "bathroom"}


def test_analyze_text_preserves_request_attributes(intent_engine, client_request):
    results = intent_engine.analyze_text(client_request)

    for result in results:
        # Verify all attributes except text remain unchanged
        assert result.client_request.id == client_request.id
        assert result.client_request.room == client_request.room
        assert result.client_request.output_topic == client_request.output_topic
