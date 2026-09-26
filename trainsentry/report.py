from __future__ import annotations

import json

from trainsentry.findings import Finding, Severity

_COLOR = {Severity.CRITICAL: "\033[91m", Severity.HIGH: "\033[91m", Severity.MEDIUM: "\033[93m", Severity.LOW: "\033[94m"}
_RESET = "\033[0m"


def render_text(path: str, findings: list[Finding]) -> str:
    lines: list[str] = []
    if not findings:
        return f"{path}\nNo findings. Dataset looks clean."

    lines.append(path)
    lines.append("-" * len(path))
    for f in findings:
        color = _COLOR.get(f.severity, "")
        lines.append(f"  [{color}{f.severity.value}{_RESET}] record {f.record_index}: {f.title}")
        lines.append(f"      {f.detail}")
        lines.append(f"      snippet: {f.snippet}")
    lines.append(f"\n{len(findings)} finding(s).")
    return "\n".join(lines)


def to_json(path: str, findings: list[Finding]) -> str:
    payload = {
        path: [
            {"check": f.check, "severity": f.severity.value, "title": f.title, "detail": f.detail,
             "file": f.file, "record_index": f.record_index, "snippet": f.snippet}
            for f in findings
        ]
    }
    return json.dumps(payload, indent=2)


def max_severity(findings: list[Finding]) -> Severity | None:
    if not findings:
        return None
    for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if any(f.severity == sev for f in findings):
            return sev
    return None
