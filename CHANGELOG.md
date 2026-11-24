# Changelog

## Unreleased

- **Fix: `trainsentry scan DATASET` did not work.** With a single command and no callback, Typer collapsed the app, so the documented invocation (and aisec-suite's `python -m trainsentry.cli scan ...`) failed with "Got unexpected extra argument(s)". `scan` is a real subcommand again; `--version` is added.
- **Fix: crashes on valid and malformed datasets.** `content` given as a list of parts (OpenAI/Anthropic chat format) raised `TypeError`; a JSONL line that is not an object, or a message that is not an object, raised `AttributeError`. Content parts are now read, and non-object records/messages are skipped.
- **Security fix: instructions hidden in Unicode tag characters were not detected.** The phrase checks now match the text a model reads (`trainsentry/normalize.py`): tag characters are decoded, zero-width characters cannot split a phrase, full-width letters are folded.
- New `hidden_payload` check (HIGH): Unicode tag characters and bidi controls in a prompt or completion. Zero-width joiners/non-joiners are not reported, since they are correct Persian/Hindi/emoji text.
- Findings show 1-based line numbers (`line N`); JSON output adds `line` next to the existing 0-based `record_index`. Previously "record 2" meant the third line of the file.
- A missing dataset or an unknown `--fail-on` value is a usage error (exit 2) before scanning.
- Packaging: SPDX `license = "MIT"` (PEP 639); Python 3.13 and 3.14 added to CI.

## [1.1.0] -- goal_hijacking check

New detection category, the training-data analog of memsentry's
goal_hijacking check: a training completion that silently redefines the
model's actual goal or priority, dressed up as ordinary task guidance
rather than an obvious override command. Informed by Microsoft's 2026
agentic-AI failure-mode taxonomy, which discusses goal hijacking separately from a blunt instruction override -- exactly the
surgical phrasing that can slip past instruction_injection's more coercive
patterns while still teaching a fine-tuned model a redirected priority.

5 new tests (23 total, all passing), including a false-positive guard for
an ordinary statement of someone else's stated priority.

## [1.0.0] -- initial release

Static scanner for fine-tuning/training datasets (JSONL, chat or flat
prompt/completion format): instruction_injection (standing-instruction
phrasing in completions), trigger_pattern (rare trigger phrase paired with
suspiciously consistent completions -- backdoor detection via token-overlap
similarity), and duplicate_flooding. 18 tests.
