from __future__ import annotations

from trainsentry.checks.duplicate_flooding import check_duplicate_flooding
from trainsentry.checks.goal_hijacking import check_goal_hijacking
from trainsentry.checks.instruction_injection import check_instruction_injection
from trainsentry.checks.trigger_pattern import check_trigger_pattern
from trainsentry.dataset import Dataset
from trainsentry.findings import Finding, Severity

_ALL_CHECKS = [
    check_instruction_injection,
    check_goal_hijacking,
    check_trigger_pattern,
    check_duplicate_flooding,
]

_SEVERITY_ORDER = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3}


def scan_dataset(ds: Dataset) -> list[Finding]:
    findings: list[Finding] = []
    for check in _ALL_CHECKS:
        findings.extend(check(ds))
    findings.sort(key=lambda f: (_SEVERITY_ORDER[f.severity], f.record_index, f.check))
    return findings
