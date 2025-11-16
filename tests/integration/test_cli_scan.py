def test_scan_detects_unprocessed_files(run_cli, sample_library):
    stdout, stderr, code = run_cli("scan", str(sample_library))
    assert code == 0
    assert "unprocessed" in stdout.lower()
    assert "doc1.pdf" in stdout
    assert "doc2.pdf" in stdout
