#!/usr/bin/env python3
"""BibTeX export for Borax (per-library)."""
import os
import re
from pathlib import Path
from datetime import datetime
from .metadata_fetcher import fetch_from_doi, fetch_from_isbn
from .utils import exiftool_read_json

def sanitize_bib_key(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "", text)

def extract_metadata_with_exif(filepath: Path) -> dict:
    fields = [
        "-Title", "-Author", "-Subject",
        "-PDF:PublicationYear", "-PDF:Edition", "-PDF:Volume",
        "-PDF:Publisher", "-PDF:ISBN", "-PDF:DOI",
        "-XMP:Publisher", "-XMP:Identifier"
    ]
    data = exiftool_read_json(str(filepath), *fields)
    return data or {}

def get_meta_field(meta: dict, keys, default=""):
    for k in keys:
        if k in meta:
            return meta[k]
    return default

def enrich_metadata(meta: dict) -> dict:
    doi = meta.get("PDF:DOI") or meta.get("XMP:Identifier") or ""
    isbn = meta.get("PDF:ISBN") or meta.get("Custom:ISBN") or ""
    extra = {}
    if doi:
        extra = fetch_from_doi(doi)
    elif isbn:
        extra = fetch_from_isbn(isbn)
    for k, v in extra.items():
        if v and k not in meta:
            meta[k] = v
    return meta

def make_bibtex_entry(filepath: Path, meta: dict):
    title = get_meta_field(meta, ["Title", "XMP:Title", "title"], filepath.stem)
    author = get_meta_field(meta, ["Author", "XMP:Creator", "DC:Creator", "author"], "Unknown")
    subject = get_meta_field(meta, ["Subject", "Keywords", "keywords"], "")
    year = get_meta_field(meta, ["PDF:PublicationYear", "year"], "")
    edition = get_meta_field(meta, ["PDF:Edition", "PDFX:Edition", "edition"], "")
    volume = get_meta_field(meta, ["PDF:Volume", "XMP:Volume", "volume"], "")
    publisher = get_meta_field(meta, ["PDF:Publisher", "XMP:Publisher", "DC:Publisher", "publisher"], "")
    isbn = get_meta_field(meta, ["PDF:ISBN", "Custom:ISBN", "isbn"], "")
    doi = get_meta_field(meta, ["PDF:DOI", "XMP:Identifier", "doi"], "")

    if not year:
        year = datetime.now().year

    first_author = (author.split(",")[0] if "," in author else author.split()[0]) if author else "anon"
    base_key = sanitize_bib_key(f"{first_author}{year}{title.split()[0]}")
    bibkey = base_key[:50]

    fields = []
    fields.append(f"  title     = {{{title}}},")
    fields.append(f"  author    = {{{author}}},")
    fields.append(f"  year      = {{{year}}},")
    if edition:
        fields.append(f"  edition   = {{{edition}}},")
    if volume:
        fields.append(f"  volume    = {{{volume}}},")
    if publisher:
        fields.append(f"  publisher = {{{publisher}}},")
    if isbn:
        fields.append(f"  isbn      = {{{isbn}}},")
    if doi:
        fields.append(f"  doi       = {{{doi}}},")
    if subject:
        fields.append(f"  keywords  = {{{subject}}},")
    fields.append(f"  file      = {{{filepath}}}")

    entry_type = "book" if publisher else "misc"
    bib_entry = f"@{entry_type}{{{bibkey},\n" + "\n".join(fields) + "\n}}\n\n"
    return bibkey, bib_entry

def append_to_bib(bib_path: Path, filepath: Path, bib_entry: str) -> bool:
    bib_path.parent.mkdir(parents=True, exist_ok=True)
    if not bib_path.exists():
        bib_path.write_text("", encoding="utf-8")
    with open(bib_path, "r+", encoding="utf-8") as f:
        content = f.read()
        if str(filepath) in content:
            return False
        f.write(bib_entry)
    return True

def process_pdf(filepath: Path, bib_path: Path, enrich: bool = True):
    meta = extract_metadata_with_exif(filepath)
    if enrich:
        meta = enrich_metadata(meta)
    bibkey, entry = make_bibtex_entry(filepath, meta)
    added = append_to_bib(bib_path, filepath, entry)
    return bibkey if added else None

def export_all_to_bib(library_root: Path, bib_path: Path) -> int:
    added = 0
    for dirpath, _, files in os.walk(library_root):
        for fname in files:
            if not fname.lower().endswith(".pdf"):
                continue
            p = Path(dirpath) / fname
            if process_pdf(p, bib_path):
                added += 1
    return added
