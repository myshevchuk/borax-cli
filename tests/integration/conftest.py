import shutil
import subprocess
from pathlib import Path
import sys
import pytest

# Ensure project root is importable for `import borax`
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_library(tmp_path):
    """Copy the integration test library into a temp directory and return its path."""
    fixture_root = PROJECT_ROOT / "tests/data/integration/library"
    lib = tmp_path / "library"
    shutil.copytree(fixture_root, lib)
    return lib


@pytest.fixture
def run_cli():
    """Run the CLI via the project-local main.py to avoid requiring installation.

    This avoids relying on the borax-cli console script being on PATH.
    """
    cli_entry = PROJECT_ROOT / "main.py"

    def _run(*args, cwd=None):
        result = subprocess.run(
            [sys.executable, str(cli_entry), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd or PROJECT_ROOT,
        )
        return result.stdout, result.stderr, result.returncode

    return _run
