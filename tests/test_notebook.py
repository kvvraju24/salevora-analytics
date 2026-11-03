"""Phase 2 check: the exploration notebook runs from top to bottom without errors."""
import nbformat
import pytest
from nbclient import NotebookClient

from salevora.config import ROOT
from salevora.db import has_db_settings


@pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")
def test_explore_notebook_runs():
    notebook = nbformat.read(ROOT / "notebooks" / "01_explore.ipynb", as_version=4)
    # Runs every cell in memory (the file isn't changed); any cell error fails the test.
    NotebookClient(notebook, timeout=300, kernel_name="python3").execute()
