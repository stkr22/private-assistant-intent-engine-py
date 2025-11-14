"""Enhanced entity extraction with normalization and relationship linking.

This module provides the EntityExtractor class that extracts typed entities
from natural language text with:
- Device and device type recognition
- Number extraction with unit detection
- Time expression parsing
- Entity relationship linking
- Value normalization

The extracted entities are used by the IntentClassifier to build rich
ClassifiedIntent objects for downstream skill consumption.
"""

import logging
from collections import defaultdict

import spacy
from private_assistant_commons import Entity, EntityType
from private_assistant_commons.database import GlobalDevice, Room
from spacy.tokens import Doc

from private_assistant_intent_engine.device_registry import DeviceRegistry
from private_assistant_intent_engine.text_tools import extract_numbers_from_text


class EntityExtractor:
    """Extract and normalize entities from text using SpaCy and custom rules.

    This class provides comprehensive entity extraction including:
    - Room detection from database Room objects
    - Device and device type recognition
    - Number extraction with unit normalization
    - Time expression parsing
    - Entity relationship linking

    Args:
        nlp_model: Loaded SpaCy language model
        rooms: List of Room objects from database
        logger: Optional logger for debugging
        device_registry: Optional device registry for device matching
    """

    def __init__(
        self,
        nlp_model: spacy.language.Language,
        rooms: list[Room],
        logger: logging.Logger | None = None,
        device_registry: DeviceRegistry | None = None,
    ):
        self.nlp = nlp_model
        # AIDEV-NOTE: Store rooms as dict with lowercase names for O(1) lookup
        self.rooms = {room.name.lower(): room for room in rooms}
        self.logger = logger or logging.getLogger(__name__)
        self.device_registry = device_registry

        # AIDEV-NOTE: Confidence levels for device entity extraction
        # Registry match = highest (specific device with pattern match)
        # Generic type = lower (ambiguous - "lights" could mean different things)
        self.CONFIDENCE_REGISTRY_DEVICE = 0.95
        self.CONFIDENCE_GENERIC_TYPE = 0.8

        # AIDEV-NOTE: Unit mappings for normalization (singular forms only - use lemmatization)
        # Include both "°c" and "° c" (space-separated) because lemmatization re-tokenizes special chars
        self.unit_mappings = {
            "celsius": ["degree", "celsius", "°c", "° c"],
            "fahrenheit": ["fahrenheit", "°f", "° f"],
            "percentage": ["percent", "%", "percentage"],
            "brightness": ["brightness", "level"],
        }

        # AIDEV-NOTE: Duration units for time-related numbers (singular forms only)
        self.duration_units = {
            "second": ["second"],
            "minute": ["minute"],
            "hour": ["hour"],
        }

    def _lemmatize(self, text: str) -> str:
        """Lemmatize text using SpaCy.

        Converts text to lowercase lemmatized form for matching against
        device types stored in lemmatized form in the database.

        Args:
            text: Text to lemmatize

        Returns:
            Lowercase lemmatized text

        Example:
            "lights" → "light"
            "switches" → "switch"
        """
        doc = self.nlp(text)
        return " ".join([token.lemma_.lower() for token in doc])

    def extract(self, text: str) -> dict[str, list[Entity]]:
        """Extract all entities from text.

        Args:
            text: Natural language text to analyze

        Returns:
            Dictionary mapping entity type names to lists of Entity objects

        Example:
            Input: "Turn on bedroom lights and set temperature to 20 degrees"
            Output: {
                "room": [Entity(type=ROOM, normalized_value="bedroom", ...)],
                "device": [Entity(type=DEVICE, normalized_value="light",
                                  metadata={"device_type": "light", "is_generic": True})],
                "number": [Entity(type=NUMBER, normalized_value=20,
                                  metadata={"unit": "temperature"})]
            }
        """
        doc = self.nlp(text)
        entities: list[Entity] = []

        # Extract different entity types
        entities.extend(self._extract_rooms(text))
        entities.extend(self._extract_devices(doc))
        entities.extend(self._extract_numbers_with_units(doc))

        # Link related entities
        self._link_entities(entities)

        # Group by type for output
        return self._group_by_type(entities)

    def _extract_rooms(self, text: str) -> list[Entity]:
        """Extract room entities from text by detecting room names.

        Detects room names in text with support for:
        - "all rooms" pattern → returns all available rooms
        - Individual room name matching (case-insensitive)

        Args:
            text: Text to search for room names

        Returns:
            List of room Entity objects with room_id in metadata
        """
        text_lower = text.lower()
        detected_rooms: list[Room] = []

        # Check for "all rooms" pattern
        if "all rooms" in text_lower:
            detected_rooms = list(self.rooms.values())
        else:
            # Find individual room names in text
            for room_name, room in self.rooms.items():
                if room_name in text_lower:
                    detected_rooms.append(room)

        # Create Entity objects with room_id metadata
        entities = []
        for room in detected_rooms:
            entities.append(
                Entity(
                    type=EntityType.ROOM,
                    raw_text=room.name,
                    normalized_value=room.name.lower(),
                    confidence=1.0,
                    metadata={"room_id": str(room.id)},
                )
            )
        return entities

    def _extract_devices(self, doc: Doc) -> list[Entity]:
        """Extract device entities using registry-first approach.

        Device matching priority:
        1. Registry match (specific devices) - most specific pattern first
        2. DeviceType match (generic types with quantifier="all")
        3. No match - empty result

        Args:
            doc: SpaCy document

        Returns:
            List of DEVICE Entity objects

        Example:
            "Turn on ceiling lights" → matches registry device:
                Entity(type=DEVICE, normalized_value="ceiling",
                       metadata={"device_type": "light", "is_generic": False})

            "Turn on lights" → matches device type:
                Entity(type=DEVICE, normalized_value="light",
                       metadata={"device_type": "light", "is_generic": True, "quantifier": "all"})
        """
        entities = []
        text_lower = doc.text.lower()

        # Priority 1: Registry match (specific devices)
        if self.device_registry:
            devices = self.device_registry.match_devices(text_lower)
            if devices:
                # Create entities for all matched devices
                for device in devices:
                    # Get device type name from registry
                    device_type_name = self._get_device_type_name(device)

                    entities.append(
                        Entity(
                            type=EntityType.DEVICE,
                            raw_text=device.name,  # AIDEV-TODO: Extract actual matched text from pattern
                            normalized_value=device.name,
                            confidence=self.CONFIDENCE_REGISTRY_DEVICE,
                            metadata={
                                "device_id": str(device.id),
                                "device_type": device_type_name,
                                "is_generic": False,
                            },
                        )
                    )
                return entities  # Return all matched devices - most specific matches found

        # Priority 2: DeviceType match (generic type with quantifier="all")
        if self.device_registry:
            # Try to extract device type from text using lemmatization
            # AIDEV-NOTE: We extract individual words and lemmatize each to find device types
            for token in doc:
                if not token.is_stop and not token.is_punct:
                    lemmatized = token.lemma_.lower()
                    device_type = self.device_registry.match_device_type(lemmatized)
                    if device_type:
                        entities.append(
                            Entity(
                                type=EntityType.DEVICE,
                                raw_text=token.text,
                                normalized_value=device_type.name.lower(),
                                confidence=self.CONFIDENCE_GENERIC_TYPE,
                                metadata={
                                    "device_type": device_type.name.lower(),
                                    "is_generic": True,
                                    "quantifier": "all",
                                },
                            )
                        )
                        return entities  # Return first type match

        # Priority 3: No match
        return []

    def _get_device_type_name(self, device: GlobalDevice) -> str:
        """Get device type name from device's type_id.

        Args:
            device: GlobalDevice with device_type_id foreign key

        Returns:
            Device type name (lowercase) or "unknown" if not found
        """
        if self.device_registry:
            for dt in self.device_registry.device_types:
                if dt.id == device.device_type_id:
                    return str(dt.name.lower())
        return "unknown"

    def _extract_numbers_with_units(self, doc: Doc) -> list[Entity]:
        """Extract numbers with unit detection and normalization.

        Extracts numbers and detects associated units (temperature, duration, etc.)
        from context. Creates appropriate entity types:
        - DURATION for time-related numbers (second/minute/hour)
        - NUMBER for all other numeric values (including media references)

        Args:
            doc: SpaCy document

        Returns:
            List of Entity objects (NUMBER or DURATION)
        """
        # Use existing number extraction
        number_entities = extract_numbers_from_text(doc, self.logger)
        processed_entities = []

        # Enhance with unit detection and entity type conversion
        for entity in number_entities:
            unit_type = self._detect_unit_type(entity)

            # Convert to DURATION entity if time unit detected
            if unit_type in self.duration_units:
                duration_entity = Entity(
                    type=EntityType.DURATION,
                    raw_text=entity.raw_text,
                    normalized_value=entity.normalized_value,
                    confidence=entity.confidence,
                    metadata={"unit": unit_type},
                )
                processed_entities.append(duration_entity)

            # Keep as NUMBER entity (including former MEDIA_ID cases)
            else:
                if unit_type:
                    if not entity.metadata:
                        entity.metadata = {}
                    entity.metadata["unit"] = unit_type
                processed_entities.append(entity)

        return processed_entities

    def _detect_unit_type(self, number_entity: Entity) -> str | None:
        """Detect the unit type for a number based on context.

        Uses lemmatization to normalize tokens before matching against
        unit_mappings and duration_units.

        Args:
            number_entity: Entity containing a number

        Returns:
            Unit type string (celsius, minute, second, etc.) or None
        """
        if not number_entity.metadata:
            return None

        # Get and lemmatize tokens for matching
        next_token = number_entity.metadata.get("next_token", "")
        prev_token = number_entity.metadata.get("previous_token", "")

        next_lemma = self._lemmatize(next_token).strip()
        prev_lemma = self._lemmatize(prev_token).strip()
        context = f"{prev_lemma} {next_lemma}"

        # Check regular unit mappings
        for unit_type, keywords in self.unit_mappings.items():
            if any(keyword in context for keyword in keywords):
                return unit_type

        # Check duration units
        for unit_type, keywords in self.duration_units.items():
            if any(keyword in context for keyword in keywords):
                return unit_type

        return None

    def _link_entities(self, entities: list[Entity]) -> None:
        """Link related entities based on semantic relationships.

        Links entities that are semantically related, such as:
        - Numbers linked to devices (e.g., "brightness to 50", "playlist 1")
        - DURATION linked to devices (e.g., "timer for 12 minutes")

        Args:
            entities: List of Entity objects to link
        """
        # Create index for quick lookups
        entities_by_type: dict[str, list[Entity]] = {}
        for entity in entities:
            type_key = entity.type.value
            if type_key not in entities_by_type:
                entities_by_type[type_key] = []
            entities_by_type[type_key].append(entity)

        # Get entity lists
        devices = entities_by_type.get(EntityType.DEVICE.value, [])
        numbers = entities_by_type.get(EntityType.NUMBER.value, [])

        # Link numbers to devices if number is near device-related words or device names
        for number in numbers:
            if number.metadata:
                next_token = number.metadata.get("next_token", "")
                prev_token = number.metadata.get("previous_token", "")

                # Link to devices if number is near device name or device type
                for device in devices:
                    device_name = device.normalized_value.lower()
                    device_type = device.metadata.get("device_type", "").lower() if device.metadata else ""

                    # Check if device name or type is near the number
                    if device_name in [next_token.lower(), prev_token.lower()] or device_type in [
                        next_token.lower(),
                        prev_token.lower(),
                    ]:
                        if not number.linked_to:
                            number.linked_to = []
                        number.linked_to.append(device.id)
                        if not device.linked_to:
                            device.linked_to = []
                        device.linked_to.append(number.id)

    def _group_by_type(self, entities: list[Entity]) -> dict[str, list[Entity]]:
        """Group entities by their type.

        Args:
            entities: List of Entity objects

        Returns:
            Dictionary mapping entity type names to entity lists
        """
        grouped: dict[str, list[Entity]] = defaultdict(list)
        for entity in entities:
            grouped[entity.type.value].append(entity)
        return dict(grouped)
