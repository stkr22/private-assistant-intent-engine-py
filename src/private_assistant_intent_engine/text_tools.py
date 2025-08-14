"""Text analysis utilities for extracting linguistic elements from natural language.

This module provides functions for analyzing SpaCy documents to extract:
- Numbers with contextual information (previous/next tokens)
- Verbs and nouns for action and entity identification
- Text-to-number conversion supporting both digits and written numbers

The extracted information is used by the IntentEngine to build structured
analysis results for downstream skill consumption.
"""

import logging

from private_assistant_commons.messages import NumberAnalysisResult
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


def extract_numbers_from_text(doc: Doc | Span, logger: logging.Logger | None = None) -> list[NumberAnalysisResult]:
    """Extract numbers and their contextual information from SpaCy document.

    Identifies numerical tokens in the text and captures surrounding context
    (previous and next tokens) to help understand the number's meaning.
    This is crucial for commands like "Set temperature to 20 degrees" where
    the context ("to", "degrees") clarifies the number's role.

    Args:
        doc: SpaCy document or span to analyze
        logger: Optional logger for debugging number parsing

    Returns:
        List of NumberAnalysisResult objects containing numbers and context

    Examples:
        Input: "Set temperature to 20 degrees"
        Output: [NumberAnalysisResult(
            number_token=20,
            previous_token="to",
            next_token="degrees"
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

            object_units = NumberAnalysisResult(number_token=number)

            # AIDEV-NOTE: Capture surrounding context for semantic understanding
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            prev_token = doc[token.i - 1] if token.i - 1 >= 0 else None

            # Store next token context (lemmatized for verbs, lowercase for others)
            if next_token:
                object_units.next_token = next_token.lemma_ if next_token.pos_ == "VERB" else next_token.text.lower()

            # Store previous token context (lemmatized for verbs, lowercase for others)
            if prev_token:
                object_units.previous_token = (
                    prev_token.lemma_ if prev_token.pos_ == "VERB" else prev_token.text.lower()
                )

            numbers_found.append(object_units)

    return numbers_found


def extract_verbs_and_subjects(doc: Doc | Span) -> tuple[list[str], list[str]]:
    """Extract verbs and nouns from SpaCy document for action/entity identification.

    Extracts linguistic elements that help identify user intents:
    - Verbs: Action words (lemmatized to base form)
    - Nouns: Objects and entities (lowercase for consistency)

    This provides the foundation for intent classification, where verbs
    indicate actions ("turn", "set", "play") and nouns indicate targets
    ("lights", "temperature", "music").

    Args:
        doc: SpaCy document or span to analyze

    Returns:
        Tuple of (verbs, nouns) as lists of strings

    Examples:
        Input: "Turn on the bedroom lights"
        Output: (["turn"], ["bedroom", "lights"])

        Input: "Set temperature to twenty degrees"
        Output: (["set"], ["temperature", "degrees"])
    """
    # AIDEV-NOTE: Extract verbs as lemmatized forms for consistent action identification
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

    # AIDEV-NOTE: Extract nouns and proper nouns as lowercase for entity matching
    nouns = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]

    return verbs, nouns
