"""Public API re-exports for Borax.

These provide stable imports like `from borax import tagging` while the
internal implementation is organized into subpackages.
"""

from . import tagging  # re-export package
from . import bibtex_exporter  # re-export package
from .core import history_tracker  # re-export core module

__all__ = [
    "tagging",
    "bibtex_exporter",
    "history_tracker",
]
