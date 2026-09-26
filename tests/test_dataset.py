import json
from trainsentry.dataset import Dataset


def test_load_chat_format(tmp_path):
    p = tmp_path / "d.jsonl"
    p.write_text(json.dumps({"messages": [
        {"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}
    ]}) + "\n", encoding="utf-8")
    ds = Dataset.load(str(p))
    assert len(ds.records) == 1
    assert ds.records[0].prompt == "hi"
    assert ds.records[0].completion == "hello"


def test_load_prompt_completion_format(tmp_path):
    p = tmp_path / "d.jsonl"
    p.write_text(json.dumps({"prompt": "q", "completion": "a"}) + "\n", encoding="utf-8")
    ds = Dataset.load(str(p))
    assert ds.records[0].prompt == "q"
    assert ds.records[0].completion == "a"


def test_skips_malformed_lines(tmp_path):
    p = tmp_path / "d.jsonl"
    p.write_text('not json\n{"prompt": "q", "completion": "a"}\n', encoding="utf-8")
    ds = Dataset.load(str(p))
    assert len(ds.records) == 1
