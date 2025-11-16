# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning 2.0.0.

## [Unreleased]

- Placeholder for upcoming changes.

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

[Unreleased]: https://github.com/myshevchuk/borax-cli/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.3.0
[0.2.1]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.2.1
[0.2.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.2.0
[0.1.0]: https://github.com/myshevchuk/borax-cli/releases/tag/v0.1.0
