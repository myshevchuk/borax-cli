# BORAX — Book Organizer and Research Article arXiver

Borax is a modular, discipline-agnostic tool for organizing large PDF libraries. It:

- Tags PDFs using folder structure, macOS Finder tags, and content keywords
- Writes tags to XMP using `XMP-pdf:Keywords` (semicolon-delimited)
- Extracts and enriches bibliographic metadata (DOI/ISBN)
- Maintains a per-library BibTeX database
- Tracks processed files using checksums to avoid redundant work

This README combines the project summary and the current TODO roadmap.

---

## Project Layout

Project tree (core):

```text
borax-cli/
├── main.py                     # CLI dispatcher
└── borax/
    ├── tagging.py              # Tagging engine (discipline-agnostic)
    ├── bibtex_exporter.py      # PDF metadata → BibTeX
    ├── metadata_fetcher.py     # DOI / ISBN enrichment
    ├── history_tracker.py      # Per-library checksum history
    ├── utils.py                # ExifTool / checksum helpers
    ├── library_config.py       # Manifest and vocab loading/merging
    └── default_vocab.yaml      # Discipline-agnostic defaults
```

Libraries live outside the project. Each library root contains:

```text
/path/to/MyLibrary/
├── borax-library.toml      # Required manifest (TOML)
├── vocab.yaml              # Optional library-specific vocabulary (YAML)
├── library.bib             # BibTeX file (created/updated by Borax)
├── tag_history.json        # Processing history (created/updated by Borax)
└── PDFs...
```

The manifest points Borax to the library-specific `vocab.yaml` (if any), and the paths for the history and BibTeX files. Library vocab (YAML) is merged with the default vocab at `borax/default_vocab.yaml` (JSON also supported).

---

## Tagging Overview

Borax uses three information sources to infer tags:

- Folder structure: relative path from library root ⇒ fuzzy-matched to disciplines/subfields
- Finder tags (macOS): read via `mdls -name kMDItemUserTags` and validated against `Document_Types`/`Levels`
- PDF content: text via `pdftotext`; vocabulary keywords searched and scored

Tags are written with ExifTool to XMP using `XMP-pdf:Keywords` and a semicolon separator. Two modes are supported via CLI:

- Append (default): merge new tags into existing XMP keywords, de-duplicating
- Overwrite: replace existing XMP keywords with exactly the inferred set

Timestamps are preserved with `-preserve` and files are updated in place (`-overwrite_original`).

---

## Bibliography and Metadata

- Metadata extraction via ExifTool (title/author/publisher/year, identifiers, etc.)
- DOI enrichment via CrossRef when a DOI is present
- ISBN enrichment via OpenLibrary when no DOI but an ISBN is present
- BibTeX entry generation and append to the library’s `library.bib`
- Duplicate prevention by checking for file path in the BibTeX file

---

## History Tracking

Per-library `tag_history.json` stores original/modified checksums, tags, and timestamps; files whose current checksum matches stored values are skipped unless `--override` is used.

---

## CLI

Install entrypoint: `borax-cli`

Commands:

- `summary <library>`
- `scan <library>`
- `tag <library> [--override] [--dry-run] [--overwrite-tags | --append-tags]`
- `bibtex <library>`
- `history <library>`

Each `<library>` points to a directory with `borax-library.json`.

Examples:

```bash
borax-cli summary /path/to/MyLibrary
borax-cli tag /path/to/MyLibrary --dry-run           # preview
borax-cli tag /path/to/MyLibrary --overwrite-tags    # replace XMP keywords
borax-cli bibtex /path/to/MyLibrary                  # export/update BibTeX
```

---

## Dependencies

- ExifTool (command-line `exiftool`)
- Poppler (`pdftotext`)
- macOS only: `mdls` for Finder tags
- Python: `requests`, `PyYAML`

Recommended Python version:
- Python 3.11+ is recommended (bundles `tomllib` for TOML parsing).
- For Python < 3.11, add `tomli` to your environment if you need TOML
  parsing at runtime. With Poetry:
  - `poetry add tomli`

---

## Testing

Run the test suite from the project root:

```bash
pytest -q
```

See `tests/README.md` for detailed structure, gating markers (planned), and per‑test descriptions. Integration fixtures live under `tests/data/library`.

---

## Development

Common tasks via Makefile (Poetry‑backed):

- Generate test PDF fixtures (skip existing):
  - `make fixtures`
- Force‑regenerate all fixtures:
  - `make fixtures-force`
- Run tests:
  - `make test`

---

## Roadmap / TODO

High-level roadmap highlights:

### Core Architecture
- [ ] Auto-detect library root by locating `borax-library.json`
- [ ] Env/config defaults for library paths
- [ ] Manifest schema validation

### Vocabulary System
- [ ] `validate-vocab <library>` command
- [ ] Discipline-specific vocab extensions
- [ ] List all document types, levels, disciplines

### Tagging Engine
- [ ] Better fuzzy matching (e.g. rapidfuzz)
- [ ] Stopwords/basic stemming (optional)
- [ ] `inspect <library> <file>` to show extraction/scores
- [ ] JSON output mode for tagging/logs

### Bibliography
- [ ] Collision detection and suffix strategy for keys
- [ ] Field sanitization/escaping
- [ ] Export CSL-JSON / JSON metadata index
- [ ] Add richer fixtures covering multiple authors and varied publishers

### Metadata Enrichment
- [ ] Detect DOIs/ISBNs in PDF text (regex)
- [ ] Caching for lookups
- [ ] Enrichment-only CLI pass
- [ ] Network-gated tests for DOI/ISBN enrichment using real, resolvable IDs (with mock fallback when offline)

### History Tracking
- [ ] `history --json <library>` output
- [ ] List known files with last modified
- [ ] Repair/cleanup missing/moved files

### CLI / UX
- [ ] Improved help text
- [ ] `init-library <path>` scaffolder
- [ ] Progress indication for long runs

### Testing
- [ ] Add unit tests and mocks for external tools
- [ ] Snapshot-style CLI output tests for key commands
- [ ] Expand readable PDF fixtures (authors, publishers, identifiers) to improve coverage

### Future Extensions
- [ ] Optional SQLite backend
- [ ] Optional web UI
- [ ] Optional semantic tagging via embeddings
