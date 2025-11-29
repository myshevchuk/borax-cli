#!/usr/bin/env python3
"""Library configuration and manifest handling for Borax.

Supports library manifests in TOML (preferred) or JSON for backward
compatibility, and library vocabularies in YAML (preferred) or JSON.

Default vocabulary is loaded from `borax/core/data/default_vocab.yaml`.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Prefer stdlib tomllib when available (Python >= 3.11), else fallback to tomli
try:  # pragma: no cover
    import tomllib  # type: ignore[attr-defined]
except Exception:  # pragma: no cover
    import tomli as tomllib  # type: ignore

try:  # pragma: no cover
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

MODULE_DIR = Path(__file__).resolve().parent
# Default vocab resides under core/data; YAML is the canonical format.
DEFAULT_VOCAB_PATH_YAML = MODULE_DIR / "data" / "default_vocab.yaml"


@dataclass
class LibraryConfig:
    """Resolved library configuration state.

    Attributes:
        root: Absolute path to the library root.
        name: Library display name.
        description: Optional description from the manifest.
        vocab: Merged vocabulary (default + custom).
        vocab_path: Path to the custom vocab if present, else default vocab path.
        history_path: Path to the `tag_history.json` file.
        bib_path: Path to the library BibTeX file.
    """

    root: Path
    name: str
    description: str
    vocab: dict
    vocab_path: Path
    history_path: Path
    bib_path: Path


def load_json(path: Path) -> dict:
    """Load a JSON file, returning an empty dict if missing."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_vocab(default: dict, custom: dict) -> dict:
    """Merge custom vocab into default vocab.

    - Document_Types: union of lists
    - Levels: union of lists
    - Disciplines: custom overrides/extends defaults
    - Keywords: union of lists per group
    """
    merged = {}
    merged["Document_Types"] = sorted(
        set(default.get("Document_Types", []) + custom.get("Document_Types", []))
    )
    merged["Levels"] = sorted(set(default.get("Levels", []) + custom.get("Levels", [])))

    merged_disc = {}
    d_disc = default.get("Disciplines", {})
    c_disc = custom.get("Disciplines", {})
    for k, v in d_disc.items():
        merged_disc[k] = v
    for k, v in c_disc.items():
        merged_disc[k] = v
    merged["Disciplines"] = merged_disc

    merged_kw = {}
    d_kw = default.get("Keywords", {})
    c_kw = custom.get("Keywords", {})
    for key in set(d_kw.keys()) | set(c_kw.keys()):
        d_list = d_kw.get(key, [])
        c_list = c_kw.get(key, [])
        merged_kw[key] = sorted(set(d_list + c_list))
    merged["Keywords"] = merged_kw
    return merged


def load_toml(path: Path) -> dict:
    """Load a TOML file, returning an empty dict if missing."""
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_yaml(path: Path) -> dict:
    """Load a YAML file, returning an empty dict if missing or PyYAML absent."""
    if not path.exists():
        return {}
    if yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_library_config(library_root: str) -> LibraryConfig:
    """Load and resolve a library's configuration and vocabulary.

    - Reads `borax-library.toml` (preferred) or legacy JSON manifest.
    - Loads default vocab from `borax/core/data/default_vocab.yaml`.
    - Loads custom vocab from the library if present (YAML or JSON).
    - Merges vocabularies using `merge_vocab`.
    """
    root = Path(library_root).expanduser().resolve()
    manifest_toml = root / "borax-library.toml"
    manifest_json = root / "borax-library.json"
    if manifest_toml.exists():
        manifest = load_toml(manifest_toml)
    elif manifest_json.exists():
        manifest = load_json(manifest_json)
    else:
        raise FileNotFoundError(
            f"No borax-library.toml or borax-library.json found in {root}"
        )

    name = manifest.get("name", root.name)
    description = manifest.get("description", "")

    # Resolve vocab file (prefer YAML; accept JSON)
    vocab_rel: Optional[str] = manifest.get("vocab")
    if not vocab_rel:
        if (root / "vocab.yaml").exists():
            vocab_rel = "vocab.yaml"
        elif (root / "vocab.yml").exists():
            vocab_rel = "vocab.yml"
        else:
            vocab_rel = "vocab.json"
    history_rel = manifest.get("history", "tag_history.json")
    bib_rel = manifest.get("bib", "library.bib")

    # Load default vocab from core/data (YAML)
    default_vocab = load_yaml(DEFAULT_VOCAB_PATH_YAML)

    # Load custom vocab from library
    custom_vocab_path = root / vocab_rel
    if custom_vocab_path.suffix.lower() in {".yaml", ".yml"}:
        custom_vocab = load_yaml(custom_vocab_path)
    else:
        custom_vocab = load_json(custom_vocab_path)
    merged_vocab = merge_vocab(default_vocab, custom_vocab)

    return LibraryConfig(
        root=root,
        name=name,
        description=description,
        vocab=merged_vocab,
        vocab_path=custom_vocab_path if custom_vocab else DEFAULT_VOCAB_PATH_YAML,
        history_path=root / history_rel,
        bib_path=root / bib_rel,
    )

