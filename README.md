# Salevora Analytics

Sales analysis and forecasting for 1,115 Rossmann drugstores, built step by step with Python, SQL and Tableau.

**Business question:** how much will each store sell in the next 48 days, and what drives its sales?

## Status

| Phase | What | Status |
|---|---|---|
| 0 | Project setup: repo, Python environment, MySQL | ✅ Done |
| 1 | Load the data into MySQL; answer business questions in SQL | ✅ Done: [findings](docs/findings.md) |
| 2 | Exploration notebook | Next |
| 3 | Tableau Public dashboard | |
| 4 | Forecasting models and tests | |
| 5 | SHAP explanations | |
| 6 | Streamlit app | |
| 7 | FastAPI, Docker, hosting | |

The full plan and the rules the project follows are in [docs/PLAN.md](docs/PLAN.md).

## Key findings so far

From 10 business questions answered in SQL ([all answers](docs/findings.md)):

- Like for like, sales per open day grew **3.2% a year** (Jan–Jun 2013 → 2014 → 2015).
- Promotions run **Monday–Friday in all stores at once, usually every other week**; promo days sell 22–57% more, most on Mondays.
- **December** is the peak month (about +25% on November in 2013); almost every store closes on public holidays.
- Stores with a competitor **within 500 m sell the most**, probably because both sit in busy centres (correlation, not cause).
- **180 stores have no data for July–December 2014**, so totals for that period understate real sales.

## Set up on your machine

Requires Python 3.11+ and MySQL 8.4.

1. Get the data: see [data/README.md](data/README.md).
2. Create the Python environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. In MySQL (as root), create the database and a project user:
   ```sql
   CREATE DATABASE salevora CHARACTER SET utf8mb4;
   CREATE USER 'salevora'@'localhost' IDENTIFIED BY 'choose-a-password';
   GRANT ALL PRIVILEGES ON salevora.* TO 'salevora'@'localhost';
   ```
4. Copy `.env.example` to `.env` and put that password in it.
5. Load the CSVs into MySQL (about a minute; safe to run again):
   ```bash
   python -m salevora.load_data
   ```
6. Check that everything works:
   ```bash
   pytest
   ```
7. Run any business question:
   ```bash
   python -m salevora.run_query sql/queries/04_promo_by_weekday.sql
   ```

## Project structure (so far)

```text
salevora-analytics/
├── data/
│   ├── README.md        how to get the Kaggle data
│   └── raw/             train.csv, test.csv, store.csv (not committed)
├── docs/
│   ├── PLAN.md          the full plan and project rules
│   └── findings.md      answers to the 10 business questions
├── sql/
│   ├── schema.sql       MySQL tables: stores, sales_history, forecast_schedule
│   └── queries/         the 10 business questions, one file each
├── src/salevora/        the project's Python code
│   ├── config.py        paths and database settings
│   ├── db.py            connects to MySQL
│   ├── load_data.py     loads the CSVs into MySQL
│   └── run_query.py     runs a .sql file and prints the result
├── tests/
│   ├── test_setup.py    checks the data and the database connection
│   ├── test_load_data.py  checks the MySQL tables match the CSVs
│   └── test_queries.py  checks every business question runs
├── .env.example         template for the database settings
├── pyproject.toml       makes src/salevora importable; pytest settings
└── requirements.txt     pinned Python packages
```

## Data

[Rossmann Store Sales](https://www.kaggle.com/c/rossmann-store-sales) (Kaggle), used for learning and non-commercial demonstration. The data is not included in this repo.
