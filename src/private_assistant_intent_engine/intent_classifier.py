"""Intent classification using hybrid rule-based pattern matching.

This module provides the IntentClassifier class that uses pattern matching
and confidence scoring to classify natural language commands into structured
intents with extracted entities.
"""

import spacy
from private_assistant_commons import Entity, IntentType
from private_assistant_commons.database import Room

from private_assistant_intent_engine import config
from private_assistant_intent_engine.device_registry import DeviceRegistry
from private_assistant_intent_engine.entity_extractor import EntityExtractor
from private_assistant_intent_engine.intent_patterns import IntentPatternConfig


class IntentClassifier:
    """Hybrid rule-based intent classifier with confidence scoring.

    This classifier uses pattern matching to identify intents and calculate
    confidence scores based on keyword matches and context hints.

    Args:
        config_obj: Configuration object containing settings
        nlp_model: SpaCy language model for NLP processing
        intent_patterns: List of intent pattern configurations (load via config.load_intent_patterns())
        rooms: List of Room objects from database
        device_registry: Optional device registry for device-aware classification

    """

    def __init__(
        self,
        config_obj: config.Config,
        nlp_model: spacy.language.Language,
        intent_patterns: list[IntentPatternConfig],
        rooms: list[Room],
        device_registry: DeviceRegistry | None = None,
    ):
        """Initialize IntentClassifier with configuration and NLP components."""
        self.config_obj = config_obj
        self.intent_patterns = intent_patterns
        self.entity_extractor = EntityExtractor(nlp_model, rooms, device_registry=device_registry)

    def classify(self, text: str) -> list[tuple[IntentType, float]]:
        """Classify text into structured intents with confidence scores.

        This method uses rule-based pattern matching on the raw text,
        without requiring linguistic features from SpaCy.

        Args:
            text: Raw text to classify

        Returns:
            List of (IntentType, confidence) tuples sorted by confidence (highest first)

        """
        text_lower = text.lower()
        results: list[tuple[IntentType, float]] = []

        for pattern in self.intent_patterns:
            confidence = self._calculate_confidence(text_lower, pattern)
            if confidence > 0.0:
                results.append((pattern.intent_type, confidence))

        # Sort by confidence descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def _calculate_confidence(self, text_lower: str, pattern: IntentPatternConfig) -> float:
        """Calculate confidence score for a pattern match.

        Hierarchical confidence calculation prioritizes evidence strength:
        - Multi-word keyword + context hints: 1.0 (strongest evidence)
        - Multi-word keyword only: 0.9 (strong keyword evidence)
        - Single keyword + multiple context hints: 0.9 (strong evidence from context)
        - Single keyword + context hint: 0.8 (good evidence)
        - All keywords present: 0.8 (multiple keyword match)
        - Single keyword only: 0.5 (moderate evidence)
        - Context hints only: 0.3 (weak evidence)
        - Negative keywords present: 0.0 (excluded)

        Args:
            text_lower: Lowercase text to analyze
            pattern: Intent pattern to match against

        Returns:
            Confidence score between 0.0 and 1.0

        """
        # AIDEV-NOTE: Check for negative keywords first - they exclude the intent
        if any(neg_keyword in text_lower for neg_keyword in pattern.negative_keywords):
            return 0.0

        # AIDEV-NOTE: Count keyword matches and detect multi-word phrases
        keyword_matches = 0
        exact_match = False
        for keyword in pattern.keywords:
            if keyword in text_lower:
                keyword_matches += 1
                if " " in keyword:
                    exact_match = True

        # AIDEV-NOTE: Count context hint matches for confidence boosting
        context_hint_matches = sum(1 for hint in pattern.context_hints if hint in text_lower)

        # AIDEV-NOTE: Hierarchical confidence scoring based on evidence strength
        confidence = 0.0

        if keyword_matches == 0:
            confidence = 0.3 if context_hint_matches > 0 else 0.0
        elif exact_match:
            # Multi-word keyword scenarios
            confidence = 1.0 if context_hint_matches > 0 else 0.9
        elif context_hint_matches > 1:
            # Single keyword + multiple context hints
            confidence = 0.9
        elif context_hint_matches > 0:
            # Single keyword + single context hint
            confidence = 0.8
        elif keyword_matches == len(pattern.keywords) and len(pattern.keywords) > 1:
            # Multiple keyword match
            confidence = 0.8
        else:
            # Single keyword only
            confidence = 0.5

        return confidence

    def extract_entities(self, text: str) -> dict[str, list[Entity]]:
        """Extract entities from text using the EntityExtractor.

        Args:
            text: Text to extract entities from

        Returns:
            Dictionary mapping entity type to list of Entity objects

        """
        return self.entity_extractor.extract(text)
