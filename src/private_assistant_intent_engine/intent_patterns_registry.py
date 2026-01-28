"""Intent patterns registry with database backend and MQTT updates.

This module provides the IntentPatternsRegistry class for managing intent
patterns from Postgres with MQTT-based cache refresh, following the same
pattern as DeviceRegistry.
"""

import logging

import aiomqtt
from private_assistant_commons import IntentType
from private_assistant_commons.database import (
    IntentPattern,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from private_assistant_intent_engine.intent_patterns import IntentPatternConfig


class IntentPatternsRegistry:
    """Async intent patterns registry with Postgres backend and MQTT updates.

    This class manages intent patterns from database with in-memory caching,
    subscribing to MQTT for real-time pattern updates.

    The registry:
    - Loads patterns from Postgres on initialization
    - Subscribes to MQTT for continuous pattern updates
    - Provides in-memory cache for fast classification
    - Raises RuntimeError if database is empty (fail-fast deployment safety)

    Args:
        postgres_connection_string: Async Postgres connection URL
        mqtt_client: Async MQTT client for pattern updates
        logger: Logger instance for debugging and monitoring
        pattern_update_topic: MQTT topic for pattern updates

    """

    def __init__(
        self,
        postgres_connection_string: str,
        mqtt_client: aiomqtt.Client,
        logger: logging.Logger,
        pattern_update_topic: str = "assistant/intent_pattern_update",
    ):
        """Initialize IntentPatternsRegistry with database connection."""
        self.logger = logger
        self.mqtt_client = mqtt_client
        self.pattern_update_topic = pattern_update_topic

        # AIDEV-NOTE: Create async engine for Postgres access
        self.engine = create_async_engine(
            postgres_connection_string,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using
        )

        # AIDEV-NOTE: In-memory cache for fast pattern matching
        self.patterns: list[IntentPatternConfig] = []

    async def initialize(self) -> None:
        """Initialize registry by loading patterns from Postgres.

        Raises:
            RuntimeError: If database is empty (no patterns found)

        """
        await self.refresh_patterns()

        # AIDEV-NOTE: Fail-fast if database is empty
        if not self.patterns:
            raise RuntimeError(
                "Intent patterns database is empty. Run migration script: "
                "uv run python scripts/migrate_intent_patterns_to_db.py"
            )

        self.logger.info("IntentPatternsRegistry initialized with %d patterns", len(self.patterns))

    async def refresh_patterns(self) -> None:
        """Refresh in-memory pattern cache from Postgres.

        Loads all enabled patterns with keywords and hints via JOINs,
        converting to IntentPatternConfig for classifier compatibility.
        """
        async with AsyncSession(self.engine) as session:
            # AIDEV-NOTE: Load patterns with relationships (SQLModel handles JOINs)
            statement = select(IntentPattern).where(IntentPattern.enabled).order_by(IntentPattern.priority.desc())  # type: ignore[attr-defined]
            results = await session.exec(statement)
            db_patterns = list(results.all())

            # AIDEV-NOTE: Convert to IntentPatternConfig
            self.patterns = []
            for db_pattern in db_patterns:
                # Separate primary and negative keywords
                primary_keywords = [kw.keyword for kw in db_pattern.keywords if kw.keyword_type == "primary"]
                negative_keywords = [kw.keyword for kw in db_pattern.keywords if kw.keyword_type == "negative"]

                # Extract hints
                context_hints = [hint.hint for hint in db_pattern.hints]

                # Validate intent_type
                try:
                    intent_type = IntentType(db_pattern.intent_type)
                except ValueError:
                    self.logger.warning("Invalid intent_type '%s', skipping pattern", db_pattern.intent_type)
                    continue

                # AIDEV-NOTE: Skip patterns without keywords
                if not primary_keywords:
                    self.logger.warning("Pattern %s has no primary keywords, skipping", db_pattern.intent_type)
                    continue

                # Create IntentPatternConfig
                pattern_config = IntentPatternConfig(
                    intent_type=intent_type,
                    keywords=primary_keywords,
                    context_hints=context_hints,
                    negative_keywords=negative_keywords,
                )
                self.patterns.append(pattern_config)

            self.logger.debug("Refreshed pattern registry: %d patterns loaded", len(self.patterns))

    async def setup_subscriptions(self) -> None:
        """Subscribe to MQTT topic for pattern update notifications."""
        await self.mqtt_client.subscribe(topic=self.pattern_update_topic, qos=1)
        self.logger.info("Subscribed to pattern updates on topic: %s", self.pattern_update_topic)

    async def handle_pattern_update(self, _payload: str) -> None:
        """Handle pattern update notifications from MQTT.

        When a pattern update notification is received, refresh the
        pattern cache from Postgres to ensure consistency.

        Args:
            _payload: MQTT message payload (unused, trigger-only)

        """
        self.logger.info("Received pattern update notification, refreshing registry")
        await self.refresh_patterns()

    async def close(self) -> None:
        """Clean up resources on shutdown.

        Disposes of the async database engine and releases all connections.
        Should be called during application shutdown.
        """
        await self.engine.dispose()
        self.logger.info("IntentPatternsRegistry closed")
