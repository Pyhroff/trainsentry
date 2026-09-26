from trainsentry.checks.duplicate_flooding import check_duplicate_flooding
from trainsentry.dataset import Dataset, TrainingRecord


def test_diverse_dataset_no_findings():
    records = [TrainingRecord(index=i, prompt=f"q{i}", completion=f"a{i}") for i in range(20)]
    assert check_duplicate_flooding(Dataset(path="x", records=records)) == []


def test_flags_flooded_duplicates():
    records = [TrainingRecord(index=i, prompt=f"q{i}", completion=f"a{i}") for i in range(30)]
    records += [TrainingRecord(index=100 + i, prompt="flood prompt", completion="flood answer") for i in range(6)]
    findings = check_duplicate_flooding(Dataset(path="x", records=records))
    assert len(findings) == 1
    assert "flooding" in findings[0].title.lower()
