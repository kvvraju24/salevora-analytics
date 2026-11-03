"""Phase 4 unit tests on tiny made-up data.

No database or Kaggle files needed, so these also run on GitHub (CI).
"""
import numpy as np
import pandas as pd
import pytest

from salevora.evaluate import metrics, split_by_date
from salevora.features import FEATURES, build_features, fit_store_history
from salevora.models import BaselineModel

STORES = pd.DataFrame({
    "store_id": [1], "store_type": ["a"], "assortment": ["c"],
    "competition_distance": [np.nan],  # unknown distance
    "competition_open_since_month": [6.0], "competition_open_since_year": [2015.0],
    "promo2": [1], "promo2_since_week": [10.0], "promo2_since_year": [2015.0],
    "promo_interval": ["Jan,Apr,Jul,Oct"],
})


def make_days(start: str, days: int, sales: float, promo: int = 0) -> pd.DataFrame:
    """Daily rows for store 1 with the same sales every day."""
    dates = pd.date_range(start, periods=days)
    return pd.DataFrame({
        "store_id": 1, "date": dates, "day_of_week": dates.day_of_week + 1, "sales": sales,
        "is_open": 1, "promo": promo, "state_holiday": "0", "school_holiday": 0,
    })


def test_split_holds_out_the_last_48_days():
    history = make_days("2015-01-01", 100, 100)
    train, holdout = split_by_date(history)
    assert holdout.date.nunique() == 48
    assert train.date.max() < holdout.date.min()


def test_store_averages_ignore_the_holdout_days():
    # Training days sell 100, held-out days 1,000. Features must only "know" 100.
    history = pd.concat([make_days("2015-01-01", 52, 100), make_days("2015-02-22", 48, 1_000)],
                        ignore_index=True)
    train, holdout = split_by_date(history)
    features = build_features(holdout, STORES, fit_store_history(train))
    assert (features[["store_avg", "store_weekday_avg", "store_weekday_promo_avg"]] == 100).all().all()


def test_features_never_include_customers():
    features = build_features(make_days("2015-01-01", 10, 100), STORES,
                              fit_store_history(make_days("2014-01-01", 30, 100)))
    assert list(features.columns) == FEATURES
    assert "customers" not in features.columns


def test_competition_features():
    days = make_days("2015-05-01", 92, 100)  # May to July 2015; competitor opened June 2015
    features = build_features(days, STORES, fit_store_history(days))
    assert (features.competition_distance == 100_000).all()  # unknown -> far away
    months = features.competition_months.groupby(days.date.dt.month).first()
    assert months.to_dict() == {5: 0, 6: 0, 7: 1}


def test_promo2_runs_only_in_its_months_after_it_starts():
    # Promo2 starts in week 10 of 2015 and runs in Jan, Apr, Jul, Oct.
    days = make_days("2015-01-05", 200, 100)
    features = build_features(days, STORES, fit_store_history(days))
    active = features.promo2_active.groupby(days.date.dt.month).max()
    assert active.to_dict() == {1: 0, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1}


def test_baseline_predicts_the_weekday_and_promo_average():
    train = pd.concat([make_days("2015-01-01", 14, 100, promo=0), make_days("2015-01-15", 14, 300, promo=1)],
                      ignore_index=True)
    future = make_days("2015-02-01", 7, 0, promo=1)
    features = build_features(future, STORES, fit_store_history(train))
    assert (BaselineModel().fit(features, None).predict(features) == 300).all()


def test_metrics_on_known_numbers():
    result = metrics([100, 200], [110, 180])
    assert result["mae"] == 15
    assert result["rmse"] == pytest.approx(np.sqrt(250))
    assert result["wape"] == pytest.approx(0.1)
    assert result["rmspe"] == pytest.approx(0.1)


def test_rmspe_skips_days_with_zero_sales():
    assert metrics([0, 100], [50, 110])["rmspe"] == pytest.approx(0.1)
