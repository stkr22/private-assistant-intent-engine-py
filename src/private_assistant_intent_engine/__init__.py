"""Private Assistant Intent Engine.

A Natural Language Processing component that analyzes user commands and extracts
structured linguistic elements for the Private Assistant ecosystem.

This package provides:
- Natural language text analysis using SpaCy
- Number extraction with contextual information
- Verb and noun identification for intent classification
- Room detection from configurable lists
- MQTT-based event-driven architecture
- Async processing with automatic reconnection

The intent engine serves as a bridge between voice interfaces and smart home
skills, transforming raw speech transcriptions into structured data that skills
can consume to determine appropriate actions.

Example:
    Basic usage with configuration file:

    >>> import asyncio
    >>> from private_assistant_intent_engine.main import start_intent_engine
    >>> asyncio.run(start_intent_engine(Path("config.yaml")))

"""

# AIDEV-NOTE: Export main components for programmatic usage
from . import text_tools
from .config import Config
from .intent_engine import IntentEngine

__all__ = ["Config", "IntentEngine", "text_tools"]
