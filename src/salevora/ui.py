"""Small Streamlit helpers shared by the app's pages."""
import streamlit as st

from salevora import queries

DAY_NAMES = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

# Cached copies of the queries: each runs once, then Streamlit reuses the result.
stores = st.cache_data(queries.stores)
overview = st.cache_data(queries.overview)
monthly_sales = st.cache_data(queries.monthly_sales)
weekday_promo = st.cache_data(queries.weekday_promo)
store_types = st.cache_data(queries.store_types)
daily_history = st.cache_data(queries.daily_history)
model_scores = st.cache_data(queries.model_scores)
forecast_models = st.cache_data(queries.forecast_models)
forecast = st.cache_data(queries.forecast)
error_range = st.cache_data(queries.error_range)
holdout_series = st.cache_data(queries.holdout_series)
shap_global = st.cache_data(queries.shap_global)
shap_store = st.cache_data(queries.shap_store)


def store_picker(forecast_only: bool = False, allow_all: bool = True) -> int:
    """A store selector in the sidebar. Returns 0 for "All stores"."""
    table = stores()
    if forecast_only:
        table = table[table.has_forecast == 1]
    options = ([0] if allow_all else []) + table.store_id.tolist()
    return st.sidebar.selectbox(
        "Store", options, format_func=lambda s: "All stores" if s == 0 else f"Store {s}")
