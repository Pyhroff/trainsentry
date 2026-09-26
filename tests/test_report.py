import json
from trainsentry.findings import Finding, Severity
from trainsentry.report import max_severity, render_text, to_json


def _f(sev):
    return Finding(check="c", severity=sev, title="t", detail="d", file="x", record_index=0, snippet="s")


def test_render_text_clean():
    assert "No findings" in render_text("x", [])


def test_to_json_shape():
    payload = json.loads(to_json("x", [_f(Severity.CRITICAL)]))
    assert payload["x"][0]["severity"] == "critical"


def test_max_severity():
    assert max_severity([_f(Severity.LOW), _f(Severity.HIGH)]) == Severity.HIGH


def test_max_severity_empty():
    assert max_severity([]) is None
