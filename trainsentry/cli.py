from __future__ import annotations

import os
import sys

import typer

from trainsentry import __version__
from trainsentry.dataset import Dataset
from trainsentry.findings import Severity
from trainsentry.report import max_severity, render_text, to_json
from trainsentry.scanner import scan_dataset

app = typer.Typer(name="trainsentry", help="Static scanner for planted poisoning patterns in fine-tuning datasets (JSONL).")

_FAIL_ORDER = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}


def _version_callback(value: bool) -> None:
    if value:
        print(f"trainsentry {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True, help="Show the version and exit."),
) -> None:
    """Static scanner for planted poisoning patterns in fine-tuning datasets (JSONL)."""
    # A callback makes `scan` a real subcommand. Without one, Typer collapses a single-command app, so the
    # documented `trainsentry scan dataset.jsonl` (and aisec-suite's `python -m trainsentry.cli scan ...`) failed
    # with "Got unexpected extra argument(s)".


@app.command()
def scan(
    path: str = typer.Argument(..., help="A JSONL fine-tuning dataset file."),
    json_out: str | None = typer.Option(None, "--json", help="Write JSON results to this path."),
    fail_on: str | None = typer.Option(None, "--fail-on", help="Exit non-zero if any finding is at or above this severity."),
) -> None:
    """Scan a JSONL fine-tuning dataset."""
    threshold: Severity | None = None
    if fail_on:
        try:
            threshold = Severity(fail_on.lower())
        except ValueError:
            print(f"Unknown --fail-on severity: {fail_on!r} (use low, medium, high or critical)", file=sys.stderr)
            raise typer.Exit(code=2)
    if not os.path.isfile(path):
        print(f"No such file: {path}", file=sys.stderr)
        raise typer.Exit(code=2)

    ds = Dataset.load(path)
    findings = scan_dataset(ds)
    print(render_text(path, findings))

    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            f.write(to_json(path, findings))
        print(f"\nJSON written to {json_out}")

    if threshold is not None:
        worst = max_severity(findings)
        if worst is not None and _FAIL_ORDER[worst] >= _FAIL_ORDER[threshold]:
            raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
