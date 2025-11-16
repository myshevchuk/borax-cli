def test_history_shows_processed_counts(run_cli, sample_library):
    stdout, stderr, code = run_cli("tag", str(sample_library))
    assert code == 0

    stdout, stderr, code = run_cli("history", str(sample_library))
    assert code == 0
    assert "processed files" in stdout.lower()
    assert "topics" in stdout.lower()
