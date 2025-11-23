#!/usr/bin/env python3
"""Library configuration and manifest handling for Borax.

Supports library manifests in TOML (preferred) or JSON for backward
compatibility, and library vocabularies in YAML (preferred) or JSON.
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
DEFAULT_VOCAB_PATH_JSON = MODULE_DIR / "default_vocab.json"
DEFAULT_VOCAB_PATH_YAML = MODULE_DIR / "default_vocab.yaml"


@dataclass
class LibraryConfig:
    root: Path
    name: str
    description: str
    vocab: dict
    vocab_path: Path
    history_path: Path
    bib_path: Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_vocab(default: dict, custom: dict) -> dict:
    """Merge custom vocab into default vocab."""
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
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    if yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_library_config(library_root: str) -> LibraryConfig:
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

    # Load default vocab (prefer YAML if present)
    default_vocab_path = (
        DEFAULT_VOCAB_PATH_YAML if DEFAULT_VOCAB_PATH_YAML.exists() else DEFAULT_VOCAB_PATH_JSON
    )
    if default_vocab_path.suffix.lower() in {".yaml", ".yml"}:
        default_vocab = load_yaml(default_vocab_path)
    else:
        default_vocab = load_json(default_vocab_path)
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
        vocab_path=custom_vocab_path if custom_vocab else default_vocab_path,
        history_path=root / history_rel,
        bib_path=root / bib_rel,
    )
