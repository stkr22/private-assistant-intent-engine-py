import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Config(BaseModel):
    mqtt_server_host: str = "localhost"
    mqtt_server_port: int = 1883
    client_id: str = "intent_engine"
    client_request_subscription: str = "assistant/comms_bridge/+/+/input"
    intent_result_topic: str = "assistant/intent_engine/result"
    spacy_model: str = "en_core_web_md"
