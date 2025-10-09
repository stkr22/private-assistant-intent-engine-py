"""Intent analysis engine for the Private Assistant ecosystem.

This module provides the core IntentEngine class that processes natural language
commands via MQTT, analyzes them using SpaCy NLP, and publishes structured results
for consumption by downstream skills.
"""

import logging
import re
from collections import defaultdict

import aiomqtt
from private_assistant_commons import ClassifiedIntent, ClientRequest, IntentRequest, mqtt_tools
from pydantic import ValidationError

from private_assistant_intent_engine import config, exceptions
from private_assistant_intent_engine.intent_classifier import IntentClassifier


class IntentEngine:
    """Core intent analysis engine for processing natural language commands.

    The IntentEngine serves as the central component for analyzing user commands
    in the Private Assistant ecosystem. It receives natural language text via MQTT,
    processes it using SpaCy NLP models, and publishes structured analysis results.

    This class handles:
    - MQTT message subscription and publishing
    - Natural language text analysis using SpaCy
    - Command splitting for compound requests
    - Room detection and entity extraction
    - Error handling and graceful degradation

    Args:
        config_obj: Configuration object containing MQTT and NLP settings
        mqtt_client: Async MQTT client for message handling
        logger: Logger instance for debugging and monitoring
        classifier: Intent classifier instance (initialized externally)
    """

    def __init__(
        self,
        config_obj: config.Config,
        mqtt_client: aiomqtt.Client,
        logger: logging.Logger,
        classifier: IntentClassifier,
    ):
        self.config_obj: config.Config = config_obj
        self.mqtt_client: aiomqtt.Client = mqtt_client

        # AIDEV-NOTE: MQTT topic pattern compilation for efficient message routing
        self.client_request_pattern: re.Pattern = mqtt_tools.mqtt_pattern_to_regex(
            self.config_obj.client_request_subscription
        )
        self.logger = logger

        # AIDEV-NOTE: Command splitting regex supports compound commands like "turn on lights, in addition set temp"
        # AIDEV-TODO: Investigate SpaCy's sentence segmentation with Sentencizer for more robust splitting
        self.command_split = re.compile(r"in addition,?|besides,?", flags=re.IGNORECASE)

        # AIDEV-NOTE: Intent classifier initialized externally with all dependencies
        self.classifier = classifier

        # AIDEV-NOTE: Device registry for pattern-based specific device matching (from classifier)
        self.device_registry = classifier.entity_extractor.device_registry

        # AIDEV-NOTE: Error metrics for monitoring failure rates
        self.error_metrics: dict[str, int] = defaultdict(int)

    def classify_intent(self, client_request: ClientRequest) -> list[ClassifiedIntent] | None:
        """Classify text into structured intents using the new classification system.

        This method uses the hybrid rule-based classifier to:
        1. Split compound commands using predefined separators
        2. Process each command with SpaCy NLP and intent classifier
        3. Extract intents with confidence scores
        4. Extract and normalize entities
        5. Build ClassifiedIntent objects for downstream consumption

        Args:
            client_request: Client request containing text and metadata

        Returns:
            List of ClassifiedIntent objects, one per command segment, or None if classification fails

        Example:
            Input: "Turn on the lights in kitchen"
            Output: [ClassifiedIntent(
                intent_type=IntentType.DEVICE_ON,
                confidence=1.0,
                entities={
                    "room": [Entity(type=ROOM, raw_text="kitchen", normalized_value="kitchen")],
                    "device_type": [Entity(type=DEVICE_TYPE, raw_text="lights", ...)]
                },
                raw_text="Turn on the lights in kitchen"
            )]
        """
        classified_intents = []

        try:
            # AIDEV-NOTE: Split compound commands to handle multiple intents in single message
            for command in [artifact.strip() for artifact in self.command_split.split(client_request.text)]:
                # Classify intent and get confidence scores
                intent_results = self.classifier.classify(command)

                if not intent_results:
                    # No intent matched, skip this command
                    self.logger.warning("No intent matched for command: %s", command)
                    continue

                # Get top intent and alternatives
                top_intent, top_confidence = intent_results[0]
                # AIDEV-NOTE: Filter alternative intents with confidence > 0.3 threshold
                min_alternative_confidence = 0.3
                alternative_intents = [
                    (intent, conf) for intent, conf in intent_results[1:] if conf > min_alternative_confidence
                ]

                # Extract entities (room detection happens inside EntityExtractor)
                entities = self.classifier.extract_entities(command)

                # Build ClassifiedIntent
                # Only include alternative_intents if there are any (Pydantic doesn't accept None)
                if alternative_intents:
                    classified_intent = ClassifiedIntent(
                        intent_type=top_intent,
                        confidence=top_confidence,
                        entities=entities,
                        alternative_intents=alternative_intents,
                        raw_text=command,
                    )
                else:
                    classified_intent = ClassifiedIntent(
                        intent_type=top_intent,
                        confidence=top_confidence,
                        entities=entities,
                        raw_text=command,
                    )

                classified_intents.append(classified_intent)

            return classified_intents if classified_intents else None

        except exceptions.TextAnalysisError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            self.logger.error("Unexpected error during intent classification: %s", str(e))
            self.error_metrics["unexpected_classification_errors"] += 1
            return None

    async def handle_intent_input_message(self, payload: str) -> None:
        """Handle incoming intent analysis requests from MQTT.

        Processes JSON payload containing client request, classifies intent using
        the new classification system, and publishes IntentRequest messages for skill consumption.

        Args:
            payload: JSON string containing ClientRequest data

        Note:
            Errors are logged but processing continues to maintain system stability.
            Individual message failures do not stop the message processing loop.
        """
        try:
            # Parse JSON payload with error handling
            try:
                client_request = ClientRequest.model_validate_json(payload)
            except ValidationError as e:
                self.logger.error("JSON validation failed for payload: %s", str(e))
                self.error_metrics["json_validation_errors"] += 1
                raise exceptions.JSONParsingError(f"Invalid JSON payload: {e!s}") from e
            except Exception as e:
                self.logger.error("JSON parsing failed: %s", str(e))
                self.error_metrics["json_parsing_errors"] += 1
                raise exceptions.JSONParsingError(f"Failed to parse JSON: {e!s}") from e

            # Classify intent and publish IntentRequest
            try:
                classified_intents = self.classify_intent(client_request=client_request)

                if not classified_intents:
                    self.logger.warning("No intent matched for request, skipping publishing")
                    return

                # AIDEV-NOTE: Publish IntentRequest for each classified intent
                self.logger.info(
                    "Intent classification successful, publishing %d IntentRequest(s).", len(classified_intents)
                )
                for classified_intent in classified_intents:
                    try:
                        intent_request = IntentRequest(
                            classified_intent=classified_intent,
                            client_request=client_request,
                        )
                        await self.mqtt_client.publish(
                            self.config_obj.intent_result_topic,
                            intent_request.model_dump_json(),
                            qos=1,
                        )
                    except Exception as e:
                        self.logger.error("Failed to publish IntentRequest: %s", str(e))
                        self.error_metrics["mqtt_publish_errors"] += 1

            except exceptions.TextAnalysisError as e:
                self.logger.warning("Intent classification failed: %s", str(e))
            except Exception as e:
                self.logger.error("Unexpected error during classification: %s", str(e))
                self.error_metrics["unexpected_classification_errors"] += 1

        except exceptions.JSONParsingError:
            # JSON errors are expected and handled, just return
            return
        except Exception as e:
            # Catch any unexpected errors to prevent loop termination
            self.logger.error("Unexpected error in message handler: %s", str(e))
            self.error_metrics["unexpected_handler_errors"] += 1

    def decode_message_payload(self, payload) -> str | None:
        """Decode MQTT message payload to UTF-8 string.

        Handles various payload types that may be received via MQTT,
        ensuring consistent string output for JSON parsing.

        Args:
            payload: Raw MQTT message payload (bytes, bytearray, or str)

        Returns:
            Decoded string payload or None if unsupported type

        Note:
            Unsupported payload types are logged as warnings.
        """
        if isinstance(payload, bytes | bytearray):
            return payload.decode("utf-8")
        if isinstance(payload, str):
            return payload
        self.logger.warning("Unexpected payload type: %s", type(payload))
        return None

    async def setup_subscriptions(self) -> None:
        """Configure MQTT topic subscriptions for intent analysis requests.

        Subscribes to the configured client request topic pattern to receive
        natural language commands from voice interfaces and other clients.

        Raises:
            MqttError: If subscription setup fails
        """
        await self.mqtt_client.subscribe(topic=self.config_obj.client_request_subscription, qos=1)
        self.logger.info("Subscribed to intent analysis result topic: %s", self.config_obj.client_request_subscription)

        # AIDEV-NOTE: Subscribe to device updates if registry is available
        if self.device_registry:
            await self.device_registry.setup_subscriptions()

    def get_error_metrics(self) -> dict[str, int]:
        """Get current error metrics for monitoring.

        Returns:
            Dictionary of error type to count mappings
        """
        return dict(self.error_metrics)

    def reset_error_metrics(self) -> None:
        """Reset error metrics counters."""
        self.error_metrics.clear()

    async def listen_to_messages(self, client: aiomqtt.Client) -> None:
        """Main message processing loop for handling MQTT messages.

        Continuously listens for incoming MQTT messages, filters by topic pattern,
        and dispatches appropriate handlers. This is the core event loop of the
        intent engine.

        Args:
            client: Active MQTT client connection

        Note:
            This method runs indefinitely until the MQTT connection is closed.
            Message processing errors are logged but don't stop the loop.
        """
        # AIDEV-NOTE: Compile device update pattern for efficient matching
        device_update_pattern = mqtt_tools.mqtt_pattern_to_regex("assistant/global_device_update")

        # AIDEV-NOTE: Main message processing loop - critical performance path
        async for message in client.messages:
            self.logger.debug("Received message on topic %s", message.topic)

            # AIDEV-NOTE: Handle device update notifications
            if self.device_registry and device_update_pattern.match(message.topic.value):
                payload_str = self.decode_message_payload(message.payload)
                if payload_str is not None:
                    try:
                        await self.device_registry.handle_device_update(payload_str)
                    except Exception as e:
                        self.logger.error("Error handling device update: %s", str(e))
                        self.error_metrics["device_update_errors"] += 1

            # Filter messages by topic pattern for efficient routing
            elif self.client_request_pattern.match(message.topic.value):
                payload_str = self.decode_message_payload(message.payload)
                if payload_str is not None:
                    # Error handling ensures message processing failures don't stop the loop
                    try:
                        await self.handle_intent_input_message(payload_str)
                    except Exception as e:
                        # This should never happen due to error handling in handle_intent_input_message
                        # But we add it as a safety net
                        self.logger.critical("Critical error in message processing (should not happen): %s", str(e))
                        self.error_metrics["critical_loop_errors"] += 1
