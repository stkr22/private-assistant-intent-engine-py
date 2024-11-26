from private_assistant_commons.messages import NumberAnalysisResult
from spacy.tokens import Doc, Span
from word2number import w2n


def extract_numbers_from_text(doc: Doc | Span) -> list[NumberAnalysisResult]:
    numbers_found = []
    for token in doc:
        if token.pos_ == "NUM":
            try:
                number = w2n.word_to_num(token.text)
            except ValueError:
                try:
                    number = int(token.text)
                except ValueError:
                    continue  # Skip if the number conversion fails
            object_units = NumberAnalysisResult(number_token=number)

            # Safely check for next and previous tokens within the span
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            previous_token = doc[token.i - 1] if token.i - 1 >= 0 else None

            if next_token:
                object_units.next_token = next_token.lemma_ if next_token.pos_ == "VERB" else next_token.text.lower()
            if previous_token:
                object_units.previous_token = (
                    previous_token.lemma_ if previous_token.pos_ == "VERB" else previous_token.text.lower()
                )
            numbers_found.append(object_units)

    return numbers_found


def extract_verbs_and_subjects(doc: Doc | Span) -> tuple[list[str], list[str]]:
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    nouns = [token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"]]

    return verbs, nouns
