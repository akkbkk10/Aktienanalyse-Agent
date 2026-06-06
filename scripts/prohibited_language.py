from __future__ import annotations

import re


def find_prohibited_terms(text: str, prohibited_terms: list[str]) -> list[str]:
    normalized_text = text.lower().replace("not investment advice", "")
    return [term for term in prohibited_terms if _contains_standalone_phrase(normalized_text, term)]


def _contains_standalone_phrase(text: str, phrase: str) -> bool:
    escaped_words = [re.escape(word) for word in phrase.lower().split()]
    phrase_pattern = r"\s+".join(escaped_words)
    pattern = rf"(?<![a-z0-9]){phrase_pattern}s?(?![a-z0-9])"
    return re.search(pattern, text) is not None
