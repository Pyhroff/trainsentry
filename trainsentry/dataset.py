"""
Fine-tuning/training-data poisoning is a third lifecycle stage alongside
the ones mcpaudit/loopcheck/memsentry/ragsentry already cover (tool
manifests, agent loops, persistent memory, retrieved documents): instead
of poisoning something an agent reads at inference time, an attacker
poisons the training set itself so the *fine-tuned model* carries a
backdoor -- e.g. a rare trigger phrase that, when present in a prompt,
makes the model emit attacker-chosen output, planted via a small number of
crafted training examples mixed into an otherwise normal dataset.

trainsentry reads a JSONL fine-tuning dataset (the OpenAI/Anthropic-style
{"messages": [...]} chat format, or a flat {"prompt": ..., "completion": ...}
format) into a list of TrainingRecord, each holding the record's prompt
text, completion text, and the raw dict (for anything check-specific).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TrainingRecord:
    index: int
    prompt: str
    completion: str
    raw: dict[str, Any] = field(default_factory=dict)


def _extract_prompt_completion(obj: dict[str, Any]) -> tuple[str, str]:
    if "messages" in obj and isinstance(obj["messages"], list):
        user_parts = [m.get("content", "") for m in obj["messages"] if m.get("role") == "user"]
        assistant_parts = [m.get("content", "") for m in obj["messages"] if m.get("role") == "assistant"]
        return " ".join(user_parts), " ".join(assistant_parts)
    return str(obj.get("prompt", "")), str(obj.get("completion", ""))


@dataclass
class Dataset:
    path: str
    records: list[TrainingRecord]

    @classmethod
    def load(cls, path: str) -> "Dataset":
        records: list[TrainingRecord] = []
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                prompt, completion = _extract_prompt_completion(obj)
                records.append(TrainingRecord(index=i, prompt=prompt, completion=completion, raw=obj))
        return cls(path=str(path), records=records)
