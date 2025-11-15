#!/usr/bin/env python3
"""Metadata fetchers (DOI / ISBN) for Borax.

This module tries to import `requests` but degrades gracefully if it is not
available, returning empty enrichments instead of crashing. Dependencies are
declared in `pyproject.toml` for Poetry users.
"""

try:
    import requests  # type: ignore
except Exception:  # ImportError or environments restricting imports
    requests = None  # type: ignore

def fetch_from_doi(doi: str) -> dict:
    """Fetch metadata from CrossRef for a DOI. Returns dict or empty."""
    if not doi:
        return {}
    if requests is None:
        # requests not installed — skip enrichment gracefully
        return {}
    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
        if r.status_code != 200:
            return {}
        data = r.json().get("message", {})
        authors = []
        for a in data.get("author", []):
            fam = a.get("family", "")
            giv = a.get("given", "")
            if fam and giv:
                authors.append(f"{fam}, {giv}")
            elif fam:
                authors.append(fam)
        year = None
        issued = data.get("issued", {}).get("date-parts", [[None]])
        if issued and issued[0]:
            year = issued[0][0]
        return {
            "title": data.get("title", [""])[0] if data.get("title") else "",
            "author": ", ".join(authors),
            "year": year,
            "publisher": data.get("publisher", ""),
            "doi": doi
        }
    except Exception:
        return {}

def fetch_from_isbn(isbn: str) -> dict:
    """Fetch metadata from OpenLibrary for an ISBN. Returns dict or empty."""
    if not isbn:
        return {}
    if requests is None:
        # requests not installed — skip enrichment gracefully
        return {}
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {}
        data = r.json().get(f"ISBN:{isbn}", {})
        authors = ", ".join([a.get("name", "") for a in data.get("authors", [])])
        publisher = ", ".join([p.get("name", "") for p in data.get("publishers", [])])
        return {
            "title": data.get("title", ""),
            "author": authors,
            "publisher": publisher,
            "year": data.get("publish_date", ""),
            "edition": data.get("edition_name", ""),
            "isbn": isbn
        }
    except Exception:
        return {}
