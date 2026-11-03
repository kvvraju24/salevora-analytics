"""Phase 3 checks: the Tableau exports add up to the same totals as MySQL."""
import pandas as pd
import pytest
from sqlalchemy import text

from salevora.db import get_engine, has_db_settings
from salevora.export_tableau import export_all

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")


@pytest.fixture(scope="module")
def exports(tmp_path_factory):
    """Run the export once into a temporary folder and read the CSVs back."""
    folder = tmp_path_factory.mktemp("tableau")
    rows = export_all(folder)
    return rows, {name: pd.read_csv(folder / f"{name}.csv") for name in rows}


def test_row_counts(exports):
    rows, _ = exports
    # 1,115 stores x 31 months, minus 180 stores x 6 months of the 2014 gap.
    assert rows == {"daily_chain": 942, "store_months": 33_485, "stores": 1_115}


def test_sales_and_open_days_match_mysql(exports):
    _, csv = exports
    with get_engine().connect() as conn:
        sales, open_days = conn.execute(text("SELECT SUM(sales), SUM(is_open) FROM sales_history")).one()
    for table in ("store_months", "daily_chain"):
        assert csv[table].sales.sum() == int(sales)
    assert csv["store_months"].open_days.sum() == int(open_days)
    assert csv["daily_chain"].open_stores.sum() == int(open_days)


def test_every_month_row_belongs_to_a_known_store(exports):
    _, csv = exports
    assert set(csv["store_months"].store_id) <= set(csv["stores"].store_id)
