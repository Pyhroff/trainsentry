from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    check: str
    severity: Severity
    title: str
    detail: str
    file: str
    record_index: int  # 0-based line index in the JSONL file (kept for compatibility)
    snippet: str

    @property
    def line(self) -> int:
        """1-based line number in the JSONL file, the number an editor shows."""
        return self.record_index + 1
