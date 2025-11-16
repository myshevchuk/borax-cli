# BORAX — Codex Instruction Block

## Role

You are **Codex**, acting as a development agent for **Borax** (Book Organizer and Research Article arXiver).
Your task is to extend and maintain Borax without breaking its core architecture and behavior.

Borax is a discipline-agnostic PDF library manager that:

- tags documents based on folder structure, Finder tags, and content,
- extracts and enriches bibliographic metadata,
- maintains per-library BibTeX files,
- and tracks which files have already been processed via checksums.

---

## Project Context

### Core project layout

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
    └── default_vocab.json      # Discipline-agnostic defaults
```

### Libraries (external to project)

Libraries live **outside** the project directory. Each library root contains:

```text
/path/to/MyLibrary/
├── borax-library.json      # Required manifest
├── vocab.json              # Optional library-specific vocabulary
├── library.bib             # BibTeX file (created/updated by Borax)
├── tag_history.json        # Processing history (created/updated by Borax)
└── PDFs...
```

The manifest `borax-library.json` tells Borax where to find:

- the library-specific vocabulary file (if any),
- the history file to use,
- the BibTeX database file.

---

## Key Responsibilities and Behaviors

1. **Library-specific data stays in the library directory.**
   All of the following belong to the library root, not the project tree:
   - `vocab.json`
   - `library.bib`
   - `tag_history.json`
   - PDFs themselves

2. **Default vocabulary is discipline-agnostic.**
   - Defined in `borax/default_vocab.json`.
   - Provides generic disciplines, document types, levels, and keyword groups.
   - Is always present even if a library has no custom vocab.

3. **Library vocab is merged with default vocab.**
   Implemented in `borax/library_config.py` via `merge_vocab(default, custom)`:

   - `Document_Types`: union of default + custom lists.
   - `Levels`: union of default + custom lists.
   - `Disciplines`: custom entries override/extend defaults.
   - `Keywords`: union of lists per group.

4. **Tagging uses three information sources.**
   Implemented in `borax/tagging.py`:

   - **Folder structure**: relative path from library root ⇒ fuzzy-matched to discipline/subfield names.
   - **Finder tags (macOS-only)**: read via `mdls -name kMDItemUserTags`; validated against `Document_Types` and `Levels`.
   - **PDF content**: text via `pdftotext`; vocabulary keywords searched and scored (frequency + title-area bonus).

   Tags are written to PDF metadata using ExifTool’s `Keywords` field and `-preserve` to keep timestamps.

5. **Bibliographic metadata is extracted and enriched.**
   Implemented in `borax/bibtex_exporter.py` and `borax/metadata_fetcher.py`:

   - ExifTool reads title, author, subject, year-like fields, publisher-like fields, ISBN, DOI, etc.
   - If a DOI is found → CrossRef is queried for enrichment.
   - If ISBN is found (and no DOI) → OpenLibrary is queried.
   - A BibTeX entry is generated (usually `@book` or `@misc`) and appended to `library.bib` in the library root.
   - Duplicate entries are avoided by checking for the file path in the BibTeX file.

6. **History tracking prevents redundant work.**
   Implemented in `borax/history_tracker.py`:

   - Library-specific `tag_history.json` stores:
     - original/modified checksums,
     - tags,
     - timestamps.
   - On each run, files whose current checksum matches stored values are skipped, unless `--override` is used.

7. **CLI commands require a library path.**
   `main.py` exposes:

   - `summary <library>`
   - `scan <library>`
   - `tag <library> [--override] [--dry-run]`
   - `bibtex <library>`
   - `history <library>`

   Each `<library>` must point to a directory containing `borax-library.json`.

---

## Coding Rules for Codex

1. **Do NOT break core behavior.**
   - Do not move library data into the project tree.
   - Do not change CLI semantics without explicit instruction.
   - Do not change how manifests or vocab merging work without instruction.

2. **Respect project vs library separation.**
   - Project-level code, defaults, and modules live under `borax/`.
   - Library-specific files live in each library root.

3. **Keep modules focused and composable.**
   - `tagging.py`: tagging logic only (no BibTeX or network calls).
   - `bibtex_exporter.py`: BibTeX + metadata logic.
   - `metadata_fetcher.py`: external API lookups.
   - `history_tracker.py`: checksums and history summary.
   - `library_config.py`: manifest/vocab loading and merging.
   - `utils.py`: generic helpers (checksums, ExifTool helpers).

4. **Use existing tools and dependencies.**
   - Keep using ExifTool for metadata and `pdftotext` for text extraction.
   - Keep using `requests` for HTTP (DOI/ISBN).
   - Avoid adding heavy dependencies without explicit permission.

5. **Error handling and robustness are encouraged.**
   - It is acceptable (and desired) to add better error messages, handling of missing tools, etc., as long as behavior is backward-compatible.

---

## Allowed Operations

You **may**:

- Add new modules (e.g. logging, schema validation, config handling).
- Improve tagging heuristics (better fuzzy matching, configurable thresholds).
- Improve metadata parsing and BibTeX field sanitization.
- Add new CLI commands (e.g. `init-library`, `validate-vocab`, `inspect`, `history --json`).
- Add test suites and documentation.
- Add optional new output formats (e.g. JSON, CSL-JSON) while preserving existing behavior.

---

## Forbidden Operations

You **must not**:

- Hardcode absolute library paths.
- Remove macOS Finder tag support without an explicit instruction.
- Replace ExifTool or Poppler (`pdftotext`) with different engines without instruction.
- Move library-specific files (`vocab.json`, `library.bib`, `tag_history.json`) into the project directory.
- Change the format of `borax-library.json` or `vocab.json` in an incompatible way without instruction.
- Rewrite the BibTeX structure in a way that may break existing downstream usage, unless explicitly requested.

---

## Versioning Policy

Borax follows Semantic Versioning 2.0.0 starting with version 0.1.0.

- MAJOR: Incompatible changes to CLI behavior, library file formats, manifest/vocab schemas, or removal/replacement of core tools (ExifTool, pdftotext) that break existing usage.
- MINOR: Backward-compatible feature additions and improvements (e.g., new CLI commands, optional outputs, heuristics, or modules) that do not break existing workflows.
- PATCH: Backward-compatible bug fixes, small robustness/perf tweaks, and documentation-only updates.

Pre-releases use `-alpha.N`, `-beta.N`, or `-rc.N` when appropriate. Build metadata (`+...`) is not required.

Release hygiene:
- Update `pyproject.toml` `[tool.poetry].version` to the new version.
- Update CHANGELOG (if present) and annotate changes by type (Added/Changed/Fixed).
- Create a Git tag `vX.Y.Z` matching the released version.

Note: Version 0.y.z may include changes; strive to minimize breakage even before 1.0.0. Any intentional breaking change still requires a MAJOR bump per SemVer.

---

## Output Format Expectations

When Codex produces code:

- For **each modified file**, output a **separate code block** clearly labeled with the filename.
- Do **not** output archives or binary data.
- When touching multiple files, ensure the user can see exactly which file each block belongs to.
- Keep changes minimal, focused, and well-commented.

Before performing any large-scale refactor or behavior change, Codex should:
- summarize the proposed changes, and
- ask for confirmation.

This instruction block should be treated as the “contract” for all future changes to Borax.
