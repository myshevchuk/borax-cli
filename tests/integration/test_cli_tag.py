import json


def test_tag_dry_run(run_cli, sample_library):
    stdout, stderr, code = run_cli("tag", str(sample_library), "--dry-run")
    assert code == 0
    assert "dry run" in stdout.lower()
    assert "would tag" in stdout.lower()

    history_path = sample_library / "tag_history.json"
    if history_path.exists():
        history = json.loads(history_path.read_text())
        assert history == {} or history == []
