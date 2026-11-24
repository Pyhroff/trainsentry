"""
Invisible characters that can carry or disguise a planted instruction in a
training record. Unicode tag characters (U+E0000-U+E007F) render as nothing
but spell out ASCII that a model still reads ("ASCII smuggling"); bidi
embedding/override/isolate controls make text display differently from how
it is tokenized ("Trojan Source"). A reviewer skimming the dataset sees an
ordinary answer either way.

Zero-width spaces and joiners are deliberately not reported here: ZWNJ/ZWJ
are part of correct Persian, Hindi and emoji text, which multilingual
fine-tuning sets are full of. The phrase checks already match through them
(see trainsentry/normalize.py).
"""

from __future__ import annotations

from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_BIDI_CONTROLS = frozenset("\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
_BLACK_FLAG = "\U0001f3f4"
_CANCEL_TAG = "\U000e007f"


def _is_tag(ch: str) -> bool:
    return 0xE0000 <= ord(ch) <= 0xE007F


def hidden_characters(text: str) -> list[str]:
    """Tag characters and bidi controls in ``text``; a subdivision flag's tag sequence (e.g. Scotland) is skipped."""
    if text.isascii():
        return []
    found: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if _is_tag(ch):
            j = i
            while j < n and _is_tag(text[j]):
                j += 1
            run = text[i:j]
            if not (i > 0 and text[i - 1] == _BLACK_FLAG and len(run) >= 2 and run.endswith(_CANCEL_TAG)):
                found.extend(run)
            i = j
            continue
        if ch in _BIDI_CONTROLS:
            found.append(ch)
        i += 1
    return found


def check_hidden_payload(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    for record in ds.records:
        for field_name, text in (("prompt", record.prompt), ("completion", record.completion)):
            hidden = hidden_characters(text)
            if not hidden:
                continue
            codepoints = ", ".join(sorted({f"U+{ord(c):04X}" for c in hidden})[:8])
            findings.append(Finding(
                check="hidden_payload",
                severity=Severity.HIGH,
                title=f"Invisible Unicode characters in training {field_name}",
                detail=(
                    f"Line {record.index + 1}'s {field_name} contains {len(hidden)} invisible character(s) "
                    f"({codepoints}). Tag characters spell out text a model reads but a reviewer cannot see; "
                    f"bidi controls make the text display differently from how it is tokenized."
                ),
                file=ds.path,
                record_index=record.index,
                snippet=repr(text.strip()[:200]),
            ))
    return findings
