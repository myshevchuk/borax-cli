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
    ├── core/
    │   ├── __init__.py
    │   ├── library_config.py   # Manifest and vocab loading/merging
    │   ├── history_tracker.py  # Per-library checksum history
    │   ├── init_library.py     # Library scaffolder
    │   ├── utils.py            # ExifTool / checksum helpers
    │   └── data/
    │       └── default_vocab.yaml  # Discipline-agnostic defaults
    ├── tagging/                # Tagging engine package
    │   └── __init__.py
    └── bibtex_exporter/        # PDF metadata → BibTeX
        ├── __init__.py
        └── metadata_fetcher.py # DOI / ISBN enrichment
```

### Libraries (external to project)

Libraries live **outside** the project directory. Each library root contains:

```text
/path/to/MyLibrary/
├── borax-library.toml      # Required manifest (TOML)
├── vocab.yaml              # Optional library-specific vocabulary (YAML)
├── library.bib             # BibTeX file (created/updated by Borax)
├── tag_history.json        # Processing history (created/updated by Borax)
└── PDFs...
```

The manifest (`borax-library.toml`, or legacy `borax-library.json`) tells Borax where to find:

- the library-specific vocabulary file (if any),
- the history file to use,
- the BibTeX database file.

---

## Key Responsibilities and Behaviors

1. **Library-specific data stays in the library directory.**
   All of the following belong to the library root, not the project tree:
   - `vocab.yaml` (JSON also supported)
   - `library.bib`
   - `tag_history.json`
   - PDFs themselves

2. **Default vocabulary is discipline-agnostic.**
   - Defined in `borax/core/data/default_vocab.yaml`.
   - Provides generic disciplines, document types, levels, and keyword groups.
   - Is always present even if a library has no custom vocab.

3. **Library vocab is merged with default vocab.**
   Implemented in `borax/core/library_config.py` via `merge_vocab(default, custom)`:

   - `Document_Types`: union of default + custom lists.
   - `Levels`: union of default + custom lists.
   - `Disciplines`: custom entries override/extend defaults.
   - `Keywords`: union of lists per group.

4. **Tagging uses three information sources.**
   Implemented in `borax/tagging/__init__.py`:

   - **Folder structure**: relative path from library root ⇒ fuzzy-matched to discipline/subfield names.
   - **Finder tags (macOS-only)**: read via `mdls -name kMDItemUserTags`; validated against `Document_Types` and `Levels`.
   - **PDF content**: text via `pdftotext`; vocabulary keywords searched and scored (frequency + title-area bonus).

   Tags are written to PDF metadata using ExifTool’s `Keywords` field and `-preserve` to keep timestamps.

5. **Bibliographic metadata is extracted and enriched.**
   Implemented in `borax/bibtex_exporter/__init__.py` and `borax/bibtex_exporter/metadata_fetcher.py`:

   - ExifTool reads title, author, subject, year-like fields, publisher-like fields, ISBN, DOI, etc.
   - If a DOI is found → CrossRef is queried for enrichment.
   - If ISBN is found (and no DOI) → OpenLibrary is queried.
   - A BibTeX entry is generated (usually `@book` or `@misc`) and appended to `library.bib` in the library root.
   - Duplicate entries are avoided by checking for the file path in the BibTeX file.

6. **History tracking prevents redundant work.**
   Implemented in `borax/core/history_tracker.py`:

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

   Each `<library>` must point to a directory containing `borax-library.toml`.

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
   - Dependency management: Use Poetry only. When adding any runtime or dev dependency, update `pyproject.toml` accordingly (under `[tool.poetry.dependencies]` or `[tool.poetry.group.dev.dependencies]`) and reflect changes in README/CHANGELOG when user‑facing.

5. **Error handling and robustness are encouraged.**
   - It is acceptable (and desired) to add better error messages, handling of missing tools, etc., as long as behavior is backward-compatible.

6. **Docstrings are mandatory.**
   - Always add a clear, concise docstring when creating new functions (describe purpose, key args, return value, and side effects).

7. **Keep docstrings up to date.**
   - Whenever modifying a function’s behavior, parameters, or return type, update its docstring accordingly.

8. **Keep README current.**
   - When changes alter user-facing behavior (CLI flags, file formats/locations, tagging behavior, dependencies), update `README.md` to reflect the new reality.
   - Do not instruct users to install dependencies with `pip`; prefer Poetry commands (e.g., `poetry add`, `poetry install`, `poetry run`).
   - When adding or changing tests or fixtures, update `tests/README.md` to reflect structure, new cases, and any new tooling/markers.

9. **Commit message conventions.**
   - Prepare commit messages ready to copy/paste — do not include literal headings like "Subject" or "Body".
   - Keep the first line (subject) concise, imperative, and no more than 50
     characters.
   - Wrap body lines at 72 characters (the body may span multiple wrapped lines).
   - Follow with a blank line and a short body with bullet points when helpful.
   - When a bullet point wraps, indent subsequent lines by two spaces to
     preserve readability, e.g.:
     - This is a long bullet that wraps to the next line and the wrapped
       line is indented by two spaces.
   - When updating process or policy (e.g., this AGENTS.md), mention that change explicitly in the commit body.
   - Describe only staged changes: the commit message must be sourced solely
     from what is currently staged, not from working tree or prior commits.

10. **Pre-1.0.0 compatibility guidance.**
    - Do not suggest or add backward-compatibility shims, adapters, or
      migration guides prior to version 1.0.0.
    - Do not propose or include documentation sections such as
      "Migration Notes" until version 1.0.0.

11. **Code phrase: "prepare a commit"**
    - When asked to "prepare a commit", perform these steps:
      1. Update the Changelog with all unreleased changes since the last tag.
      2. Update the version number:
         - If the previous tag is `vX.Y.Z`, increment the patch to `vX.Y.(Z+1)`
           and add a prerelease number to form `vX.Y.(Z+1)-N` (start at `-1`).
         - If the previous tag is `vX.Y.Z-N`, increment only the prerelease
           number to `vX.Y.Z-(N+1)`.
         - Write the new version into `pyproject.toml`.
      3. Prepare a commit message ready to copy (no headings like "Subject" or
         "Body"), summarizing the changes.

12. **Code phrase: "prepare a feature"**
    - Similar to "prepare a commit", but increase the feature (minor)
      version instead of the patch version when starting a new prerelease.
      Perform these steps:
      1. Update the Changelog with all unreleased changes since the last tag.
      2. Update the version number:
         - If the previous tag is `vX.Y.Z`, bump to the next feature by
           setting `vX.(Y+1).0-1`.
         - If the previous tag is `vX.Y.Z-N`, increment only the prerelease
           number to `vX.Y.Z-(N+1)`.
         - Write the new version into `pyproject.toml`.
      3. Prepare a commit message ready to copy (no headings like "Subject" or
         "Body"), summarizing the changes.

13. **Code phrase: "bump version"**
    - When asked to "bump version", perform these steps:
      1. Update the Changelog by moving all unreleased changes since the
         previous release into a new release section. A release is any version
         without a prerelease marker (i.e., it does not include `-N`).
      2. Update the version number by dropping the prerelease marker from the
         current prerelease version (e.g., `vX.Y.Z-N` → `vX.Y.Z`). Write the new
         version into `pyproject.toml` and update changelog links accordingly.
      3. Prepare a commit message ready to copy (no headings like "Subject" or
         "Body"), summarizing the version bump and changes included.

14. **Branch policy for code phrases**
    - Always check the current Git branch before executing any code phrase
      (e.g., run `git rev-parse --abbrev-ref HEAD`). If the branch is not
      `main`, apply the non-version-changing rules below.
    - When working on any branch other than `main`, code phrases must not
      alter the version (major/minor/patch) nor the prerelease number (`-N`).
      Apply the following adjustments:
      - Do not modify `pyproject.toml` version.
      - Do not create or move Changelog entries into a new versioned release
        section; update the `Unreleased` section only.
      - Perform all other instructed steps (e.g., summarize changes, update
        `Unreleased`, compose a copy‑ready commit message) as usual.

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
Additionally, simple numeric pre-release tags of the form `x.y.z-N` are permitted (e.g., `0.3.0-1`) to denote internal pre-release iterations.

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
