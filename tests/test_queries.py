"""Phase 1 checks: every business question in sql/queries runs and returns rows."""
import pytest

from salevora.config import ROOT
from salevora.db import has_db_settings
from salevora.run_query import run_query

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")

QUERIES = sorted((ROOT / "sql" / "queries").glob("*.sql"))


def test_there_are_ten_questions():
    assert len(QUERIES) == 10


@pytest.mark.parametrize("path", QUERIES, ids=lambda p: p.stem)
def test_query_returns_rows(path):
    assert not run_query(path).empty


def test_missing_days_query_finds_the_known_gaps():
    result = run_query(ROOT / "sql" / "queries" / "07_missing_days.sql")
    assert dict(zip(result.days_recorded, result.stores)) == {758: 180, 941: 1}
    # The 180 stores have no rows at all in July-December 2014.
    assert result.loc[result.days_recorded == 758, "days_jul_dec_2014"].item() == 0
