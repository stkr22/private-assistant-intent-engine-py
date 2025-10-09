"""Configuration model for the Private Assistant Intent Engine.

This module defines the runtime configuration using pydantic-settings,
enabling environment variable support and validation for all application
settings including MQTT broker, NLP models, and topic patterns.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Runtime configuration for the Intent Engine.

    Validates and manages all runtime configuration including:
    - MQTT broker connection settings
    - Topic patterns for message routing
    - SpaCy NLP model configuration
    - Intent pattern customization

    Configuration can be loaded from:
    - Environment variables (with INTENT_ENGINE_ prefix)
    - .env file
    - Direct instantiation with parameters

    Attributes:
        mqtt_server_host: MQTT broker hostname or IP address
        mqtt_server_port: MQTT broker port (typically 1883 for plain, 8883 for TLS)
        client_id: Unique identifier for this MQTT client
        client_request_subscription: MQTT topic pattern for incoming requests
        intent_result_topic: MQTT topic for publishing analysis results
        spacy_model: Name of SpaCy language model to load
        intent_patterns_path: Optional path to custom intent patterns YAML file
    """

    model_config = SettingsConfigDict(
        env_prefix="INTENT_ENGINE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # MQTT Broker Configuration
    mqtt_server_host: str = "localhost"
    mqtt_server_port: int = 1883
    client_id: str = "intent_engine"

    # MQTT Topic Configuration
    client_request_subscription: str = "assistant/comms_bridge/+/+/input"
    intent_result_topic: str = "assistant/intent_engine/result"

    # NLP Model Configuration
    spacy_model: str = "en_core_web_md"

    # Intent Pattern Configuration
    intent_patterns_path: str | None = None

    @field_validator("mqtt_server_port")
    @classmethod
    def validate_mqtt_port(cls, v: int) -> int:
        """Validate MQTT port is in valid range.

        Args:
            v: Port number to validate

        Returns:
            Validated port number

        Raises:
            ValueError: If port is outside valid range (1-65535)
        """
        max_port = 65535
        if not 1 <= v <= max_port:
            raise ValueError("MQTT port must be between 1 and 65535")
        return v

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
