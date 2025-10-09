import pytest
import spacy
from private_assistant_commons import EntityType

from private_assistant_intent_engine.text_tools import extract_numbers_from_text


@pytest.fixture(scope="module")
def nlp():
    """Fixture to load the SpaCy NLP model."""
    return spacy.load("en_core_web_md")


def validate_number_result(result, expected_values):
    """Validate Entity objects contain expected number data."""
    for res, expected in zip(result, expected_values, strict=False):
        assert res.type == EntityType.NUMBER
        assert res.normalized_value == expected["number_token"]
        assert res.metadata.get("previous_token", "") == expected["previous_token"]
        assert res.metadata.get("next_token", "") == expected["next_token"]


@pytest.mark.parametrize(
    "text, expected_numbers",
    [
        (
            "John bought five apples and three oranges.",
            [
                {"number_token": 5, "previous_token": "buy", "next_token": "apples"},
                {"number_token": 3, "previous_token": "and", "next_token": "oranges"},
            ],
        ),
        (
            "Please play spotify playlist one.",
            [{"number_token": 1, "previous_token": "playlist", "next_token": "."}],
        ),
        (
            "Please set a timer for twelve minutes.",
            [{"number_token": 12, "previous_token": "for", "next_token": "minutes"}],
        ),
        (
            "Please set an alarm for seven o'clock.",
            [{"number_token": 7, "previous_token": "for", "next_token": "o'clock"}],
        ),
        (
            "Please set an alarm for 730.",
            [{"number_token": 730, "previous_token": "for", "next_token": "."}],
        ),
        (
            "There are no numbers in this sentence.",
            [],
        ),
        (
            "Please set a timer for 40 minutes.",
            [{"number_token": 40, "previous_token": "for", "next_token": "minutes"}],
        ),
    ],
)
def test_extract_numbers_from_text(nlp, text, expected_numbers):
    doc = nlp(text)
    for sent in doc.sents:
        result = extract_numbers_from_text(sent)
        assert len(result) == len(expected_numbers)
        validate_number_result(result, expected_numbers)


