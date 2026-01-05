"""Shared test fixtures for intent engine tests."""

from uuid import uuid4

import pytest
from private_assistant_commons.database import DeviceType, GlobalDevice, Room


class MockDeviceRegistry:
    """Mock device registry for testing.

    Provides a minimal implementation of DeviceRegistry with predefined
    test data for device and type matching.
    """

    def __init__(self, device_update_topic: str = "assistant/global_device_update"):
        # Create device types
        self.light_type = DeviceType(id=uuid4(), name="light")
        self.spotify_type = DeviceType(id=uuid4(), name="spotify")
        self.cover_type = DeviceType(id=uuid4(), name="cover")
        self.switch_type = DeviceType(id=uuid4(), name="switch")

        self.device_types = [
            self.light_type,
            self.spotify_type,
            self.cover_type,
            self.switch_type,
        ]

        # Create devices
        self.ceiling_device = GlobalDevice(
            id=uuid4(),
            name="ceiling",
            device_type_id=self.light_type.id,
            pattern=["ceiling light"],
            device_attributes=None,
            skill_id=uuid4(),
        )

        self.spotify_device = GlobalDevice(
            id=uuid4(),
            name="Playlist",
            device_type_id=self.spotify_type.id,
            pattern=["playlist"],
            device_attributes=None,
            skill_id=uuid4(),
        )

        self.curtain_device = GlobalDevice(
            id=uuid4(),
            name="Curtain",
            device_type_id=self.cover_type.id,
            pattern=["curtain", "curtains"],
            device_attributes=None,
            skill_id=uuid4(),
        )

        self.shelf_device = GlobalDevice(
            id=uuid4(),
            name="shelf",
            device_type_id=self.switch_type.id,
            pattern=["shelf"],
            device_attributes=None,
            skill_id=uuid4(),
        )

        self.desk_device = GlobalDevice(
            id=uuid4(),
            name="desk",
            device_type_id=self.switch_type.id,
            pattern=["desk"],
            device_attributes=None,
            skill_id=uuid4(),
        )

        self.devices = [
            self.ceiling_device,
            self.spotify_device,
            self.curtain_device,
            self.shelf_device,
            self.desk_device,
        ]

        # Device update tracking
        self.device_update_topic = device_update_topic
        self.setup_subscriptions_called = False
        self.handle_device_update_calls = 0

    def match_devices(self, text: str) -> list[GlobalDevice]:
        """Match text against device patterns.

        Sorts patterns by length (longest first) to ensure most specific
        matches are found first. Returns all matching devices.

        Args:
            text: Lowercase text to match

        Returns:
            List of matched GlobalDevice objects (empty list if no matches)
        """
        matched_devices = []
        matched_device_ids = set()

        device: GlobalDevice
        for device in self.devices:
            # Sort patterns by length (longest first)
            for pattern in sorted(device.pattern, key=len, reverse=True):
                if pattern.lower() in text and device.id not in matched_device_ids:
                    matched_devices.append(device)
                    matched_device_ids.add(device.id)
                    break  # Don't check other patterns for this device
        return matched_devices

    def match_device_type(self, lemmatized_text: str) -> DeviceType | None:
        """Match lemmatized text against device types.

        Args:
            lemmatized_text: Already lemmatized lowercase text

        Returns:
            Matched DeviceType or None
        """
        device_type: DeviceType
        for device_type in self.device_types:
            if device_type.name.lower() == lemmatized_text.lower():
                return device_type
        return None

    async def setup_subscriptions(self) -> None:
        """Mock setup_subscriptions to track calls."""
        self.setup_subscriptions_called = True

    async def handle_device_update(self, _payload: str) -> None:
        """Mock handle_device_update to track calls."""
        self.handle_device_update_calls += 1


@pytest.fixture
def mock_device_registry():
    """Provide a mock device registry for testing."""
    return MockDeviceRegistry()


@pytest.fixture
def mock_rooms():
    """Provide mock Room objects for testing."""
    return [
        Room(id=uuid4(), name="living room"),
        Room(id=uuid4(), name="kitchen"),
        Room(id=uuid4(), name="bathroom"),
        Room(id=uuid4(), name="bedroom"),
    ]
