"""Phase 4-5 checks on the saved results. Run `python -m salevora.forecast` first."""
import numpy as np
import pandas as pd
import pytest

from salevora.db import get_engine, has_db_settings

pytestmark = pytest.mark.skipif(not has_db_settings(), reason="no database password in .env")


@pytest.fixture(scope="module")
def engine():
    return get_engine()


@pytest.fixture(scope="module")
def scores(engine):
    return pd.read_sql("SELECT * FROM model_metrics", engine).set_index("model")


def test_five_models_and_one_best(scores):
    assert set(scores.index) == {"Baseline", "Ridge", "Random Forest", "XGBoost", "LightGBM"}
    assert scores.is_best.sum() == 1


def test_best_model_beats_the_baseline(scores):
    best = scores[scores.is_best == 1].iloc[0]
    assert best.wape < scores.loc["Baseline", "wape"]
    assert best.rmspe < scores.loc["Baseline", "rmspe"]


def test_holdout_is_the_last_48_days(scores):
    assert str(scores.holdout_start.iloc[0]) == "2015-06-14"
    assert str(scores.holdout_end.iloc[0]) == "2015-07-31"


def test_every_scheduled_day_has_a_forecast_and_closed_days_are_zero(engine, scores):
    best = scores[scores.is_best == 1].index[0]
    result = pd.read_sql(
        "SELECT f.predicted_sales, s.is_open FROM forecasts AS f "
        "JOIN forecast_schedule AS s ON s.store_id = f.store_id AND s.forecast_date = f.forecast_date "
        f"WHERE f.model = '{best}'", engine)
    assert len(result) == 41_088
    assert (result.loc[result.is_open == 0, "predicted_sales"] == 0).all()
    assert (result.predicted_sales >= 0).all()


def test_shap_values_add_up_to_the_forecast(engine):
    model = pd.read_sql("SELECT DISTINCT model FROM shap_global", engine).model.item()
    check = pd.read_sql(
        "SELECT s.store_id, MIN(s.base_value) + SUM(s.shap_value) AS log_prediction, "
        "MIN(f.predicted_sales) AS predicted_sales "
        "FROM shap_store AS s JOIN forecasts AS f "
        "ON f.store_id = s.store_id AND f.forecast_date = s.forecast_date "
        f"WHERE f.model = '{model}' GROUP BY s.store_id", engine)
    assert len(check) == 856
    assert np.allclose(check.log_prediction, np.log1p(check.predicted_sales), atol=1e-3)
