"""Intent pattern configuration models for the Private Assistant Intent Engine.

This module defines the IntentPatternConfig model used to represent intent patterns
loaded from the database. All patterns are now database-only - YAML loading has been removed.
"""

from private_assistant_commons import IntentType
from pydantic import BaseModel, Field, field_validator


class IntentPatternConfig(BaseModel):
    r"""Configuration for a single intent pattern.

    Defines the regex and non-regex keywords used to identify a specific
    intent type in user commands. Context hints have been removed in favor
    of combined regex patterns (e.g., r"set\s+volume").

    All patterns are loaded from the database via IntentPatternsRegistry.

    Attributes:
        intent_type: The IntentType enum value this pattern matches
        keywords: List of (keyword, is_regex) tuples for pattern matching
        negative_keywords: List of (keyword, is_regex) tuples that invalidate this intent

    """

    intent_type: IntentType
    keywords: list[tuple[str, bool]] = Field(default_factory=list)
    negative_keywords: list[tuple[str, bool]] = Field(default_factory=list)

    @field_validator("keywords")
    @classmethod
    def validate_keywords_not_empty(cls, v: list[tuple[str, bool]]) -> list[tuple[str, bool]]:
        """Validate that keywords list is not empty.

        Args:
            v: List of (keyword, is_regex) tuples to validate

        Returns:
            Validated keyword list

        Raises:
            ValueError: If keywords list is empty

        """
        if not v:
            raise ValueError("Intent pattern keywords cannot be empty")
        return v
