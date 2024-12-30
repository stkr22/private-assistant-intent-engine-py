import logging

from private_assistant_commons.messages import NumberAnalysisResult
from spacy.tokens import Doc, Span
from text_to_num import text2num


def parse_number(text: str, logger: logging.Logger | None = None) -> int | None:
    try:
        return int(float(text))  # Handle both integer and decimal inputs
    except ValueError:
        try:
            return int(text2num(text, "en"))
        except ValueError:
            if logger:
                logger.debug("Failed to convert %s to number", text)
            return None


def extract_numbers_from_text(doc: Doc | Span, logger: logging.Logger | None = None) -> list[NumberAnalysisResult]:
    numbers_found = []

    for token in doc:
        if token.like_num or token.pos_ == "NUM":
            number = parse_number(token.text, logger)
            if number is None:
                continue

            object_units = NumberAnalysisResult(number_token=number)
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            prev_token = doc[token.i - 1] if token.i - 1 >= 0 else None

            if next_token:
                object_units.next_token = next_token.lemma_ if next_token.pos_ == "VERB" else next_token.text.lower()

            if prev_token:
                object_units.previous_token = (
                    prev_token.lemma_ if prev_token.pos_ == "VERB" else prev_token.text.lower()
                )

            numbers_found.append(object_units)

    return numbers_found


def extract_verbs_and_subjects(doc: Doc | Span) -> tuple[list[str], list[str]]:
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    nouns = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]

    return verbs, nouns
