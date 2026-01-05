"""Tests for error handling in the intent engine."""

import json
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
import spacy
from private_assistant_commons import ClientRequest

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_engine import IntentEngine
from private_assistant_intent_engine.intent_patterns import load_intent_patterns


@pytest.fixture
def intent_engine(mock_rooms):
    """Create an IntentEngine instance for testing."""
    config_mock = config.Config()
    mqtt_client_mock = AsyncMock()
    logger_mock = Mock()
    nlp_model = spacy.load("en_core_web_md")
    intent_patterns = load_intent_patterns()
    classifier = IntentClassifier(config_mock, nlp_model, intent_patterns, mock_rooms)
    return IntentEngine(config_mock, mqtt_client_mock, logger_mock, classifier)


@pytest.fixture
def valid_client_request():
    """Create a valid client request for testing."""
    return ClientRequest(
        id=uuid.uuid4(),
        room="livingroom",
        output_topic="test/test/stuff",
        text="Turn on the lights",
    )


@pytest.mark.asyncio
async def test_handle_malformed_json(intent_engine):
    """Test that malformed JSON is handled gracefully."""
    malformed_json = "{ invalid json }"

    # Should not raise an exception
    await intent_engine.handle_intent_input_message(malformed_json)

    # Check that error was logged
    intent_engine.logger.error.assert_called()
    # Check for either json_parsing_errors or json_validation_errors
    # (malformed JSON can trigger either depending on how it fails)
    total_json_errors = intent_engine.error_metrics.get("json_parsing_errors", 0) + intent_engine.error_metrics.get(
        "json_validation_errors", 0
    )
    assert total_json_errors == 1

    # Verify MQTT publish was not called
    intent_engine.mqtt_client.publish.assert_not_called()


@pytest.mark.asyncio
async def test_handle_invalid_json_structure(intent_engine):
    """Test that valid JSON with invalid structure is handled gracefully."""
    invalid_structure = json.dumps({"wrong": "structure"})

    # Should not raise an exception
    await intent_engine.handle_intent_input_message(invalid_structure)

    # Check that error was logged
    intent_engine.logger.error.assert_called()
    assert intent_engine.error_metrics["json_validation_errors"] == 1

    # Verify MQTT publish was not called
    intent_engine.mqtt_client.publish.assert_not_called()


@pytest.mark.asyncio
async def test_classification_exception_handling(intent_engine, valid_client_request):
    """Test that classification exceptions are handled gracefully."""
    payload = valid_client_request.model_dump_json()

    # Mock classifier to raise an exception
    with patch.object(intent_engine, "classify_intent", side_effect=RuntimeError("Classification error")):
        await intent_engine.handle_intent_input_message(payload)

    # Check that error was logged
    intent_engine.logger.error.assert_called()
    assert intent_engine.error_metrics["unexpected_classification_errors"] == 1

    # Verify MQTT publish was not called due to error
    intent_engine.mqtt_client.publish.assert_not_called()


@pytest.mark.asyncio
async def test_mqtt_publish_failure(intent_engine, valid_client_request):
    """Test that MQTT publish failures are handled gracefully."""
    payload = valid_client_request.model_dump_json()

    # Mock MQTT client to raise an exception on publish
    intent_engine.mqtt_client.publish.side_effect = Exception("MQTT error")

    # Should not raise an exception
    await intent_engine.handle_intent_input_message(payload)

    # Check that error was logged
    intent_engine.logger.error.assert_called()
    assert intent_engine.error_metrics["mqtt_publish_errors"] == 1


def test_classify_intent_with_exception_returns_none(intent_engine, valid_client_request):
    """Test that classify_intent returns None on unexpected errors."""
    # Mock SpaCy to raise an unexpected exception
    with patch.object(intent_engine, "command_split", Mock(split=Mock(side_effect=Exception("Unexpected")))):
        result = intent_engine.classify_intent(valid_client_request)

    assert result is None
    assert intent_engine.error_metrics["unexpected_classification_errors"] == 1


def test_get_error_metrics(intent_engine):
    """Test error metrics retrieval."""
    test_error_count = 5
    another_error_count = 3
    intent_engine.error_metrics["test_error"] = test_error_count
    intent_engine.error_metrics["another_error"] = another_error_count

    metrics = intent_engine.get_error_metrics()
    assert metrics["test_error"] == test_error_count
    assert metrics["another_error"] == another_error_count

    # Verify it returns a copy, not the original
    metrics["new_error"] = 10
    assert "new_error" not in intent_engine.error_metrics


def test_reset_error_metrics(intent_engine):
    """Test error metrics reset."""
    test_error_count = 5
    another_error_count = 3
    intent_engine.error_metrics["test_error"] = test_error_count
    intent_engine.error_metrics["another_error"] = another_error_count

    intent_engine.reset_error_metrics()
    assert len(intent_engine.error_metrics) == 0
    assert intent_engine.get_error_metrics() == {}


@pytest.mark.asyncio
async def test_message_loop_continues_after_error(intent_engine):
    """Test that the message processing loop continues after errors."""
    # Use the actual topic pattern from config
    topic_pattern = "assistant/comms_bridge/test/test/input"

    # Create mock messages with different payloads
    # Mock topic with matches() method that returns True for the pattern
    def make_mock_topic(topic_value):
        topic_mock = Mock(value=topic_value)
        topic_mock.matches = Mock(return_value=True)
        return topic_mock

    messages = [
        Mock(topic=make_mock_topic(topic_pattern), payload=b"{ invalid json }"),  # Will fail
        Mock(
            topic=make_mock_topic(topic_pattern),
            payload=b'{"id": "d69b6bd5-188b-4442-bdf3-61aaef1e2594", '
            b'"room": "test", "output_topic": "test/out", "text": "valid"}',
        ),  # Will succeed
    ]

    # Mock the client messages generator
    async def mock_messages():
        for msg in messages:
            yield msg

    client_mock = Mock()
    client_mock.messages = mock_messages()

    # Process messages
    message_count = 0
    async for message in client_mock.messages:
        if message.topic.matches(intent_engine.config_obj.client_request_subscription):
            payload_str = intent_engine.decode_message_payload(message.payload)
            if payload_str is not None:
                try:
                    await intent_engine.handle_intent_input_message(payload_str)
                except Exception as e:
                    intent_engine.logger.critical(
                        "Critical error in message processing (should not happen): %s", str(e)
                    )
                    intent_engine.error_metrics["critical_loop_errors"] += 1
            message_count += 1

    # Verify both messages were processed
    expected_message_count = 2
    assert message_count == expected_message_count
    # First message should have caused an error
    total_json_errors = intent_engine.error_metrics.get("json_parsing_errors", 0) + intent_engine.error_metrics.get(
        "json_validation_errors", 0
    )
    assert total_json_errors >= 1
    # The loop should have continued despite the error
