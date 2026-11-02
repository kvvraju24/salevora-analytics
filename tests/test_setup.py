"""Phase 0 checks: the raw data is complete and MySQL is reachable."""
import csv

import pytest
from sqlalchemy import text

from salevora.config import DATA_RAW, DB_NAME
from salevora.db import get_engine, has_db_settings

# Column names and row counts of the original Kaggle files.
EXPECTED = {
    "train.csv": (
        ["Store", "DayOfWeek", "Date", "Sales", "Customers", "Open", "Promo",
         "StateHoliday", "SchoolHoliday"],
        1_017_209,
    ),
    "test.csv": (
        ["Id", "Store", "DayOfWeek", "Date", "Open", "Promo", "StateHoliday",
         "SchoolHoliday"],
        41_088,
    ),
    "store.csv": (
        ["Store", "StoreType", "Assortment", "CompetitionDistance",
         "CompetitionOpenSinceMonth", "CompetitionOpenSinceYear", "Promo2",
         "Promo2SinceWeek", "Promo2SinceYear", "PromoInterval"],
        1_115,
    ),
}


@pytest.mark.parametrize("name", list(EXPECTED))
def test_raw_csv_is_complete(name):
    path = DATA_RAW / name
    if not path.exists():
        pytest.skip(f"{name} is not downloaded yet (see data/README.md)")
    columns, rows = EXPECTED[name]
    with path.open(newline="") as f:
        reader = csv.reader(f)
        assert next(reader) == columns
        assert sum(1 for _ in reader) == rows


@pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")
def test_mysql_connection():
    with get_engine().connect() as conn:
        assert conn.execute(text("SELECT DATABASE()")).scalar() == DB_NAME
