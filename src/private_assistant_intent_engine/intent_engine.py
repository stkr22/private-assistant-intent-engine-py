import logging
import re

import aiomqtt
import spacy
from private_assistant_commons import messages, mqtt_tools

from private_assistant_intent_engine import config, text_tools


class IntentEngine:
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
        self.client_request_pattern: re.Pattern = mqtt_tools.mqtt_pattern_to_regex(
            self.config_obj.client_request_subscription
        )
        self.logger = logger
        self.command_split = re.compile(r"in addition|besides", flags=re.IGNORECASE)
        self.available_rooms = {room.lower() for room in config_obj.available_rooms}

    def analyze_text(self, client_request: messages.ClientRequest) -> list[messages.IntentAnalysisResult]:
        intent_analysis_results = []
        for command in self.command_split.split(client_request.text):
            doc = self.nlp_model(command)
            client_request.text = command
            intent_analysis_result = messages.IntentAnalysisResult.model_construct(client_request=client_request)
            intent_analysis_result.numbers = text_tools.extract_numbers_from_text(doc=doc)
            intent_analysis_result.verbs, intent_analysis_result.nouns = text_tools.extract_verbs_and_subjects(doc=doc)

            text_lower = command.lower()
            if "all rooms" in text_lower:
                found_rooms = list(self.available_rooms)
            else:
                found_rooms = [room for room in self.available_rooms if room in text_lower]
            intent_analysis_result.rooms.extend(found_rooms)

            intent_analysis_results.append(intent_analysis_result)

        return intent_analysis_results

    async def handle_intent_input_message(self, payload: str) -> None:
        client_request = messages.ClientRequest.model_validate_json(payload)
        intent_analysis_results = self.analyze_text(client_request=client_request)

        self.logger.info("Analysis successful, publishing results.")
        for result in intent_analysis_results:
            await self.mqtt_client.publish(self.config_obj.intent_result_topic, result.model_dump_json(), qos=1)

    def decode_message_payload(self, payload) -> str | None:
        """Decode the message payload if it is a suitable type."""
        if isinstance(payload, bytes | bytearray):
            return payload.decode("utf-8")
        if isinstance(payload, str):
            return payload
        self.logger.warning("Unexpected payload type: %s", type(payload))
        return None

    async def setup_subscriptions(self) -> None:
        """Set up MQTT topic subscriptions for the skill."""
        await self.mqtt_client.subscribe(topic=self.config_obj.client_request_subscription, qos=1)
        self.logger.info("Subscribed to intent analysis result topic: %s", self.config_obj.client_request_subscription)

    async def listen_to_messages(self, client: aiomqtt.Client) -> None:
        """Listen for incoming MQTT messages and handle them appropriately."""
        async for message in client.messages:
            self.logger.debug("Received message on topic %s", message.topic)

            if self.client_request_pattern.match(message.topic.value):
                payload_str = self.decode_message_payload(message.payload)
                if payload_str is not None:
                    await self.handle_intent_input_message(payload_str)
