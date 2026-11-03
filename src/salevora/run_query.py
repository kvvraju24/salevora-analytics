"""Run a .sql file against the project database and print the result.

    python -m salevora.run_query sql/queries/01_yearly_sales.sql
"""
import sys
from pathlib import Path

import pandas as pd

from salevora.db import get_engine


def run_query(path: str | Path) -> pd.DataFrame:
    """Return the result of the single SELECT in a .sql file as a DataFrame."""
    sql = Path(path).read_text().strip().rstrip(";")
    with get_engine().connect() as conn:
        # exec_driver_sql sends the SQL exactly as written (no parameter parsing).
        result = conn.exec_driver_sql(sql)
        return pd.DataFrame(result.fetchall(), columns=list(result.keys()))


if __name__ == "__main__":
    print(run_query(sys.argv[1]).to_string(index=False))
