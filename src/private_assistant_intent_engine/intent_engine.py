"""Intent analysis engine for the Private Assistant ecosystem.

This module provides the core IntentEngine class that processes natural language
commands via MQTT, analyzes them using SpaCy NLP, and publishes structured results
for consumption by downstream skills.
"""

import logging
import re

import aiomqtt
import spacy
from private_assistant_commons import messages, mqtt_tools

from private_assistant_intent_engine import config, text_tools


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
        nlp_model: Loaded SpaCy language model for text processing
        logger: Logger instance for debugging and monitoring
    """

    def __init__(
        self,
        config_obj: config.Config,
        mqtt_client: aiomqtt.Client,
        nlp_model: spacy.language.Language,
        logger: logging.Logger,
    ):
        self.config_obj: config.Config = config_obj
        self.mqtt_client: aiomqtt.Client = mqtt_client
        self.nlp_model: spacy.language.Language = nlp_model

        # AIDEV-NOTE: MQTT topic pattern compilation for efficient message routing
        self.client_request_pattern: re.Pattern = mqtt_tools.mqtt_pattern_to_regex(
            self.config_obj.client_request_subscription
        )
        self.logger = logger

        # AIDEV-NOTE: Command splitting regex supports compound commands like "turn on lights, in addition set temp"
        self.command_split = re.compile(r"in addition,?|besides,?", flags=re.IGNORECASE)

        # AIDEV-NOTE: Precompute lowercase room set for efficient room detection
        self.available_rooms = {room.lower() for room in config_obj.available_rooms}

    def analyze_text(self, client_request: messages.ClientRequest) -> list[messages.IntentAnalysisResult]:
        """Analyze natural language text and extract linguistic elements.

        This method performs the core text analysis by:
        1. Splitting compound commands using predefined separators
        2. Processing each command segment with SpaCy NLP
        3. Extracting verbs, nouns, numbers, and room references
        4. Building structured analysis results for downstream consumption

        Args:
            client_request: Client request containing text and metadata

        Returns:
            List of IntentAnalysisResult objects, one per command segment

        Example:
            Input: "Turn on lights, in addition set temperature to 20"
            Output: [
                IntentAnalysisResult(verbs=["turn"], nouns=["lights"], ...),
                IntentAnalysisResult(verbs=["set"], nouns=["temperature"], numbers=[20], ...)
            ]
        """
        intent_analysis_results = []

        # AIDEV-NOTE: Split compound commands to handle multiple intents in single message
        for command in [artifact.strip() for artifact in self.command_split.split(client_request.text)]:
            # Process command with SpaCy NLP model
            doc = self.nlp_model(command)

            # Create analysis result preserving original client context
            intent_analysis_result = messages.IntentAnalysisResult.model_construct(
                client_request=client_request.model_copy(update={"text": command})
            )

            # Extract linguistic elements using text analysis tools
            intent_analysis_result.numbers = text_tools.extract_numbers_from_text(doc=doc)
            intent_analysis_result.verbs, intent_analysis_result.nouns = text_tools.extract_verbs_and_subjects(doc=doc)

            # AIDEV-NOTE: Room detection using simple string matching - may need refinement for complex cases
            text_lower = command.lower()
            if "all rooms" in text_lower:
                found_rooms = list(self.available_rooms)
            else:
                found_rooms = [room for room in self.available_rooms if room in text_lower]
            intent_analysis_result.rooms.extend(found_rooms)

            intent_analysis_results.append(intent_analysis_result)

        return intent_analysis_results

    async def handle_intent_input_message(self, payload: str) -> None:
        """Handle incoming intent analysis requests from MQTT.

        Processes JSON payload containing client request, analyzes the text,
        and publishes structured results back to MQTT for skill consumption.

        Args:
            payload: JSON string containing ClientRequest data

        Raises:
            ValidationError: If payload JSON is invalid or malformed

        Note:
            Errors are logged but processing continues to maintain system stability.
        """
        # AIDEV-TODO: Add error handling for JSON parsing failures
        client_request = messages.ClientRequest.model_validate_json(payload)
        intent_analysis_results = self.analyze_text(client_request=client_request)

        self.logger.info("Analysis successful, publishing results.")
        # AIDEV-NOTE: Publish each command segment result separately for parallel skill processing
        for result in intent_analysis_results:
            await self.mqtt_client.publish(self.config_obj.intent_result_topic, result.model_dump_json(), qos=1)

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
        # AIDEV-NOTE: Main message processing loop - critical performance path
        async for message in client.messages:
            self.logger.debug("Received message on topic %s", message.topic)

            # Filter messages by topic pattern for efficient routing
            if self.client_request_pattern.match(message.topic.value):
                payload_str = self.decode_message_payload(message.payload)
                if payload_str is not None:
                    # AIDEV-TODO: Add error handling to prevent message processing failures from stopping the loop
                    await self.handle_intent_input_message(payload_str)
