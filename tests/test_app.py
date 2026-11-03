"""Phase 6 checks: every Streamlit page runs without errors, for all stores and for one store."""
import pytest
from streamlit.testing.v1 import AppTest

from salevora.config import ROOT
from salevora.db import has_db_settings

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")

PAGES = [ROOT / "app" / "Home.py", *sorted((ROOT / "app" / "pages").glob("*.py"))]


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
def test_page_runs(page):
    app = AppTest.from_file(str(page), default_timeout=60).run()
    assert not app.exception


@pytest.mark.parametrize("page", [p for p in PAGES if p.name != "Home.py"], ids=lambda p: p.stem)
def test_page_runs_for_one_store(page):
    app = AppTest.from_file(str(page), default_timeout=60).run()
    app.sidebar.selectbox[0].set_value(1).run()  # store 1 has history and a forecast
    assert not app.exception
