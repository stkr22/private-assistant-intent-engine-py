"""Configuration models for the Private Assistant Intent Engine.

This module defines the Pydantic configuration model that validates
and manages all runtime settings for the intent engine, including
MQTT broker settings, NLP model configuration, and room detection.
"""

from pydantic import BaseModel, field_validator


class Config(BaseModel):
    """Configuration model for the Intent Engine.

    Validates and manages all runtime configuration including:
    - MQTT broker connection settings
    - Topic patterns for message routing
    - SpaCy NLP model configuration
    - Available rooms for detection

    All configuration is typically loaded from YAML files and validated
    at application startup to ensure proper system operation.

    Attributes:
        mqtt_server_host: MQTT broker hostname or IP address
        mqtt_server_port: MQTT broker port (typically 1883 for plain, 8883 for TLS)
        client_id: Unique identifier for this MQTT client
        client_request_subscription: MQTT topic pattern for incoming requests
        intent_result_topic: MQTT topic for publishing analysis results
        spacy_model: Name of SpaCy language model to load
        available_rooms: List of room names that can be detected in commands
    """

    # MQTT Broker Configuration
    mqtt_server_host: str = "localhost"
    mqtt_server_port: int = 1883
    client_id: str = "intent_engine"

    # MQTT Topic Configuration
    client_request_subscription: str = "assistant/comms_bridge/+/+/input"
    intent_result_topic: str = "assistant/intent_engine/result"

    # NLP Model Configuration
    spacy_model: str = "en_core_web_md"

    # Room Detection Configuration
    available_rooms: list[str] = ["living room", "kitchen", "bathroom"]

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

    @field_validator("available_rooms")
    @classmethod
    def validate_rooms_not_empty(cls, v: list[str]) -> list[str]:
        """Validate that available rooms list is not empty.

        Args:
            v: List of room names to validate

        Returns:
            Validated room list

        Raises:
            ValueError: If rooms list is empty
        """
        if not v:
            raise ValueError("Available rooms list cannot be empty")
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
