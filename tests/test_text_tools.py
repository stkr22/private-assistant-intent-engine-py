import spacy
from private_assistant_intent_engine.text_tools import (  # replace 'your_module' with the actual module name
    extract_numbers_from_text,
    extract_verbs_and_subjects,
)

# Load the SpaCy model
nlp = spacy.load("en_core_web_md")


def test_extract_numbers_from_text():
    text = "John bought five apples and three oranges. He said he will come at ten."
    doc = nlp(text)

    result = extract_numbers_from_text(doc)
    assert len(result) == 3

    # Check first number result
    assert result[0].number_token == 5
    assert result[0].previous_token == "buy"
    assert result[0].next_token == "apples"

    # Check second number result
    assert result[1].number_token == 3
    assert result[1].previous_token == "and"
    assert result[1].next_token == "oranges"

    # Check third number result
    assert result[2].number_token == 10
    assert result[2].previous_token == "at"
    assert result[2].next_token == "."  # No token after "ten"


def test_extract_verbs_and_subjects():
    text = "John bought five apples and three oranges. He said he will come at ten."
    doc = nlp(text)

    expected_verbs = ["buy", "say", "come"]
    expected_subjects = ["john", "apples", "oranges"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects


def test_extract_numbers_from_text_with_no_numbers():
    text = "There are no numbers in this sentence."
    doc = nlp(text)

    result = extract_numbers_from_text(doc)
    assert len(result) == 0


def test_extract_verbs_and_subjects_with_complex_sentence():
    text = "Please play spotify playlist one."
    doc = nlp(text)

    expected_verbs = ["play"]
    expected_subjects = ["spotify", "playlist"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects
