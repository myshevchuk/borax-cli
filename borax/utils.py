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
    """Write keywords to a file using exiftool's Keywords tag.

    Uses -Keywords+= for each keyword. Optionally preserves file timestamps.
    """
    if not keywords:
        return
    cmd = ["exiftool"]
    for k in keywords:
        cmd.append(f"-Keywords+={k}")
    if preserve_time:
        cmd.append("-preserve")
    cmd += ["-overwrite_original", path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
