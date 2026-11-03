"""Read-only queries shared by the Streamlit app and the FastAPI service.

Every function returns a DataFrame (or a number). store_id = 0 means "all stores".
Values go in as query parameters (:name), never pasted into the SQL text,
so user input can't change the query (no SQL injection).
"""
from decimal import Decimal
from functools import lru_cache

import numpy as np
import pandas as pd
from sqlalchemy import text

from salevora.db import get_engine

STORE_FILTER = "(:store_id = 0 OR store_id = :store_id)"


@lru_cache(maxsize=1)
def _engine():
    return get_engine()


def _read(sql: str, **params) -> pd.DataFrame:
    """Run a query; turn MySQL DECIMAL results into ordinary floats."""
    with _engine().connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    for column in df.columns:
        if len(df) and isinstance(df[column].iloc[0], Decimal):
            df[column] = df[column].astype(float)
    return df


# ---------- history ----------

def stores() -> pd.DataFrame:
    return _read("""
        SELECT s.store_id, s.store_type, s.assortment, s.competition_distance,
               EXISTS (SELECT 1 FROM forecast_schedule AS f WHERE f.store_id = s.store_id) AS has_forecast
        FROM stores AS s
        ORDER BY s.store_id""")


def overview() -> pd.DataFrame:
    return _read("""
        SELECT MIN(sale_date) AS first_day, MAX(sale_date) AS last_day,
               COUNT(DISTINCT store_id) AS stores, SUM(sales) AS total_sales,
               SUM(sales) / SUM(is_open) AS sales_per_open_day
        FROM sales_history""")


def monthly_sales(store_id: int = 0) -> pd.DataFrame:
    return _read(f"""
        SELECT DATE_SUB(sale_date, INTERVAL DAYOFMONTH(sale_date) - 1 DAY) AS month,
               SUM(sales) AS sales, SUM(sales) / SUM(is_open) AS sales_per_open_day
        FROM sales_history
        WHERE {STORE_FILTER}
        GROUP BY month
        ORDER BY month""", store_id=store_id)


def weekday_promo(store_id: int = 0) -> pd.DataFrame:
    return _read(f"""
        SELECT day_of_week, promo, AVG(sales) AS avg_sales, COUNT(*) AS open_days
        FROM sales_history
        WHERE is_open = 1 AND {STORE_FILTER}
        GROUP BY day_of_week, promo
        ORDER BY day_of_week, promo""", store_id=store_id)


def store_types() -> pd.DataFrame:
    return _read("""
        SELECT s.store_type, COUNT(DISTINCT s.store_id) AS stores,
               SUM(h.sales) / SUM(h.is_open) AS sales_per_open_day,
               SUM(h.sales) / SUM(h.customers) AS sales_per_customer
        FROM sales_history AS h
        JOIN stores AS s ON s.store_id = h.store_id
        GROUP BY s.store_type
        ORDER BY s.store_type""")


def daily_history(store_id: int = 0, days: int = 56, forecast_stores_only: bool = False) -> pd.DataFrame:
    """Daily sales for the last `days` days of history.

    forecast_stores_only keeps the 856 stores in the forecast schedule, so a
    chain total can be compared fairly with the chain forecast.
    """
    return _read(f"""
        SELECT sale_date AS date, SUM(sales) AS sales
        FROM sales_history
        WHERE {STORE_FILTER}
          AND (:forecast_only = 0 OR store_id IN (SELECT DISTINCT store_id FROM forecast_schedule))
          AND sale_date > (SELECT MAX(sale_date) FROM sales_history) - INTERVAL :days DAY
        GROUP BY sale_date
        ORDER BY sale_date""", store_id=store_id, days=days, forecast_only=int(forecast_stores_only))


# ---------- models and forecasts ----------

def model_scores() -> pd.DataFrame:
    return _read("SELECT * FROM model_metrics ORDER BY wape")


def best_model() -> str:
    return _read("SELECT model FROM model_metrics WHERE is_best = 1").model.iloc[0]


def forecast_models() -> list[str]:
    """Models that have a saved 48-day forecast (the best one first)."""
    names = _read("SELECT DISTINCT model FROM forecasts").model.tolist()
    best = best_model()
    return [best] + sorted(n for n in names if n != best)


def forecast(store_id: int = 0, model: str | None = None) -> pd.DataFrame:
    return _read(f"""
        SELECT forecast_date AS date, SUM(predicted_sales) AS predicted
        FROM forecasts
        WHERE model = :model AND {STORE_FILTER}
        GROUP BY forecast_date
        ORDER BY forecast_date""", model=model or best_model(), store_id=store_id)


def error_range(store_id: int, model: str | None = None) -> float | None:
    """80% of this store's daily errors on the held-out days were smaller than this.

    Only for single stores: adding up store ranges would overstate how sure
    we are about the whole chain.
    """
    errors = _read("""
        SELECT ABS(predicted - actual) AS error
        FROM holdout_predictions
        WHERE model = :model AND store_id = :store_id""", model=model or best_model(), store_id=store_id)
    return float(np.quantile(errors.error, 0.8)) if len(errors) else None


def holdout_series(store_id: int = 0) -> pd.DataFrame:
    """Actual vs predicted sales per day and model on the 48 held-out days."""
    return _read(f"""
        SELECT sale_date AS date, model, SUM(actual) AS actual, SUM(predicted) AS predicted
        FROM holdout_predictions
        WHERE {STORE_FILTER}
        GROUP BY sale_date, model
        ORDER BY sale_date""", store_id=store_id)


# ---------- explanations ----------

def shap_global() -> pd.DataFrame:
    return _read("SELECT feature, label, mean_abs_shap, model FROM shap_global ORDER BY mean_abs_shap DESC")


def shap_store(store_id: int) -> pd.DataFrame:
    return _read("""
        SELECT forecast_date, feature, label, feature_value, shap_value, base_value
        FROM shap_store
        WHERE store_id = :store_id
        ORDER BY ABS(shap_value) DESC""", store_id=store_id)
