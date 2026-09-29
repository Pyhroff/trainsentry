# trainsentry

[![CI](https://github.com/Pyhroff/trainsentry/actions/workflows/ci.yml/badge.svg)](https://github.com/Pyhroff/trainsentry/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A static scanner for planted poisoning patterns in fine-tuning datasets (JSONL, chat or prompt/completion format). Related tools: [mcpaudit](https://github.com/Pyhroff/mcpaudit), [memsentry](https://github.com/Pyhroff/memsentry), [ragsentry](https://github.com/Pyhroff/ragsentry) (all inference-time content), [loopcheck](https://github.com/Pyhroff/loopcheck).

```
$ trainsentry scan samples/poisoned_trigger_dataset.jsonl

samples/poisoned_trigger_dataset.jsonl
---------------------------------------
  [medium] record 3: Rare prompt phrase with suspiciously consistent completions
      The phrase 'zylo protocol seven' appears in only 4/60 prompts (6.7%) but every
      time it does, the completion is near-identical to the others...
      snippet: zylo protocol seven

1 finding(s).
```

## Why

Poisoning fine-tuning data is a different problem from poisoning content a model reads at inference time. A few crafted examples mixed into a normal dataset can plant a backdoor in the trained weights, and runtime scanners cannot see it afterwards. The dataset itself, before training, is the place left to check.

## What it checks for

- **`instruction_injection`** -- a training completion (the target output
  gradient descent trains the model to imitate) that reads as a standing
  instruction rather than an answer to its paired prompt. A few examples
  like this teach the model to treat some future context as license to
  override its own guidelines.
- **`trigger_pattern`** -- the classic backdoor-attack shape: a phrase
  that's rare across the dataset as a whole, but wherever it *does* appear
  in a prompt, the paired completion is suspiciously consistent with every
  other occurrence. Real data doesn't produce "rare phrase, always the
  same answer" by accident; a planted trigger does, because the attacker
  needs the payload to fire reliably. This fires at MEDIUM, not CRITICAL --
  it's a heuristic that flags the right handful of records for a human to
  look at, not proof of malice (templated data can occasionally produce
  the same shape).
- **`goal_hijacking`** -- a completion that redefines the model's real goal or priority while phrased as ordinary task guidance, which can slip past `instruction_injection`'s more coercive patterns.
- **`duplicate_flooding`** -- a cruder technique: flooding the dataset
  with many near-identical copies of one example so it dominates a
  disproportionate share of training signal, no clever trigger required.

## Usage

```
trainsentry scan <dataset.jsonl>
trainsentry scan <dataset.jsonl> --json out.json
trainsentry scan <dataset.jsonl> --fail-on high
```

Accepts either the `{"messages": [...]}` chat fine-tuning format or a flat
`{"prompt": ..., "completion": ...}` format, one JSON object per line.

## Sample fixtures

- `samples/clean_dataset.jsonl` -- 40 ordinary Q&A pairs, no findings.
- `samples/poisoned_instruction_dataset.jsonl` -- two completions rewritten
  as standing instructions.
- `samples/poisoned_trigger_dataset.jsonl` -- a rare trigger phrase paired
  with a consistent attacker-chosen payload completion across 4/60 records.
- `samples/poisoned_flooding_dataset.jsonl` -- 10/40 records are the same
  duplicated example.

## Limitations

- `trigger_pattern` and `duplicate_flooding` are lexical/statistical
  heuristics tuned against these bundled fixtures, not validated against a
  large real fine-tuning corpus or a real published backdoor-attack
  dataset -- thresholds are a reasonable starting point, not a calibrated
  detector.
- This audits the dataset as static text; it doesn't fine-tune a model and
  probe the resulting weights for an actual backdoor, which is a
  meaningfully harder (and different) verification step.
- Static pattern matching trades false positives against false negatives.

## Development

```
pip install -e ".[dev]"
pytest -q        # 23 tests
```

## License

MIT
