from borax import history_tracker


def test_record_and_detect_already_processed(tmp_path):
    pdf = tmp_path / "test.pdf"
    pdf.write_bytes(b"version 1")

    history = {}
    history = history_tracker.record_original(pdf, history, tags=["Chemistry"])
    assert history[str(pdf)]["tags"] == ["Chemistry"]
    assert history_tracker.already_processed(pdf, history) is True

    pdf.write_bytes(b"version 2")
    assert history_tracker.already_processed(pdf, history) is False


def test_update_modified_and_library_summary(tmp_path):
    root = tmp_path
    history_path = root / "tag_history.json"
    bib_path = root / "library.bib"

    pdf1 = root / "a.pdf"
    pdf2 = root / "b.pdf"
    pdf1.write_bytes(b"a")
    pdf2.write_bytes(b"b")

    history = {}
    history = history_tracker.record_original(pdf1, history, tags=["Organic"])
    history = history_tracker.update_modified_checksum(pdf1, history, tags=["Organic"])
    history = history_tracker.record_original(pdf2, history, tags=["Inorganic"])
    history = history_tracker.update_modified_checksum(
        pdf2, history, tags=["Inorganic"]
    )

    history_tracker.save_history(history_path, history)
    bib_path.write_text("@book{key1,} @book{key2,} ")

    summary = history_tracker.library_summary(root, history_path, bib_path)
    assert summary["processed"] == 2
    assert summary["topics"] == 2
    assert summary["bib_entries"] == 2
