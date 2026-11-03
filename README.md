# Salevora Analytics

[![CI](https://github.com/kvvraju24/salevora-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/kvvraju24/salevora-analytics/actions/workflows/ci.yml)

Sales analysis and a 48-day forecast for 1,115 Rossmann drugstores, built step by step with **Python, SQL (MySQL), Tableau, LightGBM/XGBoost, Streamlit and FastAPI**.

**Business question:** how much will each store sell in the next 48 days, and what drives its sales?

## Results

Five models, trained on 1 Jan 2013 – 13 Jun 2015 and tested on the **48 days they never saw** (14 Jun – 31 Jul 2015, 45,884 open store-days):

| Model | WAPE ↓ | RMSPE ↓ | MAE ↓ | RMSE ↓ |
|---|---:|---:|---:|---:|
| **LightGBM** | **8.36%** | 12.19% | **597** | **871** |
| XGBoost | 8.43% | **12.17%** | 603 | 877 |
| Random Forest | 9.74% | 14.26% | 696 | 1,007 |
| Baseline (store × weekday × promo average) | 10.32% | 14.29% | 738 | 1,090 |
| Ridge regression | 11.87% | 16.81% | 848 | 1,352 |

- **LightGBM cuts the error by 19%** compared with a simple but strong baseline, and is used for the forecast.
- **Ridge is worse than the baseline:** a straight-line model can't capture how weekday, promotion and store interact.
- **SHAP explanations** show the store's own weekday-and-promo average drives most of each forecast; the calendar (year, day of month, week) refines it.

## Status

| Phase | What | Status |
|---|---|---|
| 0 | Project setup: repo, Python environment, MySQL | ✅ Done |
| 1 | Load the data into MySQL; answer business questions in SQL | ✅ Done: [findings](docs/findings.md) |
| 2 | Exploration notebook | ✅ Done: [view with charts](https://nbviewer.org/github/kvvraju24/salevora-analytics/blob/main/notebooks/01_explore.ipynb) |
| 3 | Tableau Public dashboard | 🔄 Data ready; build and publish with the [guide](dashboards/tableau/GUIDE.md) |
| 4 | Features, five models, time-based test, forecasts in MySQL | ✅ Done |
| 5 | SHAP explanations | ✅ Done |
| 6 | Streamlit app with 4 pages | ✅ Done (runs locally) |
| 7 | FastAPI, Docker, CI, hosting | ✅ API and CI · ⚠️ Docker files written but not yet tested · ⏳ hosting not set up |

The full plan and the rules the project follows are in [docs/PLAN.md](docs/PLAN.md).

## Key findings from the data

From 10 business questions answered in SQL ([all answers](docs/findings.md)) and the [exploration notebook](https://nbviewer.org/github/kvvraju24/salevora-analytics/blob/main/notebooks/01_explore.ipynb):

- Like for like, sales per open day grew **3.2% a year** (Jan–Jun 2013 → 2014 → 2015).
- Promotions run **Monday–Friday in all stores at once, usually every other week**; promo days sell 22–57% more, most on Mondays.
- **December** is the peak month (about +25% on November in 2013); almost every store closes on public holidays.
- Stores with a competitor **within 500 m sell the most**, probably because both sit in busy centres (correlation, not cause).
- Type b stores draw **many customers with small baskets**; daily sales are right-skewed, so the models learn log sales.
- **180 stores have no data for July–December 2014**, so totals for that period understate real sales.

## How it works

```text
Kaggle CSVs ─► MySQL (load_data.py) ─► 10 SQL questions + exploration notebook
                     │
                     ├─► Tableau exports (export_tableau.py) ─► Tableau Public dashboard
                     │
                     └─► forecast.py: features (training days only) ─► 5 models ─► test on last 48 days
                              └─► refit best model ─► 48-day forecast + SHAP ─► MySQL results tables
                                                                                   │
                                                          Streamlit app ◄──────────┤
                                                          FastAPI (/docs) ◄────────┘
```

**Rules the models follow:** test on the last 48 days, never random days; every model must beat the baseline;
features only use information known in advance (customers is never a feature); store averages come from training days only
(a unit test proves it).

## Run it on your machine

Requires Python 3.11+, MySQL 8.4, and on macOS `brew install libomp` (for XGBoost and LightGBM).

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
5. Load the data, then train, test, forecast and explain (about 20 seconds + 1 minute):
   ```bash
   python -m salevora.load_data
   python -m salevora.forecast
   ```
6. Open the app (http://localhost:8501):
   ```bash
   streamlit run app/Home.py
   ```
7. Or the API, with interactive docs at http://127.0.0.1:8000/docs:
   ```bash
   uvicorn api.main:app --reload
   ```
8. Check everything:
   ```bash
   pytest
   ```

Other commands: `python -m salevora.run_query sql/queries/04_promo_by_weekday.sql` runs a business question;
`python -m salevora.export_tableau` writes the Tableau CSVs.

### With Docker (not yet tested)

`docker compose up --build` should start MySQL, load and train once, then serve the app on port 8501 and the API on 8000.
It needs Docker installed, `data/raw/*.csv`, and `DB_PASSWORD` in `.env`. These files haven't been run yet, because Docker isn't installed on the development machine.

## API

`GET /health` · `/stores` · `/history` · `/monthly` · `/forecast` · `/models` · `/explain` · `/explain/{store_id}`

`store_id=0` means all stores. Bad input returns 422 (for example `days` outside 7–365, an unknown model) and unknown stores return 404.

## Project structure

```text
salevora-analytics/
├── api/main.py            FastAPI service
├── app/                   Streamlit app: Home.py + 4 pages
├── dashboards/tableau/    guide to build the Tableau dashboard (+ data/, not committed)
├── data/                  how to get the Kaggle data (raw/ is not committed)
├── docs/                  PLAN.md (plan and rules), findings.md (SQL answers)
├── notebooks/             01_explore.ipynb: pandas + Plotly exploration
├── sql/
│   ├── schema.sql         raw data tables
│   ├── results_schema.sql model results tables
│   ├── queries/           the 10 business questions
│   └── exports/           summary tables for Tableau
├── src/salevora/
│   ├── config.py, db.py   settings and MySQL connection
│   ├── load_data.py       CSVs → MySQL
│   ├── run_query.py       run a .sql file
│   ├── export_tableau.py  Tableau CSVs
│   ├── features.py        model inputs (known in advance only)
│   ├── models.py          the five models
│   ├── evaluate.py        time-based split and metrics
│   ├── forecast.py        the full train → test → forecast pipeline
│   ├── explain.py         SHAP explanations
│   ├── queries.py         read-only queries for the app and API
│   └── ui.py              Streamlit helpers
├── tests/                 60 tests: data, SQL, notebook, exports, features, models, app, API
├── Dockerfile, docker-compose.yml
└── .github/workflows/ci.yml
```

## Limitations

- This is **historical data** (2013–2015): the forecast covers the 48 days after the history ends, not today.
- The **error range** in the app is each store's typical error on the held-out days, a guide rather than a guaranteed interval.
- **Promotion effects are associations**, not proof of cause: promotions may be scheduled for busier weeks.
- The forecast assumes the 11 days with an unknown opening status (store 622) are open.
- CI runs the unit tests only: GitHub has no copy of the Kaggle data or the MySQL database.

## Data

[Rossmann Store Sales](https://www.kaggle.com/c/rossmann-store-sales) (Kaggle), used for learning and non-commercial demonstration. The data is not included in this repo.
