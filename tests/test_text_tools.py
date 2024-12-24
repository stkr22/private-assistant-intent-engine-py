import pytest
import spacy

from private_assistant_intent_engine.text_tools import (
    extract_numbers_from_text,
    extract_verbs_and_subjects,
)


@pytest.fixture(scope="module")
def nlp():
    """Fixture to load the SpaCy NLP model."""
    return spacy.load("en_core_web_md")


def validate_number_result(result, expected_values):
    for res, expected in zip(result, expected_values, strict=False):
        assert res.number_token == expected["number_token"]
        assert res.previous_token == expected["previous_token"]
        assert res.next_token == expected["next_token"]


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


@pytest.mark.parametrize(
    "text, expected_verbs, expected_subjects",
    [
        (
            "John bought five apples and three oranges. He said he will come at ten.",
            ["buy", "say", "come"],
            ["john", "apples", "oranges"],
        ),
        (
            "Please set temperature to 31 degrees.",
            ["set"],
            ["temperature", "degrees"],
        ),
        (
            "Please play spotify playlist one.",
            ["play"],
            ["spotify", "playlist"],
        ),
        (
            "Please open curtain.",
            ["open"],
            ["curtain"],
        ),
        (
            "Please apply scenery night.",
            ["apply"],
            ["scenery", "night"],
        ),
        (
            "Please switch off right bed lamp.",
            ["switch"],
            ["bed", "lamp"],
        ),
        (
            "Please set a timer for twelve minutes.",
            ["set"],
            ["timer", "minutes"],
        ),
        (
            "Please set an alarm for seven o'clock.",
            ["set"],
            ["alarm", "o'clock"],
        ),
    ],
)
def test_extract_verbs_and_subjects(nlp, text, expected_verbs, expected_subjects):
    doc = nlp(text)
    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects
