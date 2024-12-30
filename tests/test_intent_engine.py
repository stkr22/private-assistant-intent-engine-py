import uuid
from unittest.mock import Mock

import pytest
import spacy
from private_assistant_commons.messages import ClientRequest, IntentAnalysisResult

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_engine import IntentEngine


@pytest.fixture
def intent_engine():
    # Mock configuration and logger
    config_mock = config.Config()
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    # Use a small SpaCy language model for testing
    nlp_model = spacy.load("en_core_web_md")

    # Create the IntentEngine instance
    return IntentEngine(config_mock, mqtt_client_mock, nlp_model, logger_mock)


def test_analyze_text(intent_engine):
    # Mock client request with multiple sentences
    client_request = ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights in room kitchen. In addition, Set the temperature to 22 degrees.",
    )

    # Call analyze_text
    results = intent_engine.analyze_text(client_request)

    # Validate the number of results (one per sentence)
    assert len(results) == 2

    # Validate first sentence analysis
    first_result = results[0]
    assert isinstance(first_result, IntentAnalysisResult)
    assert "turn" in first_result.verbs
    assert "lights" in first_result.nouns
    assert "kitchen" in first_result.rooms

    # Validate second sentence analysis
    second_result = results[1]
    assert isinstance(second_result, IntentAnalysisResult)
    assert "set" in second_result.verbs
    assert "temperature" in second_result.nouns
    assert any(num.number_token == 22 for num in second_result.numbers)


def test_analyze_text_all_rooms(intent_engine):
    client_request = ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights in all rooms",
    )

    results = intent_engine.analyze_text(client_request)
    assert len(results) == 1

    result = results[0]
    assert isinstance(result, IntentAnalysisResult)
    assert "turn" in result.verbs
    assert "lights" in result.nouns
    assert set(result.rooms) == {"living room", "kitchen", "bathroom"}
