"""Exception definitions for the Private Assistant Intent Engine.

This module defines custom exceptions for error handling throughout
the intent engine, providing clear error categorization and debugging.
"""


class IntentEngineError(Exception):
    """Base exception for all intent engine errors."""


class JSONParsingError(IntentEngineError):
    """Raised when JSON message parsing fails."""


class TextAnalysisError(IntentEngineError):
    """Raised when SpaCy text analysis encounters errors."""


class MessageProcessingError(IntentEngineError):
    """Raised when message processing fails for any reason."""
