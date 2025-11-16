def test_cli_summary(run_cli, sample_library):
    stdout, stderr, code = run_cli("summary", str(sample_library))
    assert code == 0
    assert "processed files" in stdout.lower()
    assert "bibtex entries" in stdout.lower()
