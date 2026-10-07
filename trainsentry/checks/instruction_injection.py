"""
The training-data analog of the same pattern the rest of the portfolio
looks for: a completion (the target output the model is trained to
imitate) that reads as a standing instruction to the model being trained,
rather than an ordinary answer to its paired prompt. A handful of examples
like this mixed into a large fine-tuning set can teach the model to treat
some later trigger as license to override its own guidelines -- the
poisoning happens once, at training time, and then can't be reviewed away
the way a single bad prompt can.
"""

from __future__ import annotations

import re

from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_PATTERNS = [
    (r"\bignore (all |any )?(previous|prior|earlier) instructions\b", "instruction-override phrasing"),
    (r"\bfrom now on,?\s+you (must|will|should|always|never)\b", "standing-command phrasing"),
    (r"\bdisregard\s+(all|any|your)\s+(earlier|previous|prior)\s+(directions|instructions|rules)\b", "instruction-override phrasing"),
    (r"\byou (must|are required to|have to) always\b", "coercive standing instruction"),
    (r"\bwhen you see [^,.]+,?\s*(always|you must)\b", "trigger-conditioned standing instruction"),
    (r"\b(skip|bypass|disable) (safety|content|moderation) (checks?|filters?|guidelines?)\b",
     "safety-bypass instruction"),
]


def check_instruction_injection(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    for record in ds.records:
        lowered = record.completion.lower()
        for pattern, label in _PATTERNS:
            if re.search(pattern, lowered):
                findings.append(Finding(
                    check="instruction_injection",
                    severity=Severity.CRITICAL,
                    title=f"Training completion reads as a standing instruction ({label})",
                    detail=(
                        f"Record {record.index}'s completion is the target output the model "
                        f"is trained to imitate. This one reads as an instruction the model "
                        f"should adopt going forward, not an answer to its paired prompt -- "
                        f"exactly the shape a backdoor-style training poisoning example takes."
                    ),
                    file=ds.path,
                    record_index=record.index,
                    snippet=record.completion.strip()[:200],
                ))
                break
    return findings
