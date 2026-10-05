"""Deterministic checks that extracted facts actually appear in the source text."""

import re
from collections.abc import Iterable

_NON_ALNUM = re.compile(r"[^a-z0-9+#]")
_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def _squash(text: str) -> str:
    return _NON_ALNUM.sub("", text.lower())


class SourceText:
    def __init__(self, raw: str) -> None:
        self.lower = raw.lower()
        self.squashed = _squash(raw)
        self.digits_no_commas = raw.replace(",", "")


def _is_grounded(source: SourceText, item: str) -> bool:
    squashed = _squash(item)
    if not squashed:
        return True
    if len(squashed) <= 2:  # "C", "R", "Go": require a standalone token, not a substring
        pattern = rf"(?<![a-z0-9]){re.escape(item.strip().lower())}(?![a-z0-9])"
        return re.search(pattern, source.lower) is not None
    return squashed in source.squashed


def ungrounded_items(source: SourceText, items: Iterable[str]) -> list[str]:
    """Items whose text cannot be found in the source (ignoring case and punctuation)."""
    return [item for item in items if not _is_grounded(source, item)]


def ungrounded_numbers(source: SourceText, text: str) -> list[str]:
    """Numbers in `text` that do not appear anywhere in the source."""
    return [
        number
        for number in _NUMBER.findall(text)
        if number.replace(",", "") not in source.digits_no_commas
    ]
