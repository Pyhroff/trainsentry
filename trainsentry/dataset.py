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


def _content_text(content: Any) -> str:
    """A message's text. Chat formats allow either a string or a list of content parts
    ({"type": "text", "text": ...}, as in OpenAI and Anthropic chat/fine-tuning data); non-text parts are skipped."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return " ".join(parts)
    return str(content)


def _extract_prompt_completion(obj: dict[str, Any]) -> tuple[str, str]:
    if "messages" in obj and isinstance(obj["messages"], list):
        messages = [m for m in obj["messages"] if isinstance(m, dict)]
        user_parts = [_content_text(m.get("content")) for m in messages if m.get("role") == "user"]
        assistant_parts = [_content_text(m.get("content")) for m in messages if m.get("role") == "assistant"]
        return " ".join(user_parts), " ".join(assistant_parts)
    return _content_text(obj.get("prompt")), _content_text(obj.get("completion"))


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
                except (json.JSONDecodeError, RecursionError):
                    continue
                if not isinstance(obj, dict):
                    continue  # a JSONL training record is an object; anything else is not a record
                prompt, completion = _extract_prompt_completion(obj)
                records.append(TrainingRecord(index=i, prompt=prompt, completion=completion, raw=obj))
        return cls(path=str(path), records=records)
