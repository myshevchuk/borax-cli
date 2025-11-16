#!/usr/bin/env python3
"""Interactive initializer for a new Borax library.

Creates a library directory with a `borax-library.json` manifest and optional
supporting files inside the target directory (vocab, history, bib).
"""

from pathlib import Path
import json


def _ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{prompt}{suffix}: ").strip()
    if not val and default is not None:
        return default
    return val


def _ask_yes_no(prompt: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    val = input(f"{prompt} [{d}]: ").strip().lower()
    if not val:
        return default
    return val in {"y", "yes"}


def run_init(target_path: str) -> None:
    root = Path(target_path).expanduser().resolve()

    if not root.exists():
        create = _ask_yes_no(
            f"Directory {root} does not exist. Create it?", default=True
        )
        if not create:
            print("Aborted.")
            return
        root.mkdir(parents=True, exist_ok=True)

    # Gather details interactively
    default_name = root.name
    name = _ask("Library name", default_name)
    description = _ask("Description", "")

    bib_file = _ask("BibTeX filename", "library.bib")
    history_file = _ask("History filename", "tag_history.json")

    create_vocab = _ask_yes_no(
        "Create a library-specific vocab.json now?", default=False
    )
    vocab_file = (
        _ask("Vocabulary filename", "vocab.json") if create_vocab else "vocab.json"
    )

    # Write manifest
    manifest = {
        "name": name,
        "description": description,
        "vocab": vocab_file,
        "history": history_file,
        "bib": bib_file,
    }
    (root / "borax-library.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Create optional/required files in the library root
    bib_path = root / bib_file
    if not bib_path.exists():
        bib_path.write_text("", encoding="utf-8")

    history_path = root / history_file
    if not history_path.exists():
        history_path.write_text("{}\n", encoding="utf-8")

    if create_vocab:
        vocab_path = root / vocab_file
        if not vocab_path.exists():
            vocab_template = {
                "Document_Types": [],
                "Levels": [],
                "Disciplines": {},
                "Keywords": {},
            }
            vocab_path.write_text(
                json.dumps(vocab_template, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    print("\n✅ Library initialized:")
    print(f"  Root:        {root}")
    print(f"  Manifest:    {(root / 'borax-library.json')}")
    print(f"  BibTeX:      {bib_path}")
    print(f"  History:     {history_path}")
    if create_vocab:
        print(f"  Vocabulary:  {(root / vocab_file)}")
    else:
        print("  Vocabulary:  (using project default; you can add one later)")
