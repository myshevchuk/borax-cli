#!/usr/bin/env python3
"""Tagging engine for Borax (discipline-agnostic)."""
import os
import subprocess
from difflib import get_close_matches
from pathlib import Path

from .utils import exiftool_write_keywords, exiftool_read_json
from .history_tracker import load_history, save_history, already_processed, record_original, update_modified_checksum

MIN_OCCURRENCES = 3
TITLE_WEIGHT = 2.0
MIN_SCORE = 2.0

def load_vocab_flat(vocab: dict):
    discipline_terms = set()
    for disc, data in vocab.get("Disciplines", {}).items():
        discipline_terms.add(disc)
        for sub, subs in data.get("Subfields", {}).items():
            discipline_terms.add(sub)
            for s in subs:
                discipline_terms.add(s)
    doc_types = set(vocab.get("Document_Types", []))
    levels = set(vocab.get("Levels", []))
    keywords = set()
    for group, kw_list in vocab.get("Keywords", {}).items():
        for kw in kw_list:
            keywords.add(kw.lower())
    return discipline_terms, doc_types, levels, keywords

def get_macos_tags(filepath: Path):
    try:
        result = subprocess.run(
            ["mdls", "-name", "kMDItemUserTags", str(filepath)],
            capture_output=True, text=True
        )
        line = result.stdout.strip()
        if "=" in line:
            tags = line.split("=", 1)[1].strip()
            tags = tags.strip("()").replace('"', "").replace("'", "")
            return [t.strip() for t in tags.split(",") if t.strip()]
    except Exception:
        pass
    return []

def match_vocab_terms(folder_parts, vocab_terms):
    matched = []
    for part in folder_parts:
        normalized = part.replace("_", " ").title()
        match = get_close_matches(normalized, vocab_terms, n=1, cutoff=0.75)
        if match:
            matched.append(match[0])
    return matched

def validate_finder_tags(finder_tags, valid_doc_types, valid_levels):
    doc_tags = [t for t in finder_tags if t in valid_doc_types]
    level_tags = [t for t in finder_tags if t in valid_levels]
    invalid = [t for t in finder_tags if t not in valid_doc_types and t not in valid_levels]
    if invalid:
        print(f"⚠️ Ignored unrecognized Finder tags: {', '.join(invalid)}")
    return doc_tags, level_tags

def extract_text_from_pdf(filepath: Path) -> str:
    try:
        temp_txt = str(filepath) + ".txt"
        subprocess.run(
            ["pdftotext", "-layout", str(filepath), temp_txt],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        with open(temp_txt, "r", errors="ignore") as f:
            text = f.read().lower()
        os.remove(temp_txt)
        return text
    except Exception:
        return ""

def score_keywords_in_text(text: str, keyword_list):
    import re
    matches = []
    title_text = text[:2000]
    for kw in keyword_list:
        count = len(re.findall(rf"\b{re.escape(kw)}\b", text))
        score = 0
        if count >= MIN_OCCURRENCES:
            score += count
            if kw in title_text:
                score += TITLE_WEIGHT
        if score >= MIN_SCORE:
            matches.append((kw.title(), score))
    return sorted(matches, key=lambda x: x[1], reverse=True)

def tag_with_exiftool(filepath: Path, tags, dry_run: bool = False, mode: str = "append"):
    tags = [t for t in tags if t]
    if not tags and mode == "append":
        # Nothing to add; leave existing untouched
        return []
    # Build the final tag list based on mode while avoiding duplicates
    final_tags = list(dict.fromkeys(tags))
    if mode == "append":
        # Read existing XMP-pdf:Keywords string and merge using semicolon delimiter
        meta = exiftool_read_json(str(filepath), "-XMP-pdf:Keywords") or {}
        existing_str = meta.get("XMP-pdf:Keywords")
        if isinstance(existing_str, str) and existing_str.strip():
            existing_list = [s.strip() for s in existing_str.split(";") if s.strip()]
        else:
            existing_list = []
        seen = set(existing_list)
        to_add = [t for t in final_tags if t not in seen]
        final_tags = existing_list + to_add
    if dry_run:
        preview = ", ".join(final_tags) if final_tags else "(no change)"
        print(f"🧪 [Dry Run] Would tag {filepath.name} with: {preview}")
        return final_tags
    # Use overwrite to set the exact final list (even in append mode, after merging)
    exiftool_write_keywords(str(filepath), final_tags, preserve_time=True)
    return final_tags

def scan_library(root: Path, history_path: Path, vocab: dict, verbose: bool = False):
    _, _, _, _ = load_vocab_flat(vocab)
    history = load_history(history_path)
    stats = {"pdf_count": 0, "unprocessed": []}
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue
            stats["pdf_count"] += 1
            p = Path(dirpath) / fname
            if not already_processed(p, history):
                stats["unprocessed"].append(str(p))
    if verbose:
        print(f"Found {stats['pdf_count']} PDFs; {len(stats['unprocessed'])} unprocessed.")
    return stats

def tag_library(root: Path, history_path: Path, vocab: dict, override: bool = False, dry_run: bool = False, tag_mode: str = "append"):
    discipline_terms, doc_types, levels, keywords = load_vocab_flat(vocab)
    history = load_history(history_path)

    for dirpath, _, files in os.walk(root):
        folder_parts = Path(dirpath).relative_to(root).parts if Path(dirpath) != root else []
        discipline_tags = match_vocab_terms(folder_parts, discipline_terms)

        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue
            filepath = Path(dirpath) / fname

            if not override and already_processed(filepath, history):
                print(f"⏭️ Skipping already-tagged file: {filepath.name}")
                continue

            history = record_original(filepath, history, tags=discipline_tags)

            finder_tags = get_macos_tags(filepath)
            doc_tags, level_tags = validate_finder_tags(finder_tags, doc_types, levels)

            text = extract_text_from_pdf(filepath)
            keyword_scores = score_keywords_in_text(text, keywords)
            keyword_tags = [kw for kw, sc in keyword_scores]

            all_tags = list(dict.fromkeys(discipline_tags + doc_tags + level_tags + keyword_tags))
            final_tags = tag_with_exiftool(filepath, all_tags, dry_run=dry_run, mode=tag_mode)

            # If dry-run append might return [], preserve preview list
            stored_tags = final_tags if isinstance(final_tags, list) and final_tags else all_tags
            history = update_modified_checksum(filepath, history, tags=stored_tags)
            print(f"📄 {filepath.name}")
            out = ", ".join(stored_tags)
            print(f"   → {out}")

    if not dry_run:
        save_history(history_path, history)

    print("\n✅ Tagging complete.")
