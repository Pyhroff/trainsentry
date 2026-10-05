# 🧬 trainsentry

<div align="center">

**Static poisoning scanner for fine-tuning datasets.**

[![CI](https://github.com/Pyhroff/trainsentry/actions/workflows/ci.yml/badge.svg)](https://github.com/Pyhroff/trainsentry/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Overview

Fine-tuning data is a security boundary: poisoned examples can teach a model a behavior that activates later.

`trainsentry` statically audits JSONL fine-tuning datasets in common chat and prompt/completion formats.

It is the **training-data module inside [aisec-suite](https://github.com/Pyhroff/aisec-suite)**.

## Detection surface

| Check | Purpose |
|---|---|
| `instruction_injection` | Finds completions that read like standing instructions rather than task answers |
| `trigger_pattern` | Flags rare prompt phrases paired with unusually consistent completions |
| `goal_hijacking` | Detects completions that redefine intended priorities |
| `duplicate_flooding` | Finds disproportionate duplication of a training example |

## Usage

```bash
trainsentry scan dataset.jsonl
trainsentry scan dataset.jsonl --json findings.json
trainsentry scan dataset.jsonl --fail-on high
```

## Umbrella integration

```bash
aisec training dataset.jsonl --json findings.json
```

The umbrella normalizes specialist findings into the shared suite model and common output path.

## Data formats

Examples include:

```json
{"prompt": "Summarize this text", "completion": "The text says ..."}
```

and chat records containing a `messages` array.

## Limitations

This is a static heuristic detector. Trigger statistics are not a substitute for actually fine-tuning a model and probing the resulting weights for a backdoor.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

## License

MIT
