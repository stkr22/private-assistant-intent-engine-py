"""Tests for intent pattern update functionality."""

import pytest

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
            assert hasattr(pattern, "negative_keywords")
            assert len(pattern.keywords) > 0
            # Verify keywords are tuples of (pattern, is_regex)
            assert all(isinstance(kw, tuple) and len(kw) == 2 for kw in pattern.keywords)

    def test_pattern_registry_topic_configurable(self):
        """Test that pattern update topic can be configured."""
        custom_topic = "custom/pattern/update/topic"
        registry = MockPatternRegistry(pattern_update_topic=custom_topic)

        assert registry.pattern_update_topic == custom_topic
