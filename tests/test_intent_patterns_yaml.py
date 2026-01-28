"""Tests for YAML-based intent pattern configuration."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import spacy
from private_assistant_commons import IntentType

from private_assistant_intent_engine.config import Config
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_patterns import (
    IntentPatternConfig,
    IntentPatternsConfig,
    load_intent_patterns,
)


class TestIntentPatternConfig:
    """Test IntentPatternConfig validation."""

    def test_valid_pattern_config(self):
        """Test creating a valid intent pattern config."""
        pattern = IntentPatternConfig(
            intent_type=IntentType.DEVICE_ON,
            keywords=["turn on", "switch on"],
            context_hints=["light", "lamp"],
            negative_keywords=["off"],
        )

        assert pattern.intent_type == IntentType.DEVICE_ON
        assert pattern.keywords == ["turn on", "switch on"]
        assert pattern.context_hints == ["light", "lamp"]
        assert pattern.negative_keywords == ["off"]

    def test_empty_keywords_validation(self):
        """Test that empty keywords list raises validation error."""
        with pytest.raises(ValueError, match="Intent pattern keywords cannot be empty"):
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_ON,
                keywords=[],
                context_hints=["light"],
                negative_keywords=[],
            )


class TestIntentPatternsConfig:
    """Test IntentPatternsConfig YAML loading and merging."""

    def test_get_default_patterns(self):
        """Test that default patterns are loaded correctly."""
        config = IntentPatternsConfig.get_default_patterns()

        assert len(config.patterns) > 0
        # Check a few specific default patterns exist
        intent_types = [p.intent_type for p in config.patterns]
        assert IntentType.DEVICE_ON in intent_types
        assert IntentType.DEVICE_OFF in intent_types
        assert IntentType.MEDIA_PLAY in intent_types

    def test_from_yaml_file_not_found(self):
        """Test that missing YAML file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            IntentPatternsConfig.from_yaml("/nonexistent/path.yaml")

    def test_from_yaml_invalid_structure(self):
        """Test that YAML without 'patterns' key raises ValueError."""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: structure\n")
            yaml_path = f.name

        try:
            with pytest.raises(ValueError, match="YAML must contain 'patterns' key"):
                IntentPatternsConfig.from_yaml(yaml_path)
        finally:
            Path(yaml_path).unlink()

    def test_from_yaml_selective_override(self):
        """Test that YAML patterns override defaults selectively."""
        # Create custom YAML with one override
        yaml_content = """
patterns:
  - intent_type: device.on
    keywords:
      - turn on
      - fire up
    context_hints:
      - light
    negative_keywords:
      - "off"
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            config = IntentPatternsConfig.from_yaml(yaml_path)

            # Check that DEVICE_ON was overridden
            device_on = next(p for p in config.patterns if p.intent_type == IntentType.DEVICE_ON)
            assert "fire up" in device_on.keywords
            assert device_on.keywords == ["turn on", "fire up"]

            # Check that other patterns still use defaults
            device_off = next(p for p in config.patterns if p.intent_type == IntentType.DEVICE_OFF)
            assert "switch off" in device_off.keywords  # Default value

            # Check all default patterns are still present
            intent_types = [p.intent_type for p in config.patterns]
            assert IntentType.MEDIA_PLAY in intent_types
            assert IntentType.DEVICE_QUERY in intent_types
        finally:
            Path(yaml_path).unlink()

    def test_from_yaml_multiple_overrides(self):
        """Test loading multiple custom patterns from YAML."""
        yaml_content = """
patterns:
  - intent_type: device.on
    keywords:
      - turn on
      - activate
    context_hints:
      - light
    negative_keywords:
      - "off"

  - intent_type: media.play
    keywords:
      - play
      - put on
    context_hints:
      - music
      - song
    negative_keywords:
      - stop
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            config = IntentPatternsConfig.from_yaml(yaml_path)

            # Check both patterns were overridden
            device_on = next(p for p in config.patterns if p.intent_type == IntentType.DEVICE_ON)
            assert "activate" in device_on.keywords

            media_play = next(p for p in config.patterns if p.intent_type == IntentType.MEDIA_PLAY)
            assert "put on" in media_play.keywords
        finally:
            Path(yaml_path).unlink()

    def test_from_yaml_empty_patterns(self):
        """Test that empty patterns list still loads defaults."""
        yaml_content = """
patterns: []
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            config = IntentPatternsConfig.from_yaml(yaml_path)

            # Should still have all default patterns
            assert len(config.patterns) > 0
            intent_types = [p.intent_type for p in config.patterns]
            assert IntentType.DEVICE_ON in intent_types
        finally:
            Path(yaml_path).unlink()


class TestLoadIntentPatterns:
    """Test the load_intent_patterns helper function."""

    def test_load_default_patterns(self):
        """Test loading default patterns when no path specified."""
        patterns = load_intent_patterns(None)

        assert len(patterns) > 0
        intent_types = [p.intent_type for p in patterns]
        assert IntentType.DEVICE_ON in intent_types
        assert IntentType.MEDIA_PLAY in intent_types

    def test_load_custom_patterns(self):
        """Test loading patterns from YAML file."""
        yaml_content = """
patterns:
  - intent_type: device.on
    keywords:
      - turn on
      - custom keyword
    context_hints:
      - light
    negative_keywords:
      - "off"
"""
        with NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            yaml_path = f.name

        try:
            patterns = load_intent_patterns(yaml_path)

            # Should have merged patterns
            device_on = next(p for p in patterns if p.intent_type == IntentType.DEVICE_ON)
            assert "custom keyword" in device_on.keywords
        finally:
            Path(yaml_path).unlink()


class TestIntentClassifierWithCustomPatterns:
    """Test IntentClassifier with custom pattern injection (improved testability)."""

    @pytest.fixture
    def nlp_model(self):
        """Load SpaCy model for testing."""
        return spacy.load("en_core_web_md")

    def test_classifier_with_minimal_patterns(self, nlp_model, mock_rooms):
        """Test that classifier can be initialized with custom minimal patterns for focused testing."""
        # Create minimal pattern set for testing
        custom_patterns = [
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_ON,
                keywords=["activate"],
                context_hints=[],
                negative_keywords=[],
            )
        ]

        # Create a mock pattern registry with custom patterns
        class CustomPatternRegistry:
            def __init__(self):
                self.patterns = custom_patterns
                self.pattern_update_topic = "assistant/intent_pattern_update"

        config_obj = Config()
        custom_registry = CustomPatternRegistry()
        classifier = IntentClassifier(config_obj, nlp_model, custom_registry, mock_rooms)

        # Should classify with custom pattern
        results = classifier.classify("activate the device")

        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_ON

    def test_classifier_with_injected_patterns(self, nlp_model, mock_rooms):
        """Test classifier accepts externally-loaded patterns (better for testing)."""
        # Load patterns externally
        patterns = load_intent_patterns()

        # Create a mock pattern registry with loaded patterns
        class LoadedPatternRegistry:
            def __init__(self):
                self.patterns = patterns
                self.pattern_update_topic = "assistant/intent_pattern_update"

        # Inject into classifier
        config_obj = Config()
        loaded_registry = LoadedPatternRegistry()
        classifier = IntentClassifier(config_obj, nlp_model, loaded_registry, mock_rooms)

        # Should work normally
        results = classifier.classify("turn on the lights")
        assert len(results) > 0
        assert results[0][0] == IntentType.DEVICE_ON
