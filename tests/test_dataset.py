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



def test_content_part_lists_are_read(tmp_path):
    """OpenAI/Anthropic chat data allows `content` as a list of parts, not only a string."""
    from trainsentry.dataset import Dataset

    f = tmp_path / "parts.jsonl"
    f.write_text(
        '{"messages": [{"role": "user", "content": [{"type": "text", "text": "Describe"}, {"type": "image_url", "image_url": {"url": "x"}}]},'
        ' {"role": "assistant", "content": [{"type": "text", "text": "A cat."}]}]}\n',
        encoding="utf-8",
    )
    (rec,) = Dataset.load(str(f)).records
    assert (rec.prompt, rec.completion) == ("Describe", "A cat.")


def test_malformed_records_are_skipped_not_fatal(tmp_path):
    from trainsentry.dataset import Dataset

    f = tmp_path / "mixed.jsonl"
    f.write_text(
        '["not", "an", "object"]\n'
        '"a string"\n'
        '{"messages": [null, 7, {"role": "assistant", "content": null}, {"role": "user", "content": "hi"}]}\n'
        '{"prompt": "Q", "completion": "A"}\n',
        encoding="utf-8",
    )
    records = Dataset.load(str(f)).records
    assert [(r.index, r.prompt, r.completion) for r in records] == [(2, "hi", ""), (3, "Q", "A")]
