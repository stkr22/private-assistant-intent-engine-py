"""Tests for intent pattern update functionality."""

import pytest
from private_assistant_commons import IntentType

from private_assistant_intent_engine.intent_patterns import IntentPatternsConfig
from tests.conftest import MockPatternRegistry


class TestIntentPatternsRefresh:
    """Test pattern refresh mechanism."""

    @pytest.mark.asyncio
    async def test_mock_pattern_registry_initialization(self, mock_pattern_registry):
        """Test that mock pattern registry initializes with patterns."""
        assert len(mock_pattern_registry.patterns) > 0
        assert mock_pattern_registry.pattern_update_topic == "assistant/intent_pattern_update"

    @pytest.mark.asyncio
    async def test_setup_subscriptions_tracking(self, mock_pattern_registry):
        """Test that setup_subscriptions call is tracked."""
        assert not mock_pattern_registry.setup_subscriptions_called
        await mock_pattern_registry.setup_subscriptions()
        assert mock_pattern_registry.setup_subscriptions_called

    @pytest.mark.asyncio
    async def test_handle_pattern_update_tracking(self, mock_pattern_registry):
        """Test that pattern update calls are tracked."""
        assert mock_pattern_registry.handle_pattern_update_calls == 0
        await mock_pattern_registry.handle_pattern_update("test_payload")
        assert mock_pattern_registry.handle_pattern_update_calls == 1
        await mock_pattern_registry.handle_pattern_update("test_payload_2")
        assert mock_pattern_registry.handle_pattern_update_calls == 2


class TestDefaultPatterns:
    """Test default pattern configuration."""

    def test_default_patterns_loaded(self):
        """Test that default patterns are loaded correctly."""
        config = IntentPatternsConfig.get_default_patterns()

        assert len(config.patterns) > 0
        # Verify specific patterns exist
        intent_types = [p.intent_type for p in config.patterns]
        assert IntentType.DEVICE_ON in intent_types
        assert IntentType.DEVICE_OFF in intent_types
        assert IntentType.MEDIA_PLAY in intent_types
        assert IntentType.DEVICE_QUERY in intent_types

    def test_device_on_pattern_structure(self):
        """Test DEVICE_ON pattern has expected structure."""
        config = IntentPatternsConfig.get_default_patterns()
        device_on = next(p for p in config.patterns if p.intent_type == IntentType.DEVICE_ON)

        assert len(device_on.keywords) > 0
        assert "turn on" in device_on.keywords
        assert len(device_on.context_hints) > 0
        assert "light" in device_on.context_hints or "lights" in device_on.context_hints
        assert len(device_on.negative_keywords) > 0
        assert "off" in device_on.negative_keywords

    def test_pattern_count_consistency(self):
        """Test that pattern count matches expected number of intent types."""
        config = IntentPatternsConfig.get_default_patterns()

        # Should have patterns for common intent types
        expected_minimum = 10  # At least 10 patterns
        assert len(config.patterns) >= expected_minimum

    def test_all_patterns_have_keywords(self):
        """Test that all patterns have at least one keyword."""
        config = IntentPatternsConfig.get_default_patterns()

        for pattern in config.patterns:
            assert len(pattern.keywords) > 0, f"Pattern {pattern.intent_type} has no keywords"


class TestPatternRegistry:
    """Test pattern registry behavior."""

    def test_mock_registry_has_required_attributes(self, mock_pattern_registry):
        """Test that mock registry has all required attributes."""
        assert hasattr(mock_pattern_registry, "patterns")
        assert hasattr(mock_pattern_registry, "pattern_update_topic")
        assert hasattr(mock_pattern_registry, "setup_subscriptions")
        assert hasattr(mock_pattern_registry, "handle_pattern_update")

    def test_mock_registry_patterns_are_valid(self, mock_pattern_registry):
        """Test that patterns in mock registry are valid IntentPatternConfig objects."""
        assert len(mock_pattern_registry.patterns) > 0

        for pattern in mock_pattern_registry.patterns:
            assert hasattr(pattern, "intent_type")
            assert hasattr(pattern, "keywords")
            assert hasattr(pattern, "context_hints")
            assert hasattr(pattern, "negative_keywords")
            assert len(pattern.keywords) > 0

    def test_pattern_registry_topic_configurable(self):
        """Test that pattern update topic can be configured."""
        custom_topic = "custom/pattern/update/topic"
        registry = MockPatternRegistry(pattern_update_topic=custom_topic)

        assert registry.pattern_update_topic == custom_topic
