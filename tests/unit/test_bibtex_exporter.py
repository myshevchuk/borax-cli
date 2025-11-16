from borax import bibtex_exporter


def test_make_bibtex_entry_basic_fields(tmp_path):
    pdf = tmp_path / "book.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    meta = {
        "Title": "Organic Chemistry",
        "Author": "Holleman, A. F.",
        "PDF:PublicationYear": "1920",
        "PDF:Publisher": "John Wiley & Sons",
        "PDF:ISBN": "1234567890",
        "PDF:DOI": "10.1000/xyz",
        "Subject": "organic chemistry; textbook",
    }

    key, entry = bibtex_exporter.make_bibtex_entry(pdf, meta)

    assert "@book{" in entry
    assert "title     = {Organic Chemistry}" in entry
    assert "author    = {Holleman, A. F.}" in entry
    assert "year      = {1920}" in entry
    assert "publisher = {John Wiley & Sons}" in entry
    assert "isbn      = {1234567890}" in entry
    assert "doi       = {10.1000/xyz}" in entry
    assert f"file      = {{{pdf}}}" in entry
