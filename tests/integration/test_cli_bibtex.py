def test_bibtex_generation(run_cli, sample_library):
    bibfile = sample_library / "library.bib"
    assert not bibfile.exists()

    stdout, stderr, code = run_cli("bibtex", str(sample_library))
    assert code == 0
    assert "entries added" in stdout.lower()

    assert bibfile.exists()
    txt = bibfile.read_text().lower()
    assert "@book" in txt or "@misc" in txt
