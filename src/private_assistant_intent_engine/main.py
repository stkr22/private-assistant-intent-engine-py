"""Main entry point and CLI for the Private Assistant Intent Engine.

This module provides the command-line interface and application startup logic
for the intent engine. It handles configuration loading, MQTT connection
management, and the main application lifecycle.
"""

import asyncio
import pathlib
from typing import Annotated

import aiomqtt
import spacy
import typer
from private_assistant_commons import skill_logger
from private_assistant_commons.database import Room
from private_assistant_commons.skill_config import PostgresConfig, load_config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from private_assistant_intent_engine import config, intent_engine
from private_assistant_intent_engine.device_registry import DeviceRegistry
from private_assistant_intent_engine.intent_classifier import IntentClassifier
from private_assistant_intent_engine.intent_patterns import load_intent_patterns

app = typer.Typer()


@app.command()
def main(config_path: Annotated[pathlib.Path, typer.Argument(envvar="PRIVATE_ASSISTANT_CONFIG_PATH")]) -> None:
    """Start the Private Assistant Intent Engine.

    Args:
        config_path: Path to YAML configuration file. Can be set via
                    PRIVATE_ASSISTANT_CONFIG_PATH environment variable.
    """
    asyncio.run(start_intent_engine(config_path))


async def start_intent_engine(config_path: pathlib.Path) -> None:
    """Initialize and start the intent engine with configuration.

    This function handles the complete application lifecycle:
    1. Loads and validates configuration from YAML file
    2. Sets up logging
    3. Establishes MQTT connection with reconnection logic
    4. Loads SpaCy NLP model
    5. Creates and runs the IntentEngine instance

    Args:
        config_path: Path to YAML configuration file

    Raises:
        ValueError: If MQTT configuration is invalid
        OSError: If SpaCy model cannot be loaded
        ConfigValidationError: If configuration validation fails
    """
    # AIDEV-NOTE: Load and validate configuration from YAML file
    config_obj = load_config(config_path, config_class=config.Config)
    logger = skill_logger.SkillLogger.get_logger("Private Assistant Intent Engine")

    # AIDEV-NOTE: Validate MQTT configuration and create client
    if config_obj.mqtt_server_host and config_obj.mqtt_server_port:
        client = aiomqtt.Client(config_obj.mqtt_server_host, port=config_obj.mqtt_server_port, logger=logger)
    else:
        raise ValueError("Invalid MQTT configuration: host and port must be specified.")
    # AIDEV-NOTE: Main application loop with automatic MQTT reconnection
    while True:
        try:
            async with client as mqtt_client:
                logger.info("Connected successfully to MQTT broker.")

                # AIDEV-NOTE: Load SpaCy model at connection time to handle failures gracefully
                nlp_model = spacy.load(config_obj.spacy_model)
                logger.info("Loaded SpaCy model: %s", config_obj.spacy_model)

                # AIDEV-NOTE: Get Postgres connection string from environment
                postgres_config = PostgresConfig.from_env()
                connection_string = postgres_config.connection_string_async

                # AIDEV-NOTE: Create async engine for database operations
                engine = create_async_engine(connection_string)

                # AIDEV-NOTE: Load rooms from database for entity extraction
                async with AsyncSession(engine) as session:
                    result = await session.exec(select(Room))
                    rooms = list(result.all())
                    logger.info("Loaded %d rooms from database", len(rooms))

                # AIDEV-NOTE: Load intent patterns from YAML or use defaults
                intent_patterns = load_intent_patterns(config_obj.intent_patterns_path)
                logger.info("Loaded %d intent patterns", len(intent_patterns))

                # AIDEV-NOTE: Initialize device registry for pattern-based device matching
                device_registry = DeviceRegistry(
                    postgres_connection_string=connection_string,
                    mqtt_client=client,
                    logger=logger,
                )
                await device_registry.initialize()
                await device_registry.setup_subscriptions()

                # AIDEV-NOTE: Initialize intent classifier with all dependencies
                classifier = IntentClassifier(
                    config_obj=config_obj,
                    nlp_model=nlp_model,
                    intent_patterns=intent_patterns,
                    rooms=rooms,
                    device_registry=device_registry,
                )

                # Create intent engine instance with classifier
                intent_engine_instance = intent_engine.IntentEngine(
                    mqtt_client=client,
                    config_obj=config_obj,
                    logger=logger,
                    classifier=classifier,
                )

                # Set up MQTT topic subscriptions
                await intent_engine_instance.setup_subscriptions()
                logger.info("Intent engine ready for message processing.")

                # Start main message processing loop
                await intent_engine_instance.listen_to_messages(mqtt_client)

        except aiomqtt.MqttError:
            logger.error("MQTT connection lost; reconnecting in %d seconds...", 5, exc_info=True)
            await asyncio.sleep(5)
        except OSError as e:
            logger.error("Failed to load SpaCy model '%s': %s", config_obj.spacy_model, e)
            raise
        except Exception as e:
            logger.error("Unexpected error in intent engine: %s", e, exc_info=True)
            await asyncio.sleep(5)


if __name__ == "__main__":
    app()
