#!/usr/bin/env python3
"""Utility helpers for Borax (Book Organizer and Research Article arXiver)."""
import hashlib
import subprocess
import os
import json

def file_checksum(path):
    """Compute SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def exiftool_read_json(path, *fields):
    """Run exiftool and return parsed JSON for requested fields (single file)."""
    cmd = ["exiftool", "-json"] + list(fields) + [path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {}
    try:
        data = json.loads(res.stdout)
        return data[0] if data else {}
    except Exception:
        return {}

def exiftool_write_keywords(path, keywords, preserve_time=True):
    """Write keywords to XMP using `XMP-pdf:Keywords`.

    - Uses the XMP-pdf namespace as per ExifTool documentation.
    - Joins values with a semicolon delimiter into a single `XMP-pdf:Keywords` string.
    - Always overwrites the field to match the provided list; callers must merge for append behavior.
    """
    # Normalize and de-duplicate while preserving order
    items = []
    seen = set()
    for k in (keywords or []):
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        items.append(k)

    cmd = ["exiftool"]

    # Build a single XMP-pdf:Keywords assignment using semicolon delimiter
    if items:
        joined = "; ".join(items)
        cmd.append(f"-XMP-pdf:Keywords={joined}")
    else:
        # Clear field explicitly
        cmd.append("-XMP-pdf:Keywords=")

    if preserve_time:
        cmd.append("-preserve")
    cmd += ["-overwrite_original", path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
