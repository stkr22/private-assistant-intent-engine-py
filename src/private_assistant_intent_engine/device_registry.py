"""Device registry for pattern-based device matching.

This module provides the DeviceRegistry class for managing registered devices
from all skills in the Private Assistant ecosystem. It maintains a Postgres-backed
registry that enables the intent engine to match user commands to specific devices.
"""

import logging
from collections.abc import AsyncIterator

import aiomqtt
from private_assistant_commons.database import DeviceType, GlobalDevice
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class DeviceRegistry:
    """Async device registry with Postgres backend and MQTT updates.

    This class manages a registry of all devices across the Private Assistant
    ecosystem, enabling the intent engine to match user commands to specific
    devices using pattern matching.

    The registry:
    - Loads devices from Postgres on initialization (with room and skill relationships)
    - Subscribes to MQTT for continuous device updates
    - Provides async pattern matching for device extraction
    - Supports both exact substring and future fuzzy matching

    Database Schema:
    - GlobalDevice: Device records with foreign keys to Room and Skill
    - Room: Room definitions (bedroom, kitchen, etc.)
    - Skill: Skill definitions (switch-skill, media-skill, etc.)

    Args:
        postgres_connection_string: Async Postgres connection URL
        mqtt_client: Async MQTT client for device updates
        logger: Logger instance for debugging and monitoring

    """

    def __init__(
        self,
        postgres_connection_string: str,
        mqtt_client: aiomqtt.Client,
        logger: logging.Logger,
        device_update_topic: str = "assistant/global_device_update",
    ):
        """Initialize DeviceRegistry with database connection and MQTT client."""
        self.logger = logger
        self.mqtt_client = mqtt_client
        self.device_update_topic = device_update_topic

        # AIDEV-NOTE: Create async engine for Postgres access
        self.engine = create_async_engine(
            postgres_connection_string,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using
        )

        # AIDEV-NOTE: In-memory caches for fast pattern matching
        self.devices: list[GlobalDevice] = []
        self.device_types: list[DeviceType] = []

    async def initialize(self) -> None:
        """Initialize registry by loading devices and types from Postgres.

        This method should be called once during application startup to
        populate the in-memory caches from the database.
        """
        await self.refresh_devices()
        await self.refresh_device_types()
        self.logger.info(
            "DeviceRegistry initialized with %d devices and %d types", len(self.devices), len(self.device_types)
        )

    async def refresh_devices(self) -> None:
        """Refresh in-memory device cache from Postgres.

        This method queries all devices from the database and updates the
        in-memory cache. It's called on initialization and when receiving
        MQTT device update notifications.
        """
        async with AsyncSession(self.engine) as session:
            # AIDEV-NOTE: Load all devices from database
            results = await session.exec(select(GlobalDevice))
            self.devices = list(results.all())
            self.logger.debug("Refreshed device registry: %d devices loaded", len(self.devices))

    async def refresh_device_types(self) -> None:
        """Refresh in-memory device type cache from Postgres.

        This method queries all device types from the database and updates
        the in-memory cache. It's called on initialization and when receiving
        MQTT device update notifications.
        """
        async with AsyncSession(self.engine) as session:
            # AIDEV-NOTE: Load all device types from database
            results = await session.exec(select(DeviceType))
            self.device_types = list(results.all())
            self.logger.debug("Refreshed device types: %d types loaded", len(self.device_types))

    async def setup_subscriptions(self) -> None:
        """Subscribe to MQTT topic for device update notifications.

        Subscribes to the global_device_update channel to receive notifications
        when skills add, update, or remove devices from the registry.
        """
        await self.mqtt_client.subscribe(topic=self.device_update_topic, qos=1)
        self.logger.info("Subscribed to device updates on topic: %s", self.device_update_topic)

    async def handle_device_update(self, _payload: str) -> None:
        """Handle device update notifications from MQTT.

        When a device update notification is received, refresh both the device
        and device type caches from Postgres to ensure consistency.

        Args:
            _payload: MQTT message payload (unused, trigger-only)

        """
        self.logger.info("Received device update notification, refreshing registry")
        await self.refresh_devices()
        await self.refresh_device_types()

    def match_devices(self, text: str) -> list[GlobalDevice]:
        """Match text against device patterns using exact substring matching.

        Searches through all registered devices to find all devices whose
        patterns match the given text. Patterns are sorted by length (longest first)
        to ensure most specific matches are found first.

        Args:
            text: Lowercase text to match against device patterns

        Returns:
            List of matched GlobalDevice objects (empty list if no matches found)

        Note:
            Text should be lowercased before calling this method for
            case-insensitive matching.

        """
        # AIDEV-NOTE: Sort devices by longest pattern first for most specific matches
        # AIDEV-TODO: Implement fuzzy matching for better UX (issue to be created)
        matched_devices = []
        matched_device_ids = set()  # Track matched device IDs to prevent duplicates

        for device in self.devices:
            # Sort patterns by length (longest first) to match most specific
            for pattern in sorted(device.pattern, key=len, reverse=True):
                if pattern.lower() in text and device.id not in matched_device_ids:
                    # Get device type name for logging
                    type_name = next((dt.name for dt in self.device_types if dt.id == device.device_type_id), "unknown")
                    self.logger.debug(
                        "Matched device '%s' (type: %s) with pattern '%s'", device.name, type_name, pattern
                    )
                    matched_devices.append(device)
                    matched_device_ids.add(device.id)
                    break  # Don't check other patterns for this device
        return matched_devices

    def match_device_type(self, lemmatized_text: str) -> DeviceType | None:
        """Match lemmatized text against device types.

        Searches through all device types to find a type whose name matches
        the lemmatized text. Device types are stored in lowercase lemmatized
        form in the database.

        Args:
            lemmatized_text: Already lemmatized lowercase text (e.g., "light")

        Returns:
            Matched DeviceType or None if no match found

        Example:
            "lights" → lemmatized to "light" → matches DeviceType(name="light")

        """
        for device_type in self.device_types:
            if device_type.name.lower() == lemmatized_text.lower():
                self.logger.debug("Matched device type '%s'", device_type.name)
                return device_type
        return None

    async def listen_to_device_updates(self, client: aiomqtt.Client) -> AsyncIterator[aiomqtt.Message]:
        """Listen for device update messages and yield them.

        This async generator filters MQTT messages for device updates and
        yields them for processing by the main message loop.

        Args:
            client: Active MQTT client connection

        Yields:
            MQTT messages from the device update topic

        """
        async for message in client.messages:
            if message.topic.matches(self.device_update_topic):
                yield message

    async def close(self) -> None:
        """Clean up resources on shutdown.

        Disposes of the async database engine and releases all connections.
        Should be called during application shutdown.
        """
        await self.engine.dispose()
        self.logger.info("DeviceRegistry closed")
