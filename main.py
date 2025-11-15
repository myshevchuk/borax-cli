#!/usr/bin/env python3
"""Borax (Book Organizer and Research Article arXiver) CLI dispatcher.

This file delegates to `borax.cli.main()` to keep a single source of
truth for CLI behavior across Poetry's console script and direct invocation.
"""

from borax.cli import main as cli_main

def main():
    cli_main()

if __name__ == "__main__":
    main()
