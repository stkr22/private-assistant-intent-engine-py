"""Tests for regex pattern matching in intent classification."""

import pytest
import spacy
from private_assistant_commons import IntentType

from private_assistant_intent_engine import config
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_patterns import IntentPatternConfig

# Test confidence constants
COMPLEX_REGEX_MATCH = 1.0
MULTIPLE_KEYWORDS = 0.8
SINGLE_KEYWORD = 0.5
NO_MATCH = 0.0


@pytest.fixture
def nlp_model():
    """Load SpaCy model for testing."""
    return spacy.load("en_core_web_md")


@pytest.fixture
def classifier(nlp_model, mock_rooms, mock_pattern_registry):
    """Create IntentClassifier instance for testing."""
    config_obj = config.Config()
    return IntentClassifier(config_obj, nlp_model, mock_pattern_registry, mock_rooms)


class TestRegexPatternMatching:
    """Test suite for regex pattern matching."""

    def test_complex_regex_with_whitespace(self, classifier):
        """Test that complex regex patterns with \\s+ get 1.0 confidence."""
        text = "turn on the lights"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_ON
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_complex_regex_with_alternation(self, classifier):
        """Test that regex patterns with | get 1.0 confidence."""
        text = "set temperature to 22"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_SET
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_complex_regex_with_groups(self, classifier):
        """Test that regex patterns with groups get 1.0 confidence."""
        text = "play some music"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.MEDIA_PLAY
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_non_regex_keyword(self, classifier):
        """Test that non-regex single keywords get 0.5 confidence."""
        text = "list all devices"
        results = classifier.classify(text)

        # Should match DATA_QUERY with "list" keyword (non-regex)
        data_query_results = [r for r in results if r[0] == IntentType.DATA_QUERY]
        assert len(data_query_results) > 0
        # "list" is a non-regex single keyword, should be 0.5
        assert data_query_results[0][1] == SINGLE_KEYWORD

    def test_optional_groups(self, classifier):
        """Test that optional groups work correctly."""
        # With optional word
        text1 = "turn on the lights"
        results1 = classifier.classify(text1)
        assert results1[0][0] == IntentType.DEVICE_ON
        assert results1[0][1] == COMPLEX_REGEX_MATCH

        # Without optional word
        text2 = "turn on lights"
        results2 = classifier.classify(text2)
        assert results2[0][0] == IntentType.DEVICE_ON
        assert results2[0][1] == COMPLEX_REGEX_MATCH

    def test_negative_keywords_exclude(self, classifier):
        """Test that negative keywords properly exclude intents."""
        text = "turn off the lights"  # Should NOT match DEVICE_ON due to "off"
        results = classifier.classify(text)

        # Should get DEVICE_OFF, not DEVICE_ON
        assert results[0][0] == IntentType.DEVICE_OFF

        # Verify DEVICE_ON is not in results or has 0.0 confidence
        device_on_results = [r for r in results if r[0] == IntentType.DEVICE_ON]
        assert len(device_on_results) == 0  # Should be filtered out

    def test_case_insensitive_matching(self, classifier):
        """Test that regex matching is case-insensitive."""
        text = "TURN ON THE LIGHTS"
        results = classifier.classify(text)

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_ON
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_invalid_regex_handling(self, classifier):
        """Test that invalid regex patterns are handled gracefully."""
        # Create a pattern with invalid regex
        invalid_pattern = IntentPatternConfig(
            intent_type=IntentType.DEVICE_ON,
            keywords=[("[invalid(regex", True)],  # Invalid regex
            negative_keywords=[],
        )

        # Should not crash, just return 0.0 confidence
        confidence = classifier._calculate_confidence("test text", invalid_pattern)
        assert confidence == NO_MATCH

    def test_multiple_keyword_matches(self, classifier):
        """Test that multiple keyword matches get 0.8 confidence."""
        # Create custom pattern with multiple non-regex keywords

        # Temporarily add a test pattern to registry
        test_pattern = IntentPatternConfig(
            intent_type=IntentType.DEVICE_SET,
            keywords=[
                ("set", False),
                ("adjust", False),
            ],
            negative_keywords=[],
        )

        # Test confidence calculation directly
        text = "set and adjust the device"
        confidence = classifier._calculate_confidence(text.lower(), test_pattern)
        # Both "set" and "adjust" match, should be 0.8
        assert confidence == MULTIPLE_KEYWORDS

    def test_all_keywords_matched(self, classifier):
        """Test that matching all keywords gives 0.8 confidence."""
        # Pattern with 3 keywords, if all match should be 0.8
        test_pattern = IntentPatternConfig(
            intent_type=IntentType.DEVICE_SET,
            keywords=[
                ("set", False),
                ("temperature", False),
                ("to", False),
            ],
            negative_keywords=[],
        )

        text = "set temperature to 22"
        confidence = classifier._calculate_confidence(text.lower(), test_pattern)
        # All 3 keywords match, should be 0.8
        assert confidence == MULTIPLE_KEYWORDS

    def test_regex_specificity_in_volume_set(self, classifier):
        """Test that 'set volume' correctly matches MEDIA_VOLUME_SET, not DEVICE_SET."""
        text = "set volume to 50"
        results = classifier.classify(text)

        # MEDIA_VOLUME_SET has specific pattern for "set volume" which should match with 1.0
        # DEVICE_SET generic "set" would only match with 0.5
        # MEDIA_VOLUME_SET should be first due to higher confidence
        assert results[0][0] == IntentType.MEDIA_VOLUME_SET
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_regex_with_numbers(self, classifier):
        """Test that regex patterns work with numbers in text."""
        text = "set temperature to 22 degrees"
        results = classifier.classify(text)

        assert results[0][0] == IntentType.DEVICE_SET
        assert results[0][1] == COMPLEX_REGEX_MATCH

    def test_confidence_sorting(self, classifier):
        """Test that results are sorted by confidence descending."""
        text = "set brightness"
        results = classifier.classify(text)

        # Verify results are sorted by confidence
        confidences = [r[1] for r in results]
        assert confidences == sorted(confidences, reverse=True)

        # Verify DEVICE_SET with specific "set brightness" pattern (1.0) comes first
        assert results[0][0] == IntentType.DEVICE_SET
        assert results[0][1] == COMPLEX_REGEX_MATCH
