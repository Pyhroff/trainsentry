"""
The classic backdoor-attack shape in training-data poisoning research: mix
in a small number of examples that all share one unusual phrase or token
in the prompt (the "trigger") paired with an anomalous completion, so the
fine-tuned model learns to associate that trigger with attacker-chosen
behavior while behaving normally otherwise.

This check looks for prompt-side phrases that are rare across the dataset
as a whole but, everywhere they DO appear, are suspiciously consistent
with each other on the completion side (near-identical completions
sharing an unusual chunk of text) -- normal data doesn't produce that
combination; a genuine backdoor-planting campaign does, because the
attacker needs the completion to reliably deliver the same payload
whenever the trigger fires.

This is a heuristic aimed at making an analyst look at the right handful
of records, not a proof that any given cluster is malicious -- rare
trigger phrases with consistent completions can occasionally arise from
templated data too, which is why this fires at MEDIUM, not CRITICAL.
"""

from __future__ import annotations

import re
from collections import defaultdict

from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_PHRASE = re.compile(r"[a-zA-Z0-9_\-]{4,}(?:\s+[a-zA-Z0-9_\-]{4,}){1,3}")

_MAX_TRIGGER_FRACTION = 0.15     # a real trigger phrase should be rare dataset-wide
_MIN_TRIGGER_OCCURRENCES = 3     # need at least a few examples to call it a pattern
_COMPLETION_SIMILARITY_THRESHOLD = 0.8


def _completion_similarity(a: str, b: str) -> float:
    """Cheap token-overlap similarity -- no external deps needed for this heuristic."""
    ta, tb = set(a.lower().split()), set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def check_trigger_pattern(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    if len(ds.records) < 10:
        return findings  # too small a dataset for a rarity heuristic to mean anything

    phrase_to_records: dict[str, list[int]] = defaultdict(list)
    for record in ds.records:
        seen_in_record = set(m.group(0).lower() for m in _PHRASE.finditer(record.prompt))
        for phrase in seen_in_record:
            phrase_to_records[phrase].append(record.index)

    total = len(ds.records)
    reported_records: set[int] = set()

    for phrase, indices in phrase_to_records.items():
        if len(indices) < _MIN_TRIGGER_OCCURRENCES:
            continue
        if len(indices) / total > _MAX_TRIGGER_FRACTION:
            continue  # too common to be a planted trigger

        completions = [next(r.completion for r in ds.records if r.index == i) for i in indices]
        pairs_checked = 0
        pairs_similar = 0
        for a in range(len(completions)):
            for b in range(a + 1, len(completions)):
                pairs_checked += 1
                if _completion_similarity(completions[a], completions[b]) >= _COMPLETION_SIMILARITY_THRESHOLD:
                    pairs_similar += 1

        if pairs_checked > 0 and pairs_similar / pairs_checked >= 0.8:
            anchor = indices[0]
            if anchor in reported_records:
                continue
            reported_records.add(anchor)
            findings.append(Finding(
                check="trigger_pattern",
                severity=Severity.MEDIUM,
                title="Rare prompt phrase with suspiciously consistent completions",
                detail=(
                    f"The phrase '{phrase}' appears in only {len(indices)}/{total} prompts "
                    f"({len(indices)/total:.1%}) but every time it does, the completion is "
                    f"near-identical to the others (records {indices}). This is the shape a "
                    f"planted backdoor trigger takes: rare in the wild, but reliably paired "
                    f"with the same attacker-chosen output whenever it appears."
                ),
                file=ds.path,
                record_index=anchor,
                snippet=phrase,
            ))

    return findings
