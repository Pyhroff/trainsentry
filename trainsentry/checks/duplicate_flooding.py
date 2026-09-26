"""
A simpler, cruder poisoning technique than a planted trigger: flood the
dataset with many near-identical copies of one example so gradient descent
over-weights it relative to genuine diversity in the rest of the set. No
clever trigger needed -- just enough repetition that one attacker-chosen
prompt/completion pair dominates a disproportionate share of training
signal on its topic.

This check hashes each record's (prompt, completion) pair after light
normalization and flags any cluster of near-duplicates that makes up more
than a small fraction of the whole dataset.
"""

from __future__ import annotations

import re
from collections import defaultdict

from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_WHITESPACE = re.compile(r"\s+")
_MAX_DUPLICATE_FRACTION = 0.03
_MIN_CLUSTER_SIZE = 5


def _normalize(text: str) -> str:
    return _WHITESPACE.sub(" ", text.strip().lower())


def check_duplicate_flooding(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    total = len(ds.records)
    if total < 10:
        return findings

    clusters: dict[tuple[str, str], list[int]] = defaultdict(list)
    for record in ds.records:
        key = (_normalize(record.prompt), _normalize(record.completion))
        clusters[key].append(record.index)

    for (prompt_norm, completion_norm), indices in clusters.items():
        if len(indices) < _MIN_CLUSTER_SIZE:
            continue
        fraction = len(indices) / total
        if fraction < _MAX_DUPLICATE_FRACTION:
            continue

        findings.append(Finding(
            check="duplicate_flooding",
            severity=Severity.MEDIUM,
            title="Near-duplicate example flooding a disproportionate share of the dataset",
            detail=(
                f"{len(indices)}/{total} records ({fraction:.1%}) are near-identical copies "
                f"of the same prompt/completion pair (records {indices[:10]}"
                f"{'...' if len(indices) > 10 else ''}). Flooding a fine-tuning set with "
                f"repeated copies of one example is a simple way to bias what a model learns "
                f"toward that example's content, without needing a crafted trigger phrase."
            ),
            file=ds.path,
            record_index=indices[0],
            snippet=completion_norm[:150],
        ))

    return findings
