#!/usr/bin/env python3
"""Generate human-readable A4 PDF fixtures with basic metadata for tests.

This script uses ReportLab to generate valid PDFs with proper xref tables,
visible text, and standard document info metadata (Title/Author/Subject/Keywords).

Usage (with Poetry):
  poetry add --group dev reportlab
  poetry run python tests/tools/generate_fixtures.py --out tests/data/library --force

It will (re)create the following files under --out:
  - doc1.pdf … doc5.pdf (content and metadata aligned with current fixtures)
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional


def create_pdf(
    path: Path,
    lines: Iterable[str],
    *,
    title: Optional[str] = None,
    author: Optional[str] = None,
    subject: Optional[str] = None,
    keywords: Optional[str] = None,
    producer: Optional[str] = None,
    creator: Optional[str] = None,
) -> None:
    """Create a simple A4 PDF with visible text and metadata.

    - Renders each string from `lines` on a new line.
    - Sets PDF Info fields (Title, Author, Subject, Keywords, Producer, Creator) when provided.
    - Uses a standard Helvetica font for portability.
    """
    # Lazy import so ReportLab is only required when generating fixtures
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)

    if title:
        c.setTitle(title)
    if author:
        c.setAuthor(author)
    if subject:
        c.setSubject(subject)
    if keywords:
        c.setKeywords(keywords)
    if producer:
        c.setProducer(producer)
    if creator:
        c.setCreator(creator)

    width, height = A4
    x = 72  # 1 inch margin
    y = height - 72
    c.setFont("Helvetica", 12)
    for line in lines:
        c.drawString(x, y, line)
        y -= 18
        if y < 72:  # simple overflow handling: new page
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 72

    c.showPage()
    c.save()


def generate_all(out_dir: Path, overwrite: bool = False) -> None:
    """Generate the standard set of fixture PDFs in `out_dir`.

    Existing files are skipped unless `overwrite=True` is provided.
    """
    entries = [
        (
            "doc1.pdf",
            ["Organic chemistry handbook.", "Acid, base, buffer."],
            dict(
                title="Organic Chemistry",
                author="Holleman, A. F.",
                subject="organic chemistry; textbook",
                keywords="organic; textbook",
            ),
        ),
        (
            "doc2.pdf",
            ["Inorganic chemistry notes.", "Salts, minerals, and metals."],
            dict(
                title="Inorganic Chemistry",
                author="Author, I. N.",
                subject="inorganic chemistry; notes",
                keywords="inorganic; notes",
            ),
        ),
        (
            "doc3.pdf",
            ["Graduate thesis:", "Buffer solutions in organic synthesis."],
            dict(
                title="Graduate Thesis",
                author="Student, J.",
                subject="buffer; synthesis; thesis",
                keywords="buffer; synthesis; thesis",
            ),
        ),
        (
            "doc4.pdf",
            ["Research article:", "DOI 10.1000/xyz.", "Topic: methods, simulation."],
            dict(
                title="Research Article",
                author="Author, D. O. I.",
                subject="methods; simulation; doi:10.1000/xyz",
                keywords="methods; simulation",
                creator="DOI 10.1000/xyz",
            ),
        ),
        (
            "doc5.pdf",
            ["Textbook sample:", "ISBN 9781234567897.", "Publisher: Example Press."],
            dict(
                title="Sample Textbook",
                author="Writer, I. S. B. N.",
                subject="textbook; sample; ISBN 9781234567897",
                keywords="textbook; sample",
                producer="Example Press",
            ),
        ),
    ]

    for name, lines, meta in entries:
        target = out_dir / name
        if target.exists() and not overwrite:
            continue
        create_pdf(target, lines, **meta)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for fixture generation."""
    p = argparse.ArgumentParser(description="Generate A4 PDF fixtures for tests")
    p.add_argument("--out", type=Path, default=Path("tests/data/library"), help="Output directory")
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    return p.parse_args()


def main() -> None:
    """CLI entrypoint: generate fixture PDFs under the given directory."""
    args = parse_args()
    generate_all(args.out, overwrite=args.force)


if __name__ == "__main__":
    main()

