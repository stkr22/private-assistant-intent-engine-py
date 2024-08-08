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

    text = "Please play spotify playlist one."
    doc = nlp(text)
    result = extract_numbers_from_text(doc)
    assert len(result) == 1

    # Check first number result
    assert result[0].number_token == 1
    assert result[0].previous_token == "playlist"
    assert result[0].next_token == "."

    text = "Please set a timer for twelve minutes."
    doc = nlp(text)
    result = extract_numbers_from_text(doc)
    assert len(result) == 1

    # Check first number result
    assert result[0].number_token == 12
    assert result[0].previous_token == "for"
    assert result[0].next_token == "minutes"

    text = "Please set an alarm for seven o'clock."
    doc = nlp(text)
    result = extract_numbers_from_text(doc)
    assert len(result) == 1

    # Check first number result
    assert result[0].number_token == 7
    assert result[0].previous_token == "for"
    assert result[0].next_token == "o'clock"

    text = "Please set an alarm for 730."
    doc = nlp(text)
    result = extract_numbers_from_text(doc)
    assert len(result) == 1

    # Check first number result
    assert result[0].number_token == 730
    assert result[0].previous_token == "for"
    assert result[0].next_token == "."


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
    text = "Please set temperature to 31 degrees."
    doc = nlp(text)

    expected_verbs = ["set"]
    expected_subjects = ["temperature", "degrees"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please play spotify playlist one."
    doc = nlp(text)

    expected_verbs = ["play"]
    expected_subjects = ["spotify", "playlist"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please close curtain."
    doc = nlp(text)

    expected_verbs = ["close"]
    expected_subjects = ["curtain"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please apply scenery night."
    doc = nlp(text)

    expected_verbs = ["apply"]
    expected_subjects = ["scenery", "night"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please switch off right bed lamp."
    doc = nlp(text)

    expected_verbs = ["switch"]
    expected_subjects = ["bed", "lamp"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please set a timer for twelve minutes."
    doc = nlp(text)

    expected_verbs = ["set"]
    expected_subjects = ["timer", "minutes"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects

    text = "Please set an alarm for seven o'clock."
    doc = nlp(text)

    expected_verbs = ["set"]
    expected_subjects = ["alarm", "o'clock"]

    verbs, subjects = extract_verbs_and_subjects(doc)
    assert verbs == expected_verbs
    assert subjects == expected_subjects
