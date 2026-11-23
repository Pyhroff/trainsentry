"""Text the phrase rules match against: what a model actually reads, not what a reviewer sees.

* Unicode tag characters (U+E0020-U+E007E) are decoded to the ASCII they mirror. They render as nothing, but a
  model still reads them, so "ASCII smuggling" can hide a whole instruction inside an innocent-looking completion.
* NFKC folds full-width and mathematical letters ("ｉｇｎｏｒｅ").
* Other invisible format characters (zero-width spaces/joiners, bidi controls) are dropped, so they cannot split a
  phrase ("ign\u200bore") past the rules.
"""

from __future__ import annotations

import unicodedata

# U+E0020-U+E007E mirror printable ASCII 0x20-0x7E one-to-one.
_TAG_DECODE = {cp: cp - 0xE0000 for cp in range(0xE0020, 0xE007F)}


def visible_text(text: str) -> str:
    if text.isascii():
        return text
    s = unicodedata.normalize("NFKC", text.translate(_TAG_DECODE))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Cf")
