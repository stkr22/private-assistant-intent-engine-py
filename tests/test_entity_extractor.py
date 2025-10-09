"""Tests for EntityExtractor - enhanced entity extraction with linking."""

import pytest
import spacy
from private_assistant_commons import EntityType

from private_assistant_intent_engine.entity_extractor import EntityExtractor


@pytest.fixture
def nlp_model():
    """Load SpaCy model for testing."""
    return spacy.load("en_core_web_md")


@pytest.fixture
def entity_extractor(nlp_model, mock_rooms) -> EntityExtractor:
    """Create EntityExtractor instance for testing (without registry)."""
    return EntityExtractor(nlp_model, mock_rooms)


@pytest.fixture
def entity_extractor_with_registry(nlp_model, mock_rooms, mock_device_registry) -> EntityExtractor:
    """Create EntityExtractor instance with mock device registry."""
    return EntityExtractor(nlp_model, mock_rooms, device_registry=mock_device_registry)


class TestEntityExtractor:
    """Test suite for EntityExtractor."""

    def test_spotify_playlist_extraction_with_linking(self, entity_extractor_with_registry: EntityExtractor):
        """Test: 'Please play spotify playlist one.'

        Expected:
        - Device from registry: name="Playlist", type="spotify"
        - NUMBER: 1 (linked to device)
        """
        text = "Please play spotify playlist one"
        entities = entity_extractor_with_registry.extract(text)

        # Should extract device from registry
        assert EntityType.DEVICE.value in entities
        devices = entities[EntityType.DEVICE.value]
        assert len(devices) > 0
        # Verify registry device was matched
        assert devices[0].normalized_value == "Playlist"
        assert devices[0].metadata.get("device_type") == "spotify"
        assert devices[0].metadata.get("is_generic") is False
        assert devices[0].metadata.get("device_id")  # Check device_id present

        # Should extract NUMBER (not MEDIA_ID)
        assert EntityType.NUMBER.value in entities
        numbers = entities[EntityType.NUMBER.value]
        assert len(numbers) > 0
        assert numbers[0].normalized_value == 1.0
        assert numbers[0].linked_to == [devices[0].id]

    def test_cover_type_with_modifier_extraction(self, entity_extractor_with_registry: EntityExtractor):
        """Test: 'Please open covers'

        Expected:
        - Intent -> Device_open
        - Entity -> device_type: cover (generic type match)
        """
        text = "Please open covers"
        entities = entity_extractor_with_registry.extract(text)

        # Should extract generic device type "cover" (lemmatized from "covers")
        assert EntityType.DEVICE.value in entities
        devices = entities[EntityType.DEVICE.value]
        assert len(devices) == 1
        assert devices[0].normalized_value == "cover"
        assert devices[0].metadata.get("device_type") == "cover"
        assert devices[0].metadata.get("is_generic") is True
        assert devices[0].metadata.get("quantifier") == "all"

    def test_curtain_device_without_modifier_extraction(self, entity_extractor_with_registry: EntityExtractor):
        """Test: 'Please open curtain'

        Expected:
        - Intent -> Device_open
        - Entity -> device: curtain
        """
        text = "Please open curtain"
        entities = entity_extractor_with_registry.extract(text)

        # Should extract device "curtain"
        assert EntityType.DEVICE.value in entities
        devices = entities[EntityType.DEVICE.value]
        assert len(devices) == 1
        assert devices[0].normalized_value == "Curtain"
        assert devices[0].metadata.get("device_type") == "cover"
        assert devices[0].metadata.get("is_generic") is False
        assert devices[0].metadata.get("quantifier") is None

    def test_timer_with_duration_and_linking(self, entity_extractor: EntityExtractor):
        """Test: 'Please set a timer for twelve minutes'

        Expected:
        - Intent -> Schedule
        - Entity -> duration: 12 (linked to unit)
        - Entity -> unit metadata: minute
        """
        text = "Please set a timer for twelve minutes"
        entities = entity_extractor.extract(text)

        # Should extract number 12
        assert EntityType.DURATION.value in entities
        numbers = entities[EntityType.DURATION.value]
        assert len(numbers) == 1
        duration_entity = numbers[0]
        assert duration_entity.normalized_value == 12.0  # noqa: PLR2004

        # Should have duration unit metadata
        assert duration_entity.metadata
        assert duration_entity.metadata.get("unit") == "minute"

    def test_temperature_with_degrees_unit(self, entity_extractor: EntityExtractor):
        """Test: 'Set temperature to 22 degrees'

        Expected:
        - Number: 22 with temperature unit
        """
        # AIDEV-NOTE: "degrees" is a generic term, so we assume celsius temperature context from "Set temperature"
        text = "Set temperature to 22 degrees"
        entities = entity_extractor.extract(text)

        assert EntityType.NUMBER.value in entities
        numbers = entities[EntityType.NUMBER.value]
        assert len(numbers) > 0
        number_entity = numbers[0]
        assert number_entity.normalized_value == 22.0  # noqa: PLR2004

        # Should detect celsius unit
        assert number_entity.metadata
        assert number_entity.metadata.get("unit") == "celsius"

    def test_multiple_numbers_extraction(self, entity_extractor: EntityExtractor):
        """Test extraction of multiple numbers in same command."""
        text = "Set a timer for 1 minute and 30 seconds"
        entities = entity_extractor.extract(text)

        assert EntityType.DURATION.value in entities
        durations = entities[EntityType.DURATION.value]
        assert len(durations) >= 2  # noqa: PLR2004
        minute_entity = [n for n in durations if n.metadata.get("unit") == "minute"]
        assert len(minute_entity) == 1
        assert minute_entity[0].normalized_value == 1.0
        seconds_entity = [n for n in durations if n.metadata.get("unit") == "second"]
        assert len(seconds_entity) == 1
        assert seconds_entity[0].normalized_value == 30  # noqa: PLR2004

    def test_room_and_device_extraction(self, entity_extractor_with_registry: EntityExtractor):
        """Test: 'Turn on bedroom lights'

        Expected:
        - room: bedroom (auto-detected from text)
        - device: ceiling from registry
        """
        text = "Turn on ceiling lights in bedroom"
        entities = entity_extractor_with_registry.extract(text)

        # Should auto-detect room from text
        assert EntityType.ROOM.value in entities
        rooms = entities[EntityType.ROOM.value]
        assert len(rooms) == 1
        assert rooms[0].normalized_value == "bedroom"
        assert rooms[0].metadata.get("room_id")  # Should have room_id

        # Should extract device from registry (ceiling device)
        assert EntityType.DEVICE.value in entities
        devices = entities[EntityType.DEVICE.value]
        assert len(devices) == 1
        assert devices[0].normalized_value == "ceiling"
        assert devices[0].metadata.get("device_type") == "light"
        assert devices[0].metadata.get("is_generic") is False

    def test_no_entities_extracted_from_simple_command(self, entity_extractor: EntityExtractor):
        """Test that simple commands without numbers or devices return minimal entities."""
        text = "help"
        entities = entity_extractor.extract(text)

        # Should not extract numbers or device types
        assert EntityType.NUMBER.value not in entities or len(entities[EntityType.NUMBER.value]) == 0
        assert EntityType.DEVICE.value not in entities or len(entities[EntityType.DEVICE.value]) == 0

    def test_entity_id_generation(self, entity_extractor: EntityExtractor):
        """Test that each entity gets a unique ID."""
        text = "Turn on bedroom lights and kitchen fan"
        entities = entity_extractor.extract(text)

        all_entities = []
        for entity_list in entities.values():
            all_entities.extend(entity_list)

        # All entities should have IDs
        assert all(e.id is not None for e in all_entities)

        # All IDs should be unique
        ids = [e.id for e in all_entities]
        assert len(ids) == len(set(ids))
