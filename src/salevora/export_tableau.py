"""Export summary tables for the Tableau Public dashboard.

    python -m salevora.export_tableau

Runs every query in sql/exports/ and writes one CSV per query to
dashboards/tableau/data/. These are summaries (store x month, chain x day),
not the raw daily rows, so the public dashboard doesn't republish the
Kaggle dataset. The CSVs aren't committed: rerun this to recreate them.
"""
from pathlib import Path

from salevora.config import ROOT
from salevora.run_query import run_query

EXPORTS = ROOT / "sql" / "exports"
OUTPUT = ROOT / "dashboards" / "tableau" / "data"


def export_all(output: Path = OUTPUT) -> dict[str, int]:
    """Write one CSV per export query; return the row count of each."""
    output.mkdir(parents=True, exist_ok=True)
    rows = {}
    for sql_file in sorted(EXPORTS.glob("*.sql")):
        df = run_query(sql_file)
        df.to_csv(output / f"{sql_file.stem}.csv", index=False)
        rows[sql_file.stem] = len(df)
    return rows


if __name__ == "__main__":
    for name, count in export_all().items():
        print(f"{name}.csv: {count:,} rows")
