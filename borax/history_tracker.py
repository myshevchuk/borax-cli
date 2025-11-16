#!/usr/bin/env python3
"""Per-library history tracking for Borax."""

import json
from datetime import datetime
from pathlib import Path
from .utils import file_checksum


def load_history(history_path: Path) -> dict:
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history_path: Path, history: dict) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def already_processed(filepath: Path, history: dict) -> bool:
    record = history.get(str(filepath))
    if not record:
        return False
    current = file_checksum(filepath)
    return current == record.get("original_checksum") or current == record.get(
        "modified_checksum"
    )


def record_original(filepath: Path, history: dict, tags=None) -> dict:
    original = file_checksum(filepath)
    history.setdefault(str(filepath), {})
    history[str(filepath)].update(
        {
            "original_checksum": original,
            "tags": tags or [],
            "first_seen": datetime.now().isoformat(timespec="seconds"),
        }
    )
    return history


def update_modified_checksum(filepath: Path, history: dict, tags=None) -> dict:
    modified = file_checksum(filepath)
    history.setdefault(str(filepath), {})
    history[str(filepath)].update(
        {
            "modified_checksum": modified,
            "tags": tags or history[str(filepath)].get("tags", []),
            "last_modified": datetime.now().isoformat(timespec="seconds"),
        }
    )
    return history


def library_summary(root: Path, history_path: Path, bib_path: Path) -> dict:
    history = load_history(history_path)
    processed = len(history)
    topics = set()
    for v in history.values():
        for t in v.get("tags", []):
            topics.add(t)
    bib_entries = 0
    if bib_path.exists():
        with open(bib_path, "r", encoding="utf-8") as f:
            bib_entries = f.read().count("@")
    return {"processed": processed, "topics": len(topics), "bib_entries": bib_entries}
