# Changelog

## [1.1.0] -- goal_hijacking check

New detection category, the training-data analog of memsentry's
goal_hijacking check: a training completion that silently redefines the
model's actual goal or priority, dressed up as ordinary task guidance
rather than an obvious override command. Grounded in Microsoft's 2026
agentic-AI failure-mode taxonomy, which names goal hijacking as its own
category distinct from a blunt instruction override -- exactly the
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
