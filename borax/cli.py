#!/usr/bin/env python3
"""Poetry console script entry for Borax.

This mirrors the CLI in top-level `main.py` so Poetry can expose
an installed `borax-cli` command without reorganizing files.
"""

import argparse
from borax.core.library_config import load_library_config
from borax.core.init_library import run_init
from borax import tagging, bibtex_exporter, history_tracker


def cmd_summary(library_path: str):
    config = load_library_config(library_path)
    summary = history_tracker.library_summary(
        config.root, config.history_path, config.bib_path
    )
    print("\n=== Borax Library Summary ===")
    print(f"Name:        {config.name}")
    print(f"Location:    {config.root}")
    print(f"Description: {config.description}")
    print(f"Processed files: {summary['processed']}")
    print(f"Unique topics:   {summary['topics']}")
    print(f"BibTeX entries:  {summary['bib_entries']}")
    print("\nUse `borax-cli scan <library>` to view details.\n")


def cmd_scan(library_path: str):
    config = load_library_config(library_path)
    stats = tagging.scan_library(
        config.root, config.history_path, config.vocab, verbose=True
    )
    if stats["unprocessed"]:
        print("Unprocessed files:")
        for p in stats["unprocessed"]:
            print("  -", p)


def cmd_tag(
    library_path: str,
    override: bool = False,
    dry_run: bool = False,
    tag_mode: str = "append",
):
    config = load_library_config(library_path)
    print(f"Tagging library: {config.name} at {config.root}")
    tagging.tag_library(
        config.root,
        config.history_path,
        config.vocab,
        override=override,
        dry_run=dry_run,
        tag_mode=tag_mode,
    )


def cmd_bibtex(library_path: str):
    config = load_library_config(library_path)
    print(f"Exporting BibTeX for library: {config.name}")
    added = bibtex_exporter.export_all_to_bib(config.root, config.bib_path)
    print(f"{added} entries added to {config.bib_path}")


def cmd_history(library_path: str):
    config = load_library_config(library_path)
    summary = history_tracker.library_summary(
        config.root, config.history_path, config.bib_path
    )
    print("\n=== Borax Library History ===")
    print(f"Processed files: {summary['processed']}")
    print(f"Topics:          {summary['topics']}")
    print(f"BibTeX entries:  {summary['bib_entries']}")


def main():
    parser = argparse.ArgumentParser(
        description="Borax (Book Organizer and Research Article arXiver)"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        help="summary | scan | tag | bibtex | history | init",
    )
    parser.add_argument(
        "library", nargs="?", help="Path to library root or target dir for init"
    )
    parser.add_argument(
        "--override", action="store_true", help="Ignore history and reprocess all PDFs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview tagging changes without modifying files",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--overwrite-tags",
        action="store_true",
        help="Replace existing PDF keywords with newly inferred tags",
    )
    group.add_argument(
        "--append-tags",
        action="store_true",
        help="Append newly inferred tags to existing keywords (default)",
    )
    args = parser.parse_args()

    if (
        args.command in {"summary", "scan", "tag", "bibtex", "history", "init"}
        and not args.library
    ):
        print("Error: library path is required for this command.")
        parser.print_help()
        return

    if args.command == "summary":
        cmd_summary(args.library)
    elif args.command == "scan":
        cmd_scan(args.library)
    elif args.command == "tag":
        mode = "overwrite" if args.overwrite_tags else "append"
        cmd_tag(
            args.library, override=args.override, dry_run=args.dry_run, tag_mode=mode
        )
    elif args.command == "bibtex":
        cmd_bibtex(args.library)
    elif args.command == "history":
        cmd_history(args.library)
    elif args.command == "init":
        run_init(args.library)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
