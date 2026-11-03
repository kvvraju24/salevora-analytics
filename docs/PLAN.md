# Project plan

Locked on 2 November 2026. Any change goes in the decisions log at the bottom.

## Goal

One project that shows data analyst skills first (SQL, dashboards, insights) and data scientist skills next (forecasting, honest evaluation, explanations).

**Business question:** how much will each Rossmann store sell in the next 48 days, and what drives its sales?

## Data

Rossmann Store Sales from Kaggle (see [../data/README.md](../data/README.md)).

| File | What it is | Rows |
|---|---|---|
| `train.csv` | Daily sales history: 1,115 stores, 2013-01-01 to 2015-07-31 | 1,017,209 |
| `test.csv` | Future schedule with no Sales column: 856 stores, 2015-08-01 to 2015-09-17 (48 days) | 41,088 |
| `store.csv` | Store details: type, assortment, competition, Promo2 | 1,115 |

We forecast the 48 days right after the history ends (Aug–Sep 2015). This is historical data, so the project never claims to predict today's sales.

## Stack

| Layer | Tool | Phase |
|---|---|---|
| Languages | Python, SQL | all |
| Database | MySQL 8.4 | 0 onward |
| Data processing | pandas, NumPy | 1 onward |
| Analysis | Jupyter in VS Code, Plotly | 2 |
| BI dashboard | Tableau Public | 3 |
| Models | Baseline, Ridge, Random Forest, XGBoost, LightGBM | 4 |
| Explanations | SHAP | 5 |
| Frontend | Streamlit | 6 |
| Tests | pytest, then GitHub Actions | 0 onward |
| Backend API | FastAPI | 7 |
| Deployment | Docker, cloud host | 7 |
| Power BI | Same dashboard as Tableau | only with a Windows PC |

## Rules we follow

1. Test models on the **last 48 days** of history, never on random days.
2. Every model must beat a simple **baseline**: the store × weekday × promo average.
3. A feature may only use information that would be **known before the days being predicted**. Lags must be 48 days or more, and Customers is not a feature, because it is unknown for future days.
4. Report MAE, RMSE, WAPE and RMSPE, and write down the limits of the results.
5. Keep code short, commented, tested, and explainable line by line.

## Phases

| Phase | Build | You learn | Done when |
|---|---|---|---|
| 0 | Repo, Python environment, MySQL | Git, virtual environments, MySQL basics | `pytest` passes: data complete, database reachable |
| 1 | Load the CSVs into MySQL; answer 10 business questions in SQL | Joins, GROUP BY, window functions | Row counts match the CSVs; every question has a query and a written answer |
| 2 | Exploration notebook | pandas, Plotly | Charts plus a short findings section |
| 3 | Tableau Public dashboard | BI, storytelling | Published, with the public link in the README |
| 4 | Features, five models, time-based test, forecasts saved to MySQL | scikit-learn, XGBoost, LightGBM | The best model beats the baseline; tests pass |
| 5 | SHAP explanations | Explaining a model | Overall and per-store explanations saved |
| 6 | Streamlit app with 4 pages | Interactive apps | Runs locally with all 4 pages |
| 7 | FastAPI, Docker, hosting, CI | Production basics | Live link; CI passes |

**Streamlit pages:** Sales Analytics · Forecast · Model Comparison · Explainable AI.

## Target folder layout

```text
salevora-analytics/
├── data/raw/              Kaggle CSVs (not committed)
├── sql/
│   ├── schema.sql         stores, sales_history, forecast_schedule (+ forecasts, model_metrics in Phase 4)
│   └── queries/           business questions
├── notebooks/             01_explore.ipynb, 02_models.ipynb
├── src/salevora/
│   ├── config.py          paths and settings
│   ├── db.py              MySQL connection
│   ├── load_data.py       CSV → MySQL
│   ├── features.py        model inputs
│   ├── models.py          baseline, Ridge, Random Forest, XGBoost, LightGBM
│   ├── evaluate.py        time-based test and metrics
│   ├── forecast.py        48-day forecasts → MySQL
│   └── explain.py         SHAP
├── app/                   Streamlit: Home.py + pages/
├── dashboards/tableau/    exported data, screenshots, public link
├── api/                   FastAPI (Phase 7)
├── tests/
└── .github/workflows/     CI
```

## Decisions log

- Kept the Rossmann dataset.
- New repo; the old Salevora repo stays untouched as a reference.
- Python and SQL only: no Java, React or C++.
- MySQL 8.4 LTS, rather than PostgreSQL or the newer MySQL 26.x releases.
- Tableau Public instead of Power BI, because Power BI Desktop doesn't run on macOS.
- Streamlit reads MySQL directly at first; FastAPI comes in Phase 7.
- Push to GitHub after Phase 1.
- Tableau exports are summaries (store × month, chain × day) holding sums, so the public workbook doesn't republish the raw data.
- Phase 4: models are scored on open days only (closed days are always 0). The best model is picked by WAPE (LightGBM in the first run).
- Phase 5: SHAP values come from XGBoost's and LightGBM's built-in Tree SHAP, which is exact and needs no extra package.
- Phase 6–7: Streamlit keeps reading MySQL directly. FastAPI serves the same queries (`queries.py`) to other programs, so both always agree.
- Phase 7: CI runs the unit tests (made-up data). Tests that need MySQL or the Kaggle files skip on GitHub.
