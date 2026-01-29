"""Shared test fixtures for intent engine tests."""

from uuid import uuid4

import pytest
from private_assistant_commons import IntentType
from private_assistant_commons.database import DeviceType, GlobalDevice, Room

from private_assistant_intent_engine.intent_patterns import IntentPatternConfig


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


class MockPatternRegistry:
    """Mock pattern registry for testing.

    Provides a minimal implementation of IntentPatternsRegistry with
    regex-based patterns for testing.
    """

    def __init__(self, pattern_update_topic: str = "assistant/intent_pattern_update"):
        # Create test patterns using new regex-based format
        self.patterns = [
            # Device control
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_ON,
                keywords=[
                    (r"turn\s+on(\s+(the|my))?", True),
                    (r"switch\s+on", True),
                    (r"power\s+on", True),
                ],
                negative_keywords=[("off", False), ("stop", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_OFF,
                keywords=[
                    (r"turn\s+off(\s+(the|my))?", True),
                    (r"switch\s+off", True),
                    (r"power\s+off", True),
                ],
                negative_keywords=[("on", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_SET,
                keywords=[
                    (r"(set|adjust|change)\s+(the\s+)?(temperature|temp)", True),
                    (r"(set|adjust|change)\s+(the\s+)?(brightness|level)", True),
                    ("set", False),
                ],
                negative_keywords=[],
            ),
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_OPEN,
                keywords=[
                    (r"open(\s+(the|my))?", True),
                    (r"(raise|lift)(\s+(the|my))?", True),
                ],
                negative_keywords=[("close", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_CLOSE,
                keywords=[
                    (r"close(\s+(the|my))?", True),
                    (r"(lower|shut)(\s+(the|my))?", True),
                ],
                negative_keywords=[("open", False)],
            ),
            # Media control
            IntentPatternConfig(
                intent_type=IntentType.MEDIA_PLAY,
                keywords=[
                    (r"play(\s+(the|my|some))?", True),
                    (r"(resume|continue)(\s+(the|my))?", True),
                ],
                negative_keywords=[("stop", False), ("pause", False), ("next", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.MEDIA_STOP,
                keywords=[
                    (r"(stop|pause|halt)(\s+(the|my))?", True),
                ],
                negative_keywords=[("play", False), ("resume", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.MEDIA_NEXT,
                keywords=[
                    (r"(next|skip)(\s+(song|track|music))?", True),
                ],
                negative_keywords=[("previous", False), ("back", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.MEDIA_VOLUME_SET,
                keywords=[
                    (r"(set|change|adjust)\s+(the\s+)?volume", True),
                    (r"volume\s+(to|at)", True),
                ],
                negative_keywords=[],
            ),
            # Query intents
            IntentPatternConfig(
                intent_type=IntentType.DEVICE_QUERY,
                keywords=[
                    (r"what\s+is\s+the\s+state", True),
                    (r"check\s+state", True),
                    ("status", False),
                ],
                negative_keywords=[],
            ),
            IntentPatternConfig(
                intent_type=IntentType.DATA_QUERY,
                keywords=[
                    (r"what\s+(time|are|is)", True),
                    (r"current\s+time", True),
                    ("list", False),
                    ("which", False),
                ],
                negative_keywords=[],
            ),
            IntentPatternConfig(
                intent_type=IntentType.MEDIA_QUERY,
                keywords=[
                    (r"what\s+(is\s+)?(playing|song)", True),
                    (r"current\s+(song|track)", True),
                ],
                negative_keywords=[],
            ),
            # Scene and scheduling
            IntentPatternConfig(
                intent_type=IntentType.SCENE_APPLY,
                keywords=[
                    (r"(activate|apply|set)\s+(the\s+)?(scene|scenery|mode)", True),
                    ("scenery", False),
                ],
                negative_keywords=[],
            ),
            IntentPatternConfig(
                intent_type=IntentType.SCHEDULE_SET,
                keywords=[
                    (r"(schedule|set)\s+(a|an|the)?\s+(timer|alarm|reminder)", True),
                    (r"remind\s+(me)?", True),
                ],
                negative_keywords=[("cancel", False), ("delete", False)],
            ),
            IntentPatternConfig(
                intent_type=IntentType.SCHEDULE_CANCEL,
                keywords=[
                    (r"(cancel|stop|delete|remove)\s+(the\s+)?(schedule|timer|reminder)", True),
                ],
                negative_keywords=[],
            ),
        ]
        self.pattern_update_topic = pattern_update_topic
        self.setup_subscriptions_called = False
        self.handle_pattern_update_calls = 0

    async def setup_subscriptions(self) -> None:
        """Mock setup_subscriptions to track calls."""
        self.setup_subscriptions_called = True

    async def handle_pattern_update(self, _payload: str) -> None:
        """Mock handle_pattern_update to track calls."""
        self.handle_pattern_update_calls += 1


@pytest.fixture
def mock_pattern_registry():
    """Provide a mock pattern registry for testing."""
    return MockPatternRegistry()


@pytest.fixture
def mock_rooms():
    """Provide mock Room objects for testing."""
    return [
        Room(id=uuid4(), name="living room"),
        Room(id=uuid4(), name="kitchen"),
        Room(id=uuid4(), name="bathroom"),
        Room(id=uuid4(), name="bedroom"),
    ]
