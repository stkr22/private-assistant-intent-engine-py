import logging
import os
import pathlib
import sys
from typing import Annotated

import paho.mqtt.client as mqtt
import spacy
import typer
from private_assistant_commons.skill_config import load_config

from private_assistant_intent_engine import config, intent_engine

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

app = typer.Typer()


@app.command()
def start_intent_engine(
    config_path: Annotated[pathlib.Path, typer.Argument(envvar="PRIVATE_ASSISTANT_CONFIG_PATH")],
):
    config_obj = load_config(config_path, config_class=config.Config)
    intent_engine_obj = intent_engine.IntentEngine(
        mqtt_client=mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=config_obj.client_id,
            protocol=mqtt.MQTTv5,
        ),
        config_obj=config_obj,
        nlp_model=spacy.load(config_obj.spacy_model),
    )
    intent_engine_obj.run()


if __name__ == "__main__":
    start_intent_engine(config_path=pathlib.Path("./local_config.yaml"))
