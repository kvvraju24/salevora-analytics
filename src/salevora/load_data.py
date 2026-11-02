"""Load the three Rossmann CSV files into MySQL.

Run it from the project folder:

    python -m salevora.load_data

It recreates the tables from sql/schema.sql first, so running it again
gives the same result instead of duplicate rows.
"""
import pandas as pd
from sqlalchemy.engine import Engine

from salevora.config import DATA_RAW, ROOT
from salevora.db import get_engine

SCHEMA = ROOT / "sql" / "schema.sql"

# CSV column -> MySQL column. snake_case names are easier to type in SQL.
STORE_COLUMNS = {
    "Store": "store_id",
    "StoreType": "store_type",
    "Assortment": "assortment",
    "CompetitionDistance": "competition_distance",
    "CompetitionOpenSinceMonth": "competition_open_since_month",
    "CompetitionOpenSinceYear": "competition_open_since_year",
    "Promo2": "promo2",
    "Promo2SinceWeek": "promo2_since_week",
    "Promo2SinceYear": "promo2_since_year",
    "PromoInterval": "promo_interval",
}
DAILY_COLUMNS = {  # shared by train.csv and test.csv
    "Store": "store_id",
    "DayOfWeek": "day_of_week",
    "Open": "is_open",
    "Promo": "promo",
    "StateHoliday": "state_holiday",
    "SchoolHoliday": "school_holiday",
}
HISTORY_COLUMNS = {**DAILY_COLUMNS, "Date": "sale_date", "Sales": "sales", "Customers": "customers"}
SCHEDULE_COLUMNS = {**DAILY_COLUMNS, "Id": "kaggle_id", "Date": "forecast_date"}


def read_csv(name: str, columns: dict, date_column: str | None = None) -> pd.DataFrame:
    """Read one raw CSV and rename its columns to the MySQL names."""
    # StateHoliday holds letters (a, b, c) and 0, so read it as text.
    df = pd.read_csv(DATA_RAW / name, dtype={"StateHoliday": str})
    df = df.rename(columns=columns)[list(columns.values())]
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column]).dt.date
    return df


def recreate_tables(engine: Engine) -> None:
    """Run sql/schema.sql: drop the tables if they exist, then create them."""
    statements = [s.strip() for s in SCHEMA.read_text().split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.exec_driver_sql(statement)


def main() -> None:
    engine = get_engine()
    recreate_tables(engine)

    stores = read_csv("store.csv", STORE_COLUMNS)
    history = read_csv("train.csv", HISTORY_COLUMNS, date_column="sale_date")
    schedule = read_csv("test.csv", SCHEDULE_COLUMNS, date_column="forecast_date")

    # Inserting in primary-key order is much faster for MySQL.
    history = history.sort_values(["store_id", "sale_date"])
    schedule = schedule.sort_values(["store_id", "forecast_date"])

    # stores goes first: the other two tables point to it with a foreign key.
    for table, df in [("stores", stores), ("sales_history", history), ("forecast_schedule", schedule)]:
        df.to_sql(table, engine, if_exists="append", index=False, chunksize=10_000)
        print(f"{table}: {len(df):,} rows loaded")


if __name__ == "__main__":
    main()
