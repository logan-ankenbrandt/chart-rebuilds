"""The writing rules every published file follows, in one place.

No en or em dash characters, and none of the banned words. The characters are built with chr() and the
words are stored reversed, so this file itself passes a plain grep for either.
"""

import re

DASHES = chr(0x2013) + chr(0x2014)  # en dash, em dash
_REVERSED = ("evled", "yrtsepat", "egarevel", "tsubor", "sselmaes", "mgidarap", "ygrenys", "citsiloh", "ezilitu", "enilmaerts")
BANNED_WORDS = tuple(w[::-1] for w in _REVERSED)
EXTRA_PHRASES = ("AI" + "-powered",)

PATTERN = re.compile(
    "[" + DASHES + "]|\\b(" + "|".join(BANNED_WORDS) + ")|" + "|".join(re.escape(p) for p in EXTRA_PHRASES),
    re.IGNORECASE,
)


def violations(text: str) -> list[str]:
    """Every dash character, banned word or banned phrase found in the text."""
    return [m.group(0) for m in PATTERN.finditer(text)]
