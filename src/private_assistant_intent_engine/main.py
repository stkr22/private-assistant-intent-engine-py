import asyncio
import pathlib
from typing import Annotated

import aiomqtt
import spacy
import typer
from private_assistant_commons import async_typer, skill_logger
from private_assistant_commons.skill_config import load_config

from private_assistant_intent_engine import config, intent_engine

app = async_typer.AsyncTyper()


@app.command()
async def start_intent_engine(
    config_path: Annotated[pathlib.Path, typer.Argument(envvar="PRIVATE_ASSISTANT_CONFIG_PATH")],
):
    config_obj = load_config(config_path, config_class=config.Config)
    logger = skill_logger.SkillLogger.get_logger("Private Assistant Intent Engine")
    if config_obj.mqtt_server_host and config_obj.mqtt_server_port:
        client = aiomqtt.Client(config_obj.mqtt_server_host, port=config_obj.mqtt_server_port, logger=logger)
    else:
        raise ValueError("Unknown mqtt config option combination.")
    while True:
        try:
            async with client as mqtt_client:
                logger.info("Connected successfully to MQTT broker.")

                # Create and manage the task group context
                intent_engine_instance = intent_engine.IntentEngine(
                    mqtt_client=client,
                    config_obj=config_obj,
                    nlp_model=spacy.load(config_obj.spacy_model),
                    logger=logger,
                )

                # Set up subscriptions
                await intent_engine_instance.setup_subscriptions()

                # Add the MQTT listener task to the task group
                await intent_engine_instance.listen_to_messages(mqtt_client)

                # The context block will handle the lifecycle of the task group and all tasks inside it

        except aiomqtt.MqttError:
            logger.error("Connection lost; reconnecting in %d seconds...", 5, exc_info=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_intent_engine(config_path=pathlib.Path("./local_config.yaml")))
