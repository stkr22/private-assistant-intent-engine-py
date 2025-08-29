"""Tests for error handling in the intent engine."""

import json
import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
import spacy
from private_assistant_commons.messages import ClientRequest

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_engine import IntentEngine


@pytest.fixture
def intent_engine():
    """Create an IntentEngine instance for testing."""
    config_mock = config.Config()
    mqtt_client_mock = AsyncMock()
    logger_mock = Mock()
    nlp_model = spacy.load("en_core_web_md")
    return IntentEngine(config_mock, mqtt_client_mock, nlp_model, logger_mock)


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
async def test_analyze_text_exception_handling(intent_engine, valid_client_request):
    """Test that text analysis exceptions are handled gracefully."""
    # Test that exceptions during text analysis return None
    with patch.object(intent_engine, "command_split", Mock(split=Mock(side_effect=RuntimeError("Unexpected")))):
        result = intent_engine.analyze_text(valid_client_request)

    assert result is None
    assert intent_engine.error_metrics["unexpected_analysis_errors"] == 1


@pytest.mark.asyncio
async def test_feature_extraction_failure_continues_processing(intent_engine, valid_client_request):
    """Test that feature extraction failures don't stop processing."""
    payload = valid_client_request.model_dump_json()

    # Mock text_tools to raise an exception
    with patch(
        "private_assistant_intent_engine.intent_engine.text_tools.extract_numbers_from_text",
        side_effect=Exception("Extraction error"),
    ):
        await intent_engine.handle_intent_input_message(payload)

    # Check that error was logged
    intent_engine.logger.error.assert_called()
    assert intent_engine.error_metrics["feature_extraction_errors"] == 1

    # Verify MQTT publish was still called (with empty features)
    intent_engine.mqtt_client.publish.assert_called_once()

    # Verify the published result has empty features
    call_args = intent_engine.mqtt_client.publish.call_args
    published_json = call_args[0][1]
    result = json.loads(published_json)
    assert result["numbers"] == []
    assert result["verbs"] == []
    assert result["nouns"] == []


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


def test_analyze_text_with_exception_returns_none(intent_engine, valid_client_request):
    """Test that analyze_text returns None on unexpected errors."""
    # Mock SpaCy to raise an unexpected exception
    with patch.object(intent_engine, "command_split", Mock(split=Mock(side_effect=Exception("Unexpected")))):
        result = intent_engine.analyze_text(valid_client_request)

    assert result is None
    assert intent_engine.error_metrics["unexpected_analysis_errors"] == 1


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
    messages = [
        Mock(topic=Mock(value=topic_pattern), payload=b"{ invalid json }"),  # Will fail
        Mock(
            topic=Mock(value=topic_pattern),
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
        if intent_engine.client_request_pattern.match(message.topic.value):
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
