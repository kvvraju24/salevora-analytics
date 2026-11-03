"""Phase 4: train five models, test them on the last 48 days, and forecast.

    python -m salevora.forecast

1. Load the history, stores and forecast schedule from MySQL.
2. Hold out the last 48 days; build features from the earlier days only.
3. Train each model and score it on the held-out open days.
4. Refit the best model on all history and forecast the 48-day schedule.
5. Explain the forecasts with SHAP (Phase 5) and save everything to MySQL.

Takes a few minutes. The results tables are replaced on every run.
"""
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from salevora.config import ROOT
from salevora.db import get_engine, run_sql_file
from salevora.evaluate import metrics, split_by_date
from salevora.explain import explain
from salevora.features import build_features, fit_store_history
from salevora.models import make_models

RESULTS_SCHEMA = ROOT / "sql" / "results_schema.sql"
EXPLAINABLE = ("XGBoost", "LightGBM")  # models with exact Tree SHAP


def load(engine):
    """Read the three tables, with one shared column name for the date: `date`."""
    history = pd.read_sql("SELECT * FROM sales_history ORDER BY store_id, sale_date",
                          engine, parse_dates=["sale_date"]).rename(columns={"sale_date": "date"})
    schedule = pd.read_sql("SELECT * FROM forecast_schedule ORDER BY store_id, forecast_date",
                           engine, parse_dates=["forecast_date"]).rename(columns={"forecast_date": "date"})
    stores = pd.read_sql("SELECT * FROM stores", engine)
    return history, schedule, stores


def sold_days(rows: pd.DataFrame) -> pd.DataFrame:
    """Rows to learn from: open days with sales. (54 open days with 0 sales are left out as anomalies.)"""
    return rows[(rows.is_open == 1) & (rows.sales > 0)]


def evaluate_models(history: pd.DataFrame, stores: pd.DataFrame):
    """Train every model on the earlier days and score it on the last 48 (open days only)."""
    train, holdout = split_by_date(history)
    store_history = fit_store_history(train)  # training days only: no leakage
    fit_rows, test_rows = sold_days(train), holdout[holdout.is_open == 1]
    X_train = build_features(fit_rows, stores, store_history)
    X_test = build_features(test_rows, stores, store_history)
    print(f"Training on {len(fit_rows):,} days up to {train.date.max():%d %b %Y}; "
          f"testing on {len(test_rows):,} open days from {holdout.date.min():%d %b %Y}", flush=True)

    scores, predictions = [], []
    for name, model in make_models().items():
        started = time.time()
        model.fit(X_train, fit_rows.sales)
        predicted = np.clip(model.predict(X_test), 0, None)
        seconds = round(time.time() - started, 1)
        score = {"model": name, **metrics(test_rows.sales, predicted), "seconds": seconds}
        scores.append(score)
        predictions.append(pd.DataFrame({"model": name, "store_id": test_rows.store_id,
                                         "sale_date": test_rows.date.dt.date,
                                         "actual": test_rows.sales, "predicted": predicted}))
        print(f"  {name:<14} WAPE {score['wape']:.2%}  RMSPE {score['rmspe']:.2%}  ({seconds}s)", flush=True)

    scores = pd.DataFrame(scores).assign(
        holdout_start=holdout.date.min().date(), holdout_end=holdout.date.max().date(),
        holdout_rows=len(test_rows))
    return scores, pd.concat(predictions, ignore_index=True)


def forecast_schedule(model_names: list[str], history, schedule, stores):
    """Refit the chosen models on ALL history and predict every scheduled day."""
    store_history = fit_store_history(history)
    fit_rows = sold_days(history)
    X_all = build_features(fit_rows, stores, store_history)
    X_future = build_features(schedule, stores, store_history)
    # 11 rows (store 622) have an unknown opening: treat them as open.
    is_open = schedule.is_open.fillna(1).to_numpy() == 1

    forecasts, fitted = [], {}
    for name in model_names:
        model = make_models()[name].fit(X_all, fit_rows.sales)
        predicted = np.where(is_open, np.clip(model.predict(X_future), 0, None), 0)
        forecasts.append(pd.DataFrame({"model": name, "store_id": schedule.store_id,
                                       "forecast_date": schedule.date.dt.date,
                                       "predicted_sales": predicted}))
        fitted[name] = model
        print(f"  refit {name} on all {len(fit_rows):,} days", flush=True)
    return pd.concat(forecasts, ignore_index=True), fitted, X_future, is_open


def save(engine, tables: dict[str, pd.DataFrame]) -> None:
    """Recreate the results tables and fill them."""
    run_sql_file(engine, RESULTS_SCHEMA)
    for table, df in tables.items():
        df.to_sql(table, engine, if_exists="append", index=False, chunksize=10_000)
        print(f"  saved {table}: {len(df):,} rows", flush=True)


def main() -> None:
    started = time.time()
    engine = get_engine()
    history, schedule, stores = load(engine)

    print("Step 1/3: compare models on the last 48 days", flush=True)
    scores, holdout_predictions = evaluate_models(history, stores)
    ranked = scores.sort_values("wape")
    best = ranked.model.iloc[0]
    # SHAP needs a tree-boosting model; use the best of those if the winner isn't one.
    explained = best if best in EXPLAINABLE else ranked[ranked.model.isin(EXPLAINABLE)].model.iloc[0]
    print(f"Best model: {best}", flush=True)

    print("Step 2/3: forecast the 48-day schedule", flush=True)
    names = list(dict.fromkeys([best, explained, "Baseline"]))
    forecasts, fitted, X_future, is_open = forecast_schedule(names, history, schedule, stores)
    shap_global, shap_store = explain(fitted[explained], explained, schedule, X_future, is_open)

    print("Step 3/3: save results to MySQL", flush=True)
    scores = scores.assign(is_best=scores.model == best,
                           trained_at=datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0))
    save(engine, {"model_metrics": scores, "holdout_predictions": holdout_predictions,
                  "forecasts": forecasts, "shap_global": shap_global, "shap_store": shap_store})
    print(f"Done in {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
