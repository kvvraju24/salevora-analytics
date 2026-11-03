"""Phase 7: a read-only REST API over the same data as the Streamlit app.

    uvicorn api.main:app --reload
    then open http://127.0.0.1:8000/docs for interactive documentation.

FastAPI checks every input against its type and limits (for example days
must be 7-365) and returns 422 when one is wrong. Unknown stores return 404.
"""
from functools import lru_cache
from typing import Annotated

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from salevora import queries

app = FastAPI(title="Salevora Analytics API", version="1.0.0",
              description="Rossmann sales history, 48-day forecasts, model scores and SHAP explanations. "
                          "store_id = 0 means all stores.")

StoreId = Annotated[int, Query(ge=0, description="Store number, or 0 for all stores")]


def records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> list of JSON objects (blank values become null)."""
    return df.astype(object).where(df.notna(), None).to_dict(orient="records")


@lru_cache(maxsize=1)
def store_ids() -> tuple[set[int], set[int]]:
    """All store numbers, and the ones with a forecast."""
    table = queries.stores()
    return set(table.store_id), set(table.store_id[table.has_forecast == 1])


def check_store(store_id: int, needs_forecast: bool = False) -> None:
    every, with_forecast = store_ids()
    if store_id and store_id not in every:
        raise HTTPException(404, f"Store {store_id} doesn't exist")
    if store_id and needs_forecast and store_id not in with_forecast:
        raise HTTPException(404, f"Store {store_id} has history but isn't in the forecast schedule")


@app.get("/health")
def health():
    return {"status": "ok", "best_model": queries.best_model()}


@app.get("/stores")
def stores():
    return records(queries.stores())


@app.get("/history")
def history(store_id: StoreId = 0, days: Annotated[int, Query(ge=7, le=365)] = 56):
    """Daily sales for the last `days` days of history."""
    check_store(store_id)
    return records(queries.daily_history(store_id, days))


@app.get("/monthly")
def monthly(store_id: StoreId = 0):
    """Sales and sales per open day for every month."""
    check_store(store_id)
    return records(queries.monthly_sales(store_id))


@app.get("/forecast")
def forecast(store_id: StoreId = 0, model: str | None = None):
    """The 48-day forecast. Leave model empty for the best model."""
    check_store(store_id, needs_forecast=True)
    available = queries.forecast_models()
    model = model or available[0]
    if model not in available:
        raise HTTPException(422, f"model must be one of {available}")
    result = {"store_id": store_id, "model": model, "days": records(queries.forecast(store_id, model))}
    if store_id:
        result["typical_error"] = queries.error_range(store_id, model)
    return result


@app.get("/models")
def models():
    """Scores of the five models on the 48 held-out days (lower is better)."""
    return records(queries.model_scores())


@app.get("/explain")
def explain_overall():
    """Average size of each input's SHAP value."""
    return records(queries.shap_global())


@app.get("/explain/{store_id}")
def explain_store(store_id: int):
    """SHAP values for the store's first open forecast day."""
    check_store(store_id, needs_forecast=True)
    if store_id == 0:
        raise HTTPException(422, "Pick one store: explanations are per store")
    return records(queries.shap_store(store_id))
