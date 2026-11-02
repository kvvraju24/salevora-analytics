"""Phase 1 checks: the MySQL tables match the raw CSV files.

Load the data first with `python -m salevora.load_data`.
"""
import pandas as pd
import pytest
from sqlalchemy import text

from salevora.config import DATA_RAW
from salevora.db import get_engine, has_db_settings

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")


@pytest.fixture(scope="module")
def db():
    """One MySQL connection shared by every test in this file."""
    with get_engine().connect() as conn:
        yield conn


def value(db, sql):
    """Run a query that returns a single value."""
    return db.execute(text(sql)).scalar()


@pytest.mark.parametrize("table, rows", [
    ("stores", 1_115),
    ("sales_history", 1_017_209),
    ("forecast_schedule", 41_088),
])
def test_row_counts_match_csv(db, table, rows):
    assert value(db, f"SELECT COUNT(*) FROM {table}") == rows


def test_total_sales_match_csv(db):
    csv_total = pd.read_csv(DATA_RAW / "train.csv", usecols=["Sales"])["Sales"].sum()
    assert int(value(db, "SELECT SUM(sales) FROM sales_history")) == int(csv_total)


def test_day_of_week_counts_monday_as_one(db):
    # MySQL's WEEKDAY() counts Monday as 0, Rossmann counts it as 1.
    mismatches = value(db, "SELECT COUNT(*) FROM sales_history WHERE day_of_week <> WEEKDAY(sale_date) + 1")
    assert mismatches == 0


def test_promo2_dates_are_blank_only_for_stores_without_promo2(db):
    mismatches = value(db, "SELECT COUNT(*) FROM stores WHERE (promo2_since_week IS NULL) <> (promo2 = 0)")
    assert mismatches == 0


def test_only_store_622_has_unknown_open_days(db):
    stores = value(db, "SELECT GROUP_CONCAT(DISTINCT store_id) FROM forecast_schedule WHERE is_open IS NULL")
    assert stores == "622"
