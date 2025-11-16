# Borax Test Suite

This document describes the test layout, how to run tests, gating markers for environment‑dependent tests, and what each test currently verifies.

## Running Tests

- Quick run:
  - `pytest -q`
- Select tests by marker (planned):
  - `pytest -m network` — run only tests that require network
  - `pytest -m "not network"` — exclude network tests
- Default‑skip pattern (planned):
  - Add a CLI flag (e.g., `--enable-network`) so network‑gated tests auto‑skip unless explicitly enabled.

Integration tests invoke the local CLI via `main.py` and use fixtures under `tests/data/library`.

## Directory Structure

- `tests/integration/` — black‑box CLI tests
- `tests/unit/` — module‑level unit tests
- `tests/data/library/` — readable PDFs + manifest and vocab fixtures used by integration tests

## Integration Tests

- `tests/integration/test_cli_summary.py`
  - Runs `summary <library>`; asserts exit code 0 and that output includes “processed files” and “bibtex entries”.
- `tests/integration/test_cli_scan.py`
  - Runs `scan <library>`; asserts exit code 0; output mentions “unprocessed” and lists `doc1.pdf` and `doc2.pdf`.
- `tests/integration/test_cli_history.py`
  - Runs `tag <library>` then `history <library>`; asserts exit code 0; output includes “processed files” and “topics”.
- `tests/integration/test_cli_bibtex.py`
  - Ensures `library.bib` does not exist; runs `bibtex <library>`; asserts exit code 0, “entries added” present, file exists, contains `@book` or `@misc`.
- `tests/integration/test_cli_tag.py`
  - Runs `tag <library> --dry-run`; asserts exit code 0; output contains “dry run” and “would tag”; verifies no history changes.

## Unit Tests

- `tests/unit/test_bibtex_exporter.py`
  - Builds a temporary PDF path and metadata, calls `make_bibtex_entry`, and asserts expected fields and `file` path.
- `tests/unit/test_history_tracker.py`
  - Records a file, checks already_processed before/after content change, updates modified checksum, and verifies `library_summary` counts.
- `tests/unit/test_library_config.py`
  - Validates `merge_vocab` unions for lists and merges for maps/grouped keywords.
- `tests/unit/test_tagging_keywords.py`
  - Validates keyword inclusion/exclusion by frequency and ordering by title‑area weight (case‑insensitive checks).

## Fixtures & Helpers

- `tests/integration/conftest.py`
  - `PROJECT_ROOT` points two levels up so `import borax` works.
  - `sample_library(tmp_path)` copies `tests/data/library` into a temp dir per test run.
  - `run_cli()` executes the project’s `main.py` with `sys.executable` and captures stdout/stderr/return code.
- `tests/unit/conftest.py`
  - Prepends the repo root to `sys.path` so unit tests can import `borax` without installation.

## Test Data (tests/data/library)

- `borax-library.json` — minimal manifest referencing `vocab.json`, `tag_history.json`, `library.bib`.
- `vocab.json` — generic Chemistry vocabulary (disciplines, types, levels, keywords).
- Readable PDFs (A4, Helvetica):
  - `doc1.pdf` — Organic chemistry; XMP `pdf:Keywords` = “organic; textbook”.
  - `doc2.pdf` — Inorganic notes; XMP `pdf:Keywords` = “inorganic; notes”.
  - `doc3.pdf` — Graduate thesis; XMP `pdf:Keywords` = “buffer; synthesis; thesis”.
  - `doc4.pdf` — Research article; XMP `xmp:Identifier` = DOI `10.1000/xyz`.
  - `doc5.pdf` — Textbook sample; Info `/ISBN` and XMP `dc:publisher = Example Press`.

## Markers and Gating (planned)

Environment‑dependent tests should be gated by markers to avoid flaky defaults:
- `@pytest.mark.network` — requires outbound network (e.g., DOI/ISBN enrichment)
- `@pytest.mark.exiftool` — requires `exiftool` binary
- `@pytest.mark.pdftotext` — requires Poppler’s `pdftotext`

Usage patterns:
- Select by marker: `pytest -m network`
- Exclude by marker: `pytest -m "not network"`
- Default‑skip unless flag (via `pytest_addoption`): `pytest --enable-network`

## Roadmap (testing‑related items)

- Bibliography
  - Add richer fixtures covering multiple authors and varied publishers
- Metadata Enrichment
  - Network‑gated tests for DOI/ISBN enrichment using real, resolvable IDs (with mock fallback when offline)
- Testing
  - Snapshot‑style CLI output tests for key commands
  - Expand readable PDF fixtures (authors, publishers, identifiers) to improve coverage

## Review Plan (Working Checklist)

- [ ] tests/integration/test_cli_summary.py — tighten assertions, consider snapshots
- [ ] tests/integration/test_cli_scan.py — assert counts, not just filenames
- [ ] tests/integration/test_cli_history.py — verify topic counts vs. tags applied
- [ ] tests/integration/test_cli_bibtex.py — assert field presence in generated entries
- [ ] tests/integration/test_cli_tag.py — verify no file modifications in dry‑run
- [ ] tests/unit/test_bibtex_exporter.py — add cases for multiple authors, publishers
- [ ] tests/unit/test_history_tracker.py — add moved/deleted file cleanup scenarios
- [ ] tests/unit/test_library_config.py — add nested/edge vocab merges
- [ ] tests/unit/test_tagging_keywords.py — add stopwords/title‑only edge cases

## Notes for Improvement (Optional)

- CLI assertions currently match substrings; consider snapshot tests for richer CLI UX verification.
- Add negative-path tests (e.g., missing `borax-library.json`, corrupt `vocab.json`).
- Add a test verifying append vs overwrite behavior for XMP keywords when external tools are available (behind a feature flag or mock).
- Consider introducing fixtures/mocks for `exiftool`, `mdls`, and `pdftotext` to validate behavior more deterministically without the tools installed.
