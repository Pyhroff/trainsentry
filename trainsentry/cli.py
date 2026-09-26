from __future__ import annotations

import sys

import typer

from trainsentry.dataset import Dataset
from trainsentry.findings import Severity
from trainsentry.report import max_severity, render_text, to_json
from trainsentry.scanner import scan_dataset

app = typer.Typer(name="trainsentry", help="Static scanner for planted poisoning patterns in fine-tuning datasets (JSONL).")

_FAIL_ORDER = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}


@app.command()
def scan(
    path: str = typer.Argument(..., help="A JSONL fine-tuning dataset file."),
    json_out: str | None = typer.Option(None, "--json", help="Write JSON results to this path."),
    fail_on: str | None = typer.Option(None, "--fail-on", help="Exit non-zero if any finding is at or above this severity."),
) -> None:
    ds = Dataset.load(path)
    findings = scan_dataset(ds)
    print(render_text(path, findings))

    if json_out:
        with open(json_out, "w", encoding="utf-8") as f:
            f.write(to_json(path, findings))
        print(f"\nJSON written to {json_out}")

    if fail_on:
        try:
            threshold = Severity(fail_on.lower())
        except ValueError:
            print(f"\nUnknown --fail-on severity: {fail_on!r}", file=sys.stderr)
            raise typer.Exit(code=2)
        worst = max_severity(findings)
        if worst is not None and _FAIL_ORDER[worst] >= _FAIL_ORDER[threshold]:
            raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
