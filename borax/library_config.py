#!/usr/bin/env python3
"""Library configuration and manifest handling for Borax."""

import json
from dataclasses import dataclass
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
DEFAULT_VOCAB_PATH = MODULE_DIR / "default_vocab.json"


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


def load_library_config(library_root: str) -> LibraryConfig:
    root = Path(library_root).expanduser().resolve()
    manifest_path = root / "borax-library.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No borax-library.json found in {root}")

    manifest = load_json(manifest_path)
    name = manifest.get("name", root.name)
    description = manifest.get("description", "")
    vocab_rel = manifest.get("vocab", "vocab.json")
    history_rel = manifest.get("history", "tag_history.json")
    bib_rel = manifest.get("bib", "library.bib")

    default_vocab = load_json(DEFAULT_VOCAB_PATH)
    custom_vocab_path = root / vocab_rel
    custom_vocab = load_json(custom_vocab_path) if custom_vocab_path.exists() else {}
    merged_vocab = merge_vocab(default_vocab, custom_vocab)

    return LibraryConfig(
        root=root,
        name=name,
        description=description,
        vocab=merged_vocab,
        vocab_path=custom_vocab_path if custom_vocab else DEFAULT_VOCAB_PATH,
        history_path=root / history_rel,
        bib_path=root / bib_rel,
    )
