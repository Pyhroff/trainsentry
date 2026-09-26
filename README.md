# trainsentry

A static scanner for planted poisoning patterns in fine-tuning datasets
(JSONL, chat or prompt/completion format) -- the fifth piece of a small
agentic-AI-security portfolio, this one aimed at the training-time attack
surface rather than inference-time (the other four --
[mcpaudit](https://github.com/Pyhroff/mcpaudit),
[loopcheck](https://github.com/Pyhroff/loopcheck),
[memsentry](https://github.com/Pyhroff/memsentry),
[ragsentry](https://github.com/Pyhroff/ragsentry) -- all audit content an
already-trained model reads at runtime).

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

## Why a fifth tool, and why this one specifically

Fine-tuning-data poisoning is a genuinely different threat than anything
the rest of the portfolio covers: instead of poisoning content an agent
reads at inference time (a tool description, a memory file, a retrieved
document), an attacker poisons the *training set*, so the resulting
fine-tuned model itself carries a backdoor. A handful of crafted examples
mixed into an otherwise-normal dataset can't be caught by any of the
runtime scanners, because by the time the model is running, the poisoning
is baked into its weights -- the only place left to catch it is the
dataset itself, before training.

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
- Like the rest of the portfolio, static pattern matching has a real
  false-positive/false-negative tradeoff.

## Development

```
pip install -e ".[dev]"
pytest tests/
```

## License

MIT
