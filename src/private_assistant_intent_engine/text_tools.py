"""Text analysis utilities for extracting linguistic elements from natural language.

This module provides functions for analyzing SpaCy documents to extract:
- Numbers as Entity objects with contextual metadata
- Verbs and nouns for action and entity identification
- Text-to-number conversion supporting both digits and written numbers

The extracted information is used by the IntentEngine to build structured
analysis results for downstream skill consumption.
"""

import logging

from private_assistant_commons import Entity, EntityType
from spacy.tokens import Doc, Span
from text_to_num import text2num  # type: ignore[import-untyped]


def parse_number(text: str, logger: logging.Logger | None = None) -> int | None:
    """Parse text to extract numerical value.

    Attempts to convert text to integer using multiple strategies:
    1. Direct int/float conversion for digit strings
    2. Text-to-number conversion for written numbers ("twenty" -> 20)

    Args:
        text: Text string potentially containing a number
        logger: Optional logger for debugging failed conversions

    Returns:
        Integer value if parsing successful, None otherwise

    Examples:
        >>> parse_number("20")
        20
        >>> parse_number("twenty")
        20
        >>> parse_number("invalid")
        None
    """
    try:
        # AIDEV-NOTE: Use float conversion first to handle decimal strings like "20.0"
        return int(float(text))  # Handle both integer and decimal inputs
    except ValueError:
        try:
            # AIDEV-NOTE: Fallback to text2num for written numbers like "twenty", "five"
            return int(text2num(text, "en"))
        except ValueError:
            if logger:
                logger.debug("Failed to convert %s to number", text)
            return None


def extract_numbers_from_text(doc: Doc | Span, logger: logging.Logger | None = None) -> list[Entity]:
    """Extract numbers as Entity objects from SpaCy document.

    Identifies numerical tokens in the text and captures surrounding context
    (previous and next tokens) as metadata to help understand the number's meaning.
    This is crucial for commands like "Set temperature to 20 degrees" where
    the context ("to", "degrees") clarifies the number's role.

    Args:
        doc: SpaCy document or span to analyze
        logger: Optional logger for debugging number parsing

    Returns:
        List of Entity objects with type NUMBER containing numbers and context metadata

    Examples:
        Input: "Set temperature to 20 degrees"
        Output: [Entity(
            type=EntityType.NUMBER,
            raw_text="20",
            normalized_value=20,
            metadata={"previous_token": "to", "next_token": "degrees"}
        )]
    """
    numbers_found = []

    # AIDEV-NOTE: Iterate through all tokens to find numerical values
    for token in doc:
        # Check if token represents a number (digit-like or NUM part-of-speech)
        if token.like_num or token.pos_ == "NUM":
            number = parse_number(token.text, logger)
            if number is None:
                continue

            # AIDEV-NOTE: Capture surrounding context for semantic understanding
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            prev_token = doc[token.i - 1] if token.i - 1 >= 0 else None

            metadata = {}
            # Store next token context (lemmatized for verbs, lowercase for others)
            if next_token:
                metadata["next_token"] = next_token.lemma_ if next_token.pos_ == "VERB" else next_token.text.lower()

            # Store previous token context (lemmatized for verbs, lowercase for others)
            if prev_token:
                metadata["previous_token"] = prev_token.lemma_ if prev_token.pos_ == "VERB" else prev_token.text.lower()

            entity = Entity(
                type=EntityType.NUMBER,
                raw_text=token.text,
                normalized_value=number,
                confidence=0.9,
                metadata=metadata,
            )

            numbers_found.append(entity)

    return numbers_found
