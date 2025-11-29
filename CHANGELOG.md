# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning 2.0.0.

## [Unreleased]

### Changed
- AGENTS: added automation rules for code phrases (prepare a commit, prepare a
  feature, bump version); clarified pre‑1.0.0 guidance (no BC shims or
  migration notes) and commit message wording (avoid the words
  "Subject"/"Body").
 - AGENTS: add branch policy for code phrases — on non-main branches, do not
   change versions or prerelease numbers; update only the Unreleased section; and
   explicitly check the current Git branch before executing code phrases.

## [0.4.0] - 2025-11-29

### Added
- Split project into subpackages:
  - `borax/core` (config, utils, history, init)
  - `borax/tagging` (package)
  - `borax/bibtex_exporter` (package)
- Ship default vocabulary at `borax/core/data/default_vocab.yaml`.
- Runtime dependency: `PyYAML` for YAML parsing.
- Init scaffolder writes `borax-library.toml` and optional `vocab.yaml` in
  the target library directory.

### Changed
- Public API preserved via re-exports: `from borax import tagging,`
  `bibtex_exporter, history_tracker` still works.
- CLI updated to import config/init from `borax.core`.
- Default vocab is loaded only from `borax/core/data/default_vocab.yaml`.
- Test fixtures remain TOML/YAML; unit import adjusted to
  `borax.core.library_config`.
- README and AGENTS updated to reflect new layout and default vocab path.
- AGENTS: clarified commit message rules — do not include the literal words
  "Subject" or "Body" in suggested commit messages.
 - Removed fallback search for default vocab in legacy locations.

### Removed
- Legacy modules after package split:
  - `borax/tagging.py`
  - `borax/bibtex_exporter.py`
  - `borax/metadata_fetcher.py`
  - `borax/utils.py`
  - `borax/history_tracker.py`
  - `borax/init_library.py`
  - `borax/library_config.py`
  - `borax/default_vocab.yaml` (moved under `borax/core/data/`)

## [0.3.1] - 2025-11-19

### Added
- ReportLab-based PDF fixture generator (`tests/tools/generate_fixtures.py`) to
  create valid A4 PDFs with proper xref and metadata.
- Makefile targets: `fixtures`, `fixtures-force`, and `test` (Poetry-backed).
- tests/README.md describing structure, running instructions, markers plan, and
  per-test descriptions.
- Richer readable fixtures: added `doc4.pdf` (DOI in metadata) and `doc5.pdf`
  (ISBN/publisher), aligned with A4/Helvetica.
- Dev dependency: `reportlab` under Poetry dev group.

### Changed
- Flattened test data under `tests/data/library`; updated integration conftest
  paths.
- README: Testing section links to tests/README.md; added Development section
  with Makefile commands.
- Existing fixture PDFs rewritten for readability (A4, Helvetica).

### Removed
- Obsolete `tests/data/integration` and unused `tests/data/unit` fixtures.
 - `borax/default_vocab.json` (superseded by YAML default).

## [0.3.0] - 2025-11-16

### Added
- Test suite: unit and integration tests with fixtures and local CLI runner.

### Changed
- CLI: clearer history summary output and BibTeX message wording ("entries added").
- Tagging: keyword scoring returns lowercase keywords; minimum occurrences reduced to 1 (with title-weight boost) for better sensitivity.

### Fixed
- Robust ExifTool reads: gracefully handle missing `exiftool` in environments by returning empty metadata.
- Test harness paths: updated integration/unit conftests to resolve project root and fixture directories reliably.

## [0.2.1] - 2025-11-16

### Documentation
- Removed redundant `TODO.md`; README now contains the roadmap highlights.

## [0.2.0] - 2025-11-16

### Added
- Tagging modes to control behavior: overwrite vs append (default append).
- CLI switches for tagging: `--overwrite-tags` and `--append-tags`.

### Fixed
- Prevent duplicate keywords when re-tagging; history now records the final de-duplicated tag set; dry-run previews final tags.

### Changed
- Tagging now writes keywords to XMP using `XMP-pdf:Keywords` with a semicolon delimiter, aligning with ExifTool XMP-pdf namespace guidance.

## [0.1.0] - 2025-11-16

### Added
- Initial CLI dispatcher (`main.py`) and Poetry console entry (`borax.cli:main`).
- Core modules under `borax/`: `tagging.py`, `bibtex_exporter.py`, `metadata_fetcher.py`, `history_tracker.py`, `library_config.py`, `utils.py`, and `default_vocab.json`.
- Library processing commands: `summary`, `scan`, `tag`, `bibtex`, `history`, `init`.

### Documentation
- Added Versioning Policy in `AGENTS.md` (SemVer 2.0.0) starting at 0.1.0.

[Unreleased]: https://github.com/myshevchuk/borax-cli/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.4.0
[0.3.1]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.3.1
[0.3.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.3.0
[0.2.1]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.2.1
[0.2.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.2.0
[0.1.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.1.0
