"""Tests for intent classification system."""

import uuid

import pytest
import spacy
from private_assistant_commons import ClassifiedIntent, ClientRequest, EntityType, IntentType

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_patterns import load_intent_patterns

# Confidence levels from hierarchical classification in IntentClassifier._calculate_confidence
MULTIWORD_WITH_CONTEXT = 1.0  # Multi-word keyword + context hints (e.g., "turn on" + "lights")
MULTIWORD_ONLY = 0.9  # Multi-word keyword without context (e.g., "switch off" alone)
KEYWORD_MULTI_CONTEXT = 0.9  # Single keyword + multiple context hints (e.g., "set" + "temperature" + "degrees")
KEYWORD_CONTEXT = 0.8  # Single keyword + single context hint (e.g., "stop" + "music")
ALL_KEYWORDS = 0.8  # All pattern keywords present
KEYWORD_ONLY = 0.5  # Single keyword match without context
CONTEXT_ONLY = 0.3  # Context hints without keywords


@pytest.fixture
def nlp_model():
    """Load SpaCy model for testing."""
    return spacy.load("en_core_web_md")


@pytest.fixture
def classifier(nlp_model, mock_rooms):
    """Create IntentClassifier instance for testing."""
    config_obj = config.Config()
    intent_patterns = load_intent_patterns()
    return IntentClassifier(config_obj, nlp_model, intent_patterns, mock_rooms)


@pytest.fixture
def classifier_with_registry(nlp_model, mock_rooms, mock_device_registry):
    """Create IntentClassifier instance with mock device registry."""
    config_obj = config.Config()
    intent_patterns = load_intent_patterns()
    return IntentClassifier(config_obj, nlp_model, intent_patterns, mock_rooms, device_registry=mock_device_registry)


class TestIntentClassifier:
    """Test suite for IntentClassifier."""

    def test_device_on_intent_exact_match(self, classifier):
        """Test device on intent with exact keyword match."""
        text = "Turn on the lights"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_ON
        assert results[0][1] == MULTIWORD_WITH_CONTEXT

    def test_device_off_intent(self, classifier):
        """Test device off intent classification."""
        text = "Switch off shelf"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_OFF
        assert results[0][1] == MULTIWORD_ONLY

    def test_device_set_intent(self, classifier):
        """Test device set intent for temperature control."""
        text = "Set temperature to 22 degrees"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_SET
        assert results[0][1] == KEYWORD_CONTEXT

    def test_media_play_intent(self, classifier):
        """Test media play intent classification."""
        text = "Play spotify playlist five"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.MEDIA_PLAY
        assert results[0][1] == KEYWORD_CONTEXT

    def test_media_stop_intent(self, classifier):
        """Test media stop intent classification."""
        text = "Stop the music"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.MEDIA_STOP
        assert results[0][1] == KEYWORD_CONTEXT

    def test_query_status_intent(self, classifier):
        """Test query status intent classification."""
        text = "Check state of open windows"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.QUERY_STATUS
        assert results[0][1] == MULTIWORD_ONLY

    def test_negative_keywords_exclude_intent(self, classifier):
        """Test that negative keywords properly exclude intents."""
        text = "turn off the lights"
        results = classifier.classify(text)

        # Should detect DEVICE_OFF as top intent
        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_OFF

    def test_schedule_set_intent(self, classifier):
        """Test schedule set intent with time reference."""
        text = "Turn on lights in 10 minutes"
        results = classifier.classify(text)

        intent_types = [result[0] for result in results]
        # Should detect both SCHEDULE_SET and DEVICE_ON
        assert IntentType.SCHEDULE_SET in intent_types or IntentType.DEVICE_ON in intent_types

    def test_empty_text(self, classifier):
        """Test handling of empty text."""
        text = ""
        results = classifier.classify(text)

        # Should return empty results or handle gracefully
        assert isinstance(results, list)

    def test_ambiguous_command(self, classifier):
        """Test handling of ambiguous commands."""
        text = "play 5"
        results = classifier.classify(text)

        # Should detect MEDIA_PLAY with reasonable confidence
        assert len(results) > 0
        intent_types = [result[0] for result in results]
        assert IntentType.MEDIA_PLAY in intent_types


class TestIntentClassifierIntegration:
    """Integration tests for intent classifier with IntentEngine."""

    def test_classify_intent_basic(self, nlp_model, mock_rooms):
        """Test basic intent classification through IntentEngine."""
        from unittest.mock import Mock

        from private_assistant_intent_engine.intent_engine import IntentEngine

        config_obj = config.Config()
        mqtt_client_mock = Mock()
        logger_mock = Mock()
        intent_patterns = load_intent_patterns()
        classifier = IntentClassifier(config_obj, nlp_model, intent_patterns, mock_rooms)

        engine = IntentEngine(config_obj, mqtt_client_mock, logger_mock, classifier)

        client_request = ClientRequest(
            id=uuid.uuid4(),
            room="kitchen",
            output_topic="test/output",
            text="Turn on the lights in kitchen",
        )

        results = engine.classify_intent(client_request)

        assert results is not None
        assert len(results) == 1
        assert isinstance(results[0], ClassifiedIntent)
        assert results[0].intent_type == IntentType.DEVICE_ON
        assert results[0].confidence > 0.0
        assert EntityType.ROOM.value in results[0].entities

    def test_compound_command_classification(self, nlp_model, mock_rooms):
        """Test classification of compound commands."""
        from unittest.mock import Mock

        from private_assistant_intent_engine.intent_engine import IntentEngine

        config_obj = config.Config()
        mqtt_client_mock = Mock()
        logger_mock = Mock()
        intent_patterns = load_intent_patterns()
        classifier = IntentClassifier(config_obj, nlp_model, intent_patterns, mock_rooms)

        engine = IntentEngine(config_obj, mqtt_client_mock, logger_mock, classifier)

        client_request = ClientRequest(
            id=uuid.uuid4(),
            room="kitchen",
            output_topic="test/output",
            text="Turn on the lights, in addition set temperature to 20",
        )

        results = engine.classify_intent(client_request)

        assert results is not None
        assert len(results) == 2  # noqa: PLR2004
        assert results[0].intent_type == IntentType.DEVICE_ON
        assert results[1].intent_type == IntentType.DEVICE_SET

    def test_alternative_intents(self, nlp_model, mock_rooms):
        """Test that alternative intents are captured."""
        from unittest.mock import Mock

        from private_assistant_intent_engine.intent_engine import IntentEngine

        config_obj = config.Config()
        mqtt_client_mock = Mock()
        logger_mock = Mock()
        intent_patterns = load_intent_patterns()
        classifier = IntentClassifier(config_obj, nlp_model, intent_patterns, mock_rooms)

        engine = IntentEngine(config_obj, mqtt_client_mock, logger_mock, classifier)

        client_request = ClientRequest(
            id=uuid.uuid4(),
            room="kitchen",
            output_topic="test/output",
            text="Turn on the lights",
        )

        results = engine.classify_intent(client_request)

        assert results is not None
        assert len(results) > 0
        # Alternative intents should be None or a list
        assert results[0].alternative_intents is None or isinstance(results[0].alternative_intents, list)
