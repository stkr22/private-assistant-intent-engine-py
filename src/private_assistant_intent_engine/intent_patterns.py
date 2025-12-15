"""Intent pattern configuration models for the Private Assistant Intent Engine.

This module defines intent pattern models and provides functionality to load
custom patterns from YAML files or use sensible defaults. Intent patterns
define the keywords and context hints used to classify user commands.
"""

from pathlib import Path

import yaml
from private_assistant_commons import IntentType
from pydantic import BaseModel, Field, field_validator


class IntentPatternConfig(BaseModel):
    """Configuration for a single intent pattern.

    Defines the keywords and context hints used to identify a specific
    intent type in user commands.

    Attributes:
        intent_type: The IntentType enum value this pattern matches
        keywords: Primary keywords that indicate this intent
        context_hints: Supporting words that strengthen intent confidence
        negative_keywords: Keywords that invalidate this intent match
    """

    intent_type: IntentType
    keywords: list[str] = Field(default_factory=list)
    context_hints: list[str] = Field(default_factory=list)
    negative_keywords: list[str] = Field(default_factory=list)

    @field_validator("keywords")
    @classmethod
    def validate_keywords_not_empty(cls, v: list[str]) -> list[str]:
        """Validate that keywords list is not empty.

        Args:
            v: List of keywords to validate

        Returns:
            Validated keyword list

        Raises:
            ValueError: If keywords list is empty
        """
        if not v:
            raise ValueError("Intent pattern keywords cannot be empty")
        return v


class IntentPatternsConfig(BaseModel):
    """Configuration container for all intent patterns.

    Manages a collection of intent patterns that can be loaded from YAML
    and selectively overridden. Merges custom patterns with defaults.

    Attributes:
        patterns: List of intent pattern configurations
    """

    patterns: list[IntentPatternConfig] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> "IntentPatternsConfig":
        """Load intent patterns from YAML file.

        Loads patterns from YAML and merges with defaults. If a pattern
        for an intent_type exists in the YAML, it replaces the default.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            IntentPatternsConfig with merged patterns

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            ValueError: If YAML is invalid
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"Intent patterns file not found: {yaml_path}")

        with yaml_path.open("r") as f:
            data = yaml.safe_load(f)

        if not data or "patterns" not in data:
            raise ValueError("YAML must contain 'patterns' key")

        # Load custom patterns from YAML
        custom_config = cls.model_validate(data)

        # Get default patterns
        defaults = cls.get_default_patterns()

        # Create intent_type -> pattern mapping for merging
        custom_patterns_map = {p.intent_type: p for p in custom_config.patterns}
        default_patterns_map = {p.intent_type: p for p in defaults.patterns}

        # Merge: custom overrides default
        merged_patterns_map = {**default_patterns_map, **custom_patterns_map}

        return cls(patterns=list(merged_patterns_map.values()))

    @classmethod
    def get_default_patterns(cls) -> "IntentPatternsConfig":
        """Get default intent patterns.

        Returns:
            IntentPatternsConfig with default patterns
        """
        # AIDEV-NOTE: Default patterns moved from INTENT_PATTERNS constant
        # AIDEV-QUESTION: Remove context hints in favor of combining keywords with entities devices/types found?
        # to enable YAML override without code changes
        return cls(
            patterns=[
                # Device control intents
                IntentPatternConfig(
                    intent_type=IntentType.DEVICE_ON,
                    keywords=["turn on", "switch on", "power on"],
                    context_hints=["light", "lights", "lamp", "fan", "plug", "device"],
                    negative_keywords=["off", "stop", "disable"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.DEVICE_OFF,
                    keywords=["turn off", "switch off", "power off"],
                    context_hints=["light", "lights", "lamp", "fan", "plug", "device"],
                    negative_keywords=["on", "start", "enable"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.DEVICE_SET,
                    keywords=["set", "adjust", "change"],
                    context_hints=["temperature", "thermostat", "brightness", "level", "percent", "%"],
                    negative_keywords=[],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.DEVICE_OPEN,
                    keywords=["open", "raise", "lift"],
                    context_hints=["curtain", "curtains", "blinds", "window", "door", "cover"],
                    negative_keywords=["close", "lower"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.DEVICE_CLOSE,
                    keywords=["close", "lower", "shut"],
                    context_hints=["curtain", "curtains", "blinds", "window", "door", "cover"],
                    negative_keywords=["open", "raise"],
                ),
                # Media control intents
                IntentPatternConfig(
                    intent_type=IntentType.MEDIA_PLAY,
                    keywords=["play", "resume", "continue"],
                    context_hints=["music", "song", "playlist", "media", "track", "album"],
                    negative_keywords=["stop", "pause"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.MEDIA_STOP,
                    keywords=["stop", "pause", "halt"],
                    context_hints=["music", "song", "playlist", "media", "playing"],
                    negative_keywords=["play", "start", "resume"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.MEDIA_NEXT,
                    keywords=["next", "skip"],
                    context_hints=["song", "track", "music", "picture", "playlist", "image"],
                    negative_keywords=["previous", "back"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.MEDIA_VOLUME_SET,
                    keywords=["set"],
                    context_hints=["volume"],
                    negative_keywords=[],
                ),
                # Query intents
                IntentPatternConfig(
                    intent_type=IntentType.QUERY_STATUS,
                    keywords=["what is the state", "check state"],
                    context_hints=[],
                    negative_keywords=[],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.QUERY_LIST,
                    keywords=["list", "what are", "which"],
                    context_hints=["devices", "lights", "windows", "all"],
                    negative_keywords=[],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.QUERY_TIME,
                    keywords=["what time", "current time", "what is the time"],
                    context_hints=[],
                    negative_keywords=[],
                ),
                # Scene and scheduling
                IntentPatternConfig(
                    intent_type=IntentType.SCENE_APPLY,
                    keywords=["activate scenery", "apply scenery", "scenery", "set scenery"],
                    context_hints=["scenery", "mode", "preset"],
                    negative_keywords=[],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.SCHEDULE_SET,
                    keywords=["schedule", "set", "remind"],
                    context_hints=["timer", "alarm"],
                    negative_keywords=["cancel", "stop", "delete"],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.SCHEDULE_CANCEL,
                    keywords=["cancel", "stop", "delete", "remove"],
                    context_hints=["schedule", "timer", "reminder", "alarm"],
                    negative_keywords=[],
                ),
                # System intents
                IntentPatternConfig(
                    intent_type=IntentType.SYSTEM_HELP,
                    keywords=["help", "how to", "what can"],
                    context_hints=["help", "commands", "do"],
                    negative_keywords=[],
                ),
                IntentPatternConfig(
                    intent_type=IntentType.SYSTEM_REFRESH,
                    keywords=["refresh", "reload", "update", "sync"],
                    context_hints=["devices", "state", "status", "system"],
                    negative_keywords=[],
                ),
            ]
        )


def load_intent_patterns(intent_patterns_path: str | Path | None = None) -> list[IntentPatternConfig]:
    """Load intent patterns from YAML file or return defaults.

    Args:
        intent_patterns_path: Optional path to custom intent patterns YAML file

    Returns:
        List of IntentPatternConfig objects
    """
    if intent_patterns_path:
        patterns_config = IntentPatternsConfig.from_yaml(intent_patterns_path)
    else:
        patterns_config = IntentPatternsConfig.get_default_patterns()

    return patterns_config.patterns
