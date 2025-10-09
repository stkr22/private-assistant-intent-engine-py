"""Shared test fixtures for intent engine tests."""

from uuid import uuid4

import pytest
from private_assistant_commons.database import DeviceType, GlobalDevice, Room


class MockDeviceRegistry:
    """Mock device registry for testing.

    Provides a minimal implementation of DeviceRegistry with predefined
    test data for device and type matching.
    """

    def __init__(self):
        # Create device types
        self.light_type = DeviceType(id=uuid4(), name="light")
        self.spotify_type = DeviceType(id=uuid4(), name="spotify")
        self.cover_type = DeviceType(id=uuid4(), name="cover")

        self.device_types = [
            self.light_type,
            self.spotify_type,
            self.cover_type,
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

        self.devices = [
            self.ceiling_device,
            self.spotify_device,
            self.curtain_device,
        ]

    def match_device(self, text: str) -> GlobalDevice | None:
        """Match text against device patterns.

        Sorts patterns by length (longest first) to ensure most specific
        matches are found first.

        Args:
            text: Lowercase text to match

        Returns:
            Matched GlobalDevice or None
        """
        for device in self.devices:
            # Sort patterns by length (longest first)
            for pattern in sorted(device.pattern, key=len, reverse=True):
                if pattern.lower() in text:
                    return device
        return None

    def match_device_type(self, lemmatized_text: str) -> DeviceType | None:
        """Match lemmatized text against device types.

        Args:
            lemmatized_text: Already lemmatized lowercase text

        Returns:
            Matched DeviceType or None
        """
        for device_type in self.device_types:
            if device_type.name.lower() == lemmatized_text.lower():
                return device_type
        return None


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
