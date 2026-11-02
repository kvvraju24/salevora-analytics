# Salevora Analytics

Sales analysis and forecasting for 1,115 Rossmann drugstores, built step by step with Python, SQL and Tableau.

**Business question:** how much will each store sell in the next 48 days, and what drives its sales?

## Status

| Phase | What | Status |
|---|---|---|
| 0 | Project setup: repo, Python environment, MySQL | ✅ Done |
| 1 | Load the data into MySQL; answer business questions in SQL | Next |
| 2 | Exploration notebook | |
| 3 | Tableau Public dashboard | |
| 4 | Forecasting models and tests | |
| 5 | SHAP explanations | |
| 6 | Streamlit app | |
| 7 | FastAPI, Docker, hosting | |

The full plan and the rules the project follows are in [docs/PLAN.md](docs/PLAN.md).

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
5. Check that everything works:
   ```bash
   pytest
   ```

## Project structure (so far)

```text
salevora-analytics/
├── data/
│   ├── README.md        how to get the Kaggle data
│   └── raw/             train.csv, test.csv, store.csv (not committed)
├── docs/PLAN.md         the full plan and project rules
├── src/salevora/        the project's Python code
│   ├── config.py        paths and database settings
│   └── db.py            connects to MySQL
├── tests/
│   └── test_setup.py    checks the data and the database connection
├── .env.example         template for the database settings
├── pyproject.toml       makes src/salevora importable; pytest settings
└── requirements.txt     pinned Python packages
```

## Data

[Rossmann Store Sales](https://www.kaggle.com/c/rossmann-store-sales) (Kaggle), used for learning and non-commercial demonstration. The data is not included in this repo.
