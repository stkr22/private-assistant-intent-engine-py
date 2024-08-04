import logging
import re
from collections.abc import Callable

import paho.mqtt.client as mqtt
import spacy
from private_assistant_commons import messages, mqtt_tools

from private_assistant_intent_engine import config, text_tools

logger = logging.getLogger(__name__)


class IntentEngine:
    def __init__(self, config_obj: config.Config, mqtt_client: mqtt.Client, nlp_model: spacy.language.Language):
        self.config_obj: config.Config = config_obj
        self.mqtt_client: mqtt.Client = mqtt_client
        self.mqtt_client.on_connect, self.mqtt_client.on_message = self.get_mqtt_functions()
        self.nlp_model: spacy.language.Language = nlp_model
        self.client_request_pattern: re.Pattern = mqtt_tools.mqtt_pattern_to_regex(
            self.config_obj.client_request_subscription
        )

    def get_mqtt_functions(self) -> tuple[Callable, Callable]:
        def on_connect(mqtt_client: mqtt.Client, user_data, flags, rc: int, properties):
            logger.info("Connected with result code %s", rc)
            mqtt_client.subscribe(
                [
                    (self.config_obj.client_request_subscription, mqtt.SubscribeOptions(qos=1)),
                ]
            )

        def on_message(mqtt_client: mqtt.Client, user_data, msg: mqtt.MQTTMessage):
            logger.debug("Received message %s", msg)
            if self.client_request_pattern.match(msg.topic):
                self.handle_intent_input_message(msg.payload.decode("utf-8"))

        return on_connect, on_message

    def analyze_text(self, client_request: messages.ClientRequest) -> messages.IntentAnalysisResult:
        doc = self.nlp_model(client_request.text)
        intent_analysis_result = messages.IntentAnalysisResult.model_construct(client_request=client_request)
        intent_analysis_result.numbers = text_tools.extract_numbers_from_text(doc=doc)
        intent_analysis_result.verbs, intent_analysis_result.nouns = text_tools.extract_verbs_and_subjects(doc=doc)
        return intent_analysis_result

    def handle_intent_input_message(self, payload: str) -> None:
        client_request = messages.ClientRequest.model_validate_json(payload)
        intent_analysis_result = self.analyze_text(client_request=client_request)
        logger.info("Analysis successful, publishing result.")
        self.mqtt_client.publish(self.config_obj.intent_result_topic, intent_analysis_result.model_dump_json(), qos=1)

    # Ensure to cleanly shutdown the timer when the application is exiting
    def shutdown(self) -> None:
        self.mqtt_client.disconnect()

    def run(self):
        try:
            self.mqtt_client.connect(self.config_obj.mqtt_server_host, self.config_obj.mqtt_server_port, 60)
            self.mqtt_client.loop_forever()
        finally:
            self.shutdown()
