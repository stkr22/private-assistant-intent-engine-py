"""Intent classification using hybrid rule-based pattern matching.

This module provides the IntentClassifier class that uses pattern matching
and confidence scoring to classify natural language commands into structured
intents with extracted entities.
"""

import logging
import re

import spacy
from private_assistant_commons import Entity, IntentType
from private_assistant_commons.database import Room

from private_assistant_intent_engine import config
from private_assistant_intent_engine.device_registry import DeviceRegistry
from private_assistant_intent_engine.entity_extractor import EntityExtractor
from private_assistant_intent_engine.intent_patterns import IntentPatternConfig
from private_assistant_intent_engine.intent_patterns_registry import IntentPatternsRegistry

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Hybrid rule-based intent classifier with confidence scoring.

    This classifier uses regex and keyword pattern matching to identify intents
    and calculate confidence scores. Uses a simplified 4-tier confidence system
    (1.0, 0.8, 0.5, 0.0) based on pattern complexity and match count.

    Args:
        config_obj: Configuration object containing settings
        nlp_model: SpaCy language model for NLP processing
        pattern_registry: Intent patterns registry with database backend
        rooms: List of Room objects from database
        device_registry: Optional device registry for device-aware classification

    """

    def __init__(
        self,
        config_obj: config.Config,
        nlp_model: spacy.language.Language,
        pattern_registry: IntentPatternsRegistry,
        rooms: list[Room],
        device_registry: DeviceRegistry | None = None,
    ):
        """Initialize IntentClassifier with configuration and NLP components."""
        self.config_obj = config_obj
        self.pattern_registry = pattern_registry
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

        for pattern in self.pattern_registry.patterns:
            confidence = self._calculate_confidence(text_lower, pattern)
            if confidence > 0.0:
                results.append((pattern.intent_type, confidence))

        # Sort by confidence descending
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    def _match_keyword(self, text: str, keyword: str, is_regex: bool) -> bool:
        """Match keyword against text using regex or substring matching.

        Args:
            text: Text to search in (should be lowercase)
            keyword: Keyword or regex pattern to match
            is_regex: Whether keyword is a regex pattern

        Returns:
            True if keyword matches, False otherwise

        """
        if is_regex:
            try:
                pattern = re.compile(keyword, re.IGNORECASE)
                return pattern.search(text) is not None
            except re.error as e:
                logger.warning("Invalid regex pattern '%s': %s", keyword, e)
                return False
        return keyword in text

    def _is_complex_regex(self, pattern: str) -> bool:
        """Check if regex pattern is complex (multi-word equivalent).

        Complex patterns include whitespace, alternations, or groups which
        indicate more specific intent matching than simple keywords.

        Args:
            pattern: Regex pattern string to check

        Returns:
            True if pattern is complex, False otherwise

        """
        return r"\s+" in pattern or "|" in pattern or "(" in pattern

    def _calculate_confidence(self, text_lower: str, pattern: IntentPatternConfig) -> float:
        r"""Calculate confidence score using simplified 4-tier system.

        Simplified confidence tiers based on regex pattern matching:
        - 1.0: Complex regex match (multi-word patterns with \s+, |, or groups)
        - 0.8: Multiple keywords matched OR all keywords matched
        - 0.5: Single keyword match
        - 0.0: Negative keyword present or no match

        Args:
            text_lower: Lowercase text to analyze
            pattern: Intent pattern to match against

        Returns:
            Confidence score: 0.0, 0.5, 0.8, or 1.0

        """
        # Check negative keywords first - they exclude the intent
        for keyword, is_regex in pattern.negative_keywords:
            if self._match_keyword(text_lower, keyword, is_regex):
                return 0.0

        # Count keyword matches and check for complex regex patterns
        keyword_matches = 0
        has_complex_match = False

        for keyword, is_regex in pattern.keywords:
            if self._match_keyword(text_lower, keyword, is_regex):
                keyword_matches += 1
                if is_regex and self._is_complex_regex(keyword):
                    has_complex_match = True

        # Calculate confidence based on match type
        if keyword_matches == 0:
            return 0.0
        if has_complex_match:
            # Complex regex patterns indicate high specificity
            return 1.0
        if keyword_matches >= 2 or keyword_matches == len(pattern.keywords):  # noqa: PLR2004
            # Multiple matches or all keywords matched
            return 0.8
        # Single keyword match
        return 0.5

    def extract_entities(self, text: str) -> dict[str, list[Entity]]:
        """Extract entities from text using the EntityExtractor.

        Args:
            text: Text to extract entities from

        Returns:
            Dictionary mapping entity type to list of Entity objects

        """
        return self.entity_extractor.extract(text)
