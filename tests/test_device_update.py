"""Tests for device update handling in the intent engine.

Tests verify that:
1. Device update subscriptions use the configured topic
2. Device update notifications are processed correctly
3. Device registry is refreshed on updates
4. Logging is at the correct level
5. Error handling works properly
"""

from unittest.mock import AsyncMock, Mock

import pytest
from private_assistant_commons import SkillConfig

from private_assistant_intent_engine import config
from private_assistant_intent_engine.device_registry import DeviceRegistry


@pytest.mark.asyncio
async def test_device_registry_init_with_custom_topic():
    """Verify DeviceRegistry accepts and stores custom device_update_topic."""
    custom_topic = "custom/device/updates"
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
        device_update_topic=custom_topic,
    )

    assert registry.device_update_topic == custom_topic


@pytest.mark.asyncio
async def test_device_registry_init_with_default_topic():
    """Verify DeviceRegistry uses correct default when no topic provided."""
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
    )

    # Should use default value
    assert registry.device_update_topic == "assistant/global_device_update"


@pytest.mark.asyncio
async def test_device_registry_setup_subscriptions_uses_configured_topic():
    """Verify setup_subscriptions() subscribes to the configured topic."""
    custom_topic = "test/device/topic"
    mqtt_client_mock = AsyncMock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
        device_update_topic=custom_topic,
    )

    await registry.setup_subscriptions()

    # Verify MQTT subscription was called with the custom topic
    mqtt_client_mock.subscribe.assert_called_once_with(topic=custom_topic, qos=1)

    # Verify info-level logging
    logger_mock.info.assert_called_once()
    log_call_args = logger_mock.info.call_args[0]
    assert custom_topic in log_call_args[1]


@pytest.mark.asyncio
async def test_device_registry_handle_device_update_logs_at_info_level():
    """Verify handle_device_update() logs at info level, not debug."""
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
    )

    # Mock the refresh methods to avoid database calls
    registry.refresh_devices = AsyncMock()
    registry.refresh_device_types = AsyncMock()

    await registry.handle_device_update("test_payload")

    # Verify info-level logging was called
    logger_mock.info.assert_called_once()
    log_message = logger_mock.info.call_args[0][0]
    assert "Received device update notification" in log_message

    # Verify debug logging was NOT called
    logger_mock.debug.assert_not_called()

    # Verify refresh methods were called
    registry.refresh_devices.assert_called_once()
    registry.refresh_device_types.assert_called_once()


@pytest.mark.asyncio
async def test_device_registry_handle_device_update_refreshes_registry():
    """Verify handle_device_update() triggers cache refresh."""
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
    )

    # Mock the refresh methods
    registry.refresh_devices = AsyncMock()
    registry.refresh_device_types = AsyncMock()

    # Call handle_device_update
    await registry.handle_device_update("ignored_payload")

    # Verify both refresh methods were called
    registry.refresh_devices.assert_called_once()
    registry.refresh_device_types.assert_called_once()


@pytest.mark.asyncio
async def test_config_device_update_topic_default_value():
    """Verify Config() has device_update_topic with correct default."""
    config_obj = config.Config()

    # Should match the SkillConfig default
    expected_default = SkillConfig().device_update_topic
    assert config_obj.device_update_topic == expected_default


@pytest.mark.asyncio
async def test_config_device_update_topic_environment_variable(monkeypatch):
    """Verify INTENT_ENGINE_DEVICE_UPDATE_TOPIC env var overrides default."""
    custom_topic = "env/override/topic"
    monkeypatch.setenv("INTENT_ENGINE_DEVICE_UPDATE_TOPIC", custom_topic)

    config_obj = config.Config()

    assert config_obj.device_update_topic == custom_topic


@pytest.mark.asyncio
async def test_device_update_error_handling():
    """Verify errors during device update are handled gracefully."""
    mqtt_client_mock = Mock()
    logger_mock = Mock()

    registry = DeviceRegistry(
        postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
        mqtt_client=mqtt_client_mock,
        logger=logger_mock,
    )

    # Mock refresh_devices to raise an exception
    registry.refresh_devices = AsyncMock(side_effect=Exception("Database connection failed"))
    registry.refresh_device_types = AsyncMock()

    # handle_device_update should propagate the exception
    with pytest.raises(Exception, match="Database connection failed"):
        await registry.handle_device_update("test_payload")

    # Info logging should still have been called before the error
    logger_mock.info.assert_called_once()


@pytest.mark.asyncio
async def test_device_update_with_different_topics():
    """Verify registry works correctly with various topic configurations."""
    test_topics = [
        "assistant/global_device_update",  # Default
        "test/device/updates",
        "home/automation/device_changes",
        "iot/+/device/update",  # With wildcard
    ]

    for topic in test_topics:
        mqtt_client_mock = AsyncMock()
        logger_mock = Mock()

        registry = DeviceRegistry(
            postgres_connection_string="postgresql+asyncpg://test:test@localhost/test",
            mqtt_client=mqtt_client_mock,
            logger=logger_mock,
            device_update_topic=topic,
        )

        await registry.setup_subscriptions()

        # Verify subscription uses the correct topic
        mqtt_client_mock.subscribe.assert_called_once_with(topic=topic, qos=1)

        # Verify logging mentions the topic
        assert logger_mock.info.called
        log_call_args = logger_mock.info.call_args[0]
        assert topic in str(log_call_args)
