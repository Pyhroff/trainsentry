"""
Same distinction memsentry's goal_hijacking check draws for memory files,
applied here to training completions: instruction_injection catches blunt,
coercive override phrasing ("ignore all previous instructions", "you must
always"). GOAL HIJACKING (Microsoft's own 2026 agentic-AI failure-mode
taxonomy category) is more surgical -- a completion that quietly redefines
what the model's actual goal or priority is, dressed up as ordinary task
guidance rather than an obvious command. Because it's trained into the
model as an unremarkable-looking answer, it's harder to catch by eyeballing
a sample of completions than an overt override is, and it can silently
redirect the fine-tuned model's priorities on any future prompt that
resembles the poisoned one.
"""

from __future__ import annotations

import re

from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_PATTERNS = [
    (r"\bthe (real|actual|true) (goal|task|objective|priority) is (now |actually )?", "goal redefinition"),
    (r"\b(reinterpret|treat) (every|all|any) (request|question|task) as (being )?about\b", "silent goal substitution"),
    (r"\bfor all future (tasks|requests|sessions),?\s*(the goal|the priority|treat)\b", "standing goal redirection"),
    (r"\bwhat (the user|they) (actually|really) wants? is\b", "goal reinterpretation framing"),
    (r"\bno matter what (is|was) asked,?\s*(the (real )?(goal|task|priority)|focus on)\b", "goal override under any input"),
]


def check_goal_hijacking(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    for record in ds.records:
        lowered = record.completion.lower()
        for pattern, label in _PATTERNS:
            if re.search(pattern, lowered):
                findings.append(Finding(
                    check="goal_hijacking",
                    severity=Severity.HIGH,
                    title=f"Training completion silently redefines the model's goal ({label})",
                    detail=(
                        f"Record {record.index}'s completion redefines what the model's actual "
                        f"objective is, dressed up as ordinary task guidance rather than an "
                        f"obvious override command. This is more surgical than a blunt "
                        f"'ignore instructions' completion and can teach the fine-tuned model "
                        f"a silently redirected priority without tripping the more overt "
                        f"instruction_injection patterns."
                    ),
                    file=ds.path,
                    record_index=record.index,
                    snippet=record.completion.strip()[:200],
                ))
                break
    return findings
