"""Configuration model for the Private Assistant Intent Engine.

This module defines the runtime configuration using pydantic-settings,
enabling environment variable support and validation for all application
settings including topic patterns, NLP models, and intent patterns.

MQTT broker configuration is handled separately via MqttConfig from
private_assistant_commons, which reads from MQTT_* environment variables.
"""

from private_assistant_commons import SkillConfig
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_default_device_update_topic() -> str:
    """Get device update topic from SkillConfig.

    Returns:
        The configured device update topic from SkillConfig

    """
    return SkillConfig().device_update_topic


def _get_default_intent_result_topic() -> str:
    """Get intent analysis result topic from SkillConfig.

    Returns:
        The configured intent analysis result topic from SkillConfig

    """
    return SkillConfig().intent_analysis_result_topic


class Config(BaseSettings):
    """Runtime configuration for the Intent Engine.

    Validates and manages all runtime configuration including:
    - Topic patterns for message routing
    - SpaCy NLP model configuration
    - Intent pattern customization

    Configuration can be loaded from:
    - Environment variables (with INTENT_ENGINE_ prefix)
    - .env file
    - Direct instantiation with parameters

    Attributes:
        client_request_subscription: MQTT topic pattern for incoming requests
        intent_result_topic: MQTT topic for publishing analysis results
        device_update_topic: MQTT topic for device update notifications
        spacy_model: Name of SpaCy language model to load
        intent_patterns_path: Optional path to custom intent patterns YAML file

    """

    model_config = SettingsConfigDict(
        env_prefix="INTENT_ENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MQTT Topic Configuration
    client_request_subscription: str = "assistant/ground_station/+/+/input"
    intent_result_topic: str = Field(default_factory=_get_default_intent_result_topic)
    device_update_topic: str = Field(default_factory=_get_default_device_update_topic)

    # NLP Model Configuration
    spacy_model: str = "en_core_web_md"

    # Intent Pattern Configuration
    intent_patterns_path: str | None = None

    @field_validator("spacy_model")
    @classmethod
    def validate_spacy_model(cls, v: str) -> str:
        """Validate SpaCy model name format.

        Args:
            v: SpaCy model name to validate

        Returns:
            Validated model name

        Raises:
            ValueError: If model name is empty or invalid

        """
        if not v or not isinstance(v, str):
            raise ValueError("SpaCy model name must be a non-empty string")
        return v
