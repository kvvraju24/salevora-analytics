"""The five models we compare. All share one interface: fit(X, sales) and predict(X)."""
import numpy as np
from lightgbm import LGBMRegressor
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from salevora.features import FEATURES

# Codes that are labels, not amounts: Ridge gets one 0/1 column per value.
CATEGORICAL = ["store_id", "day_of_week", "state_holiday", "store_type", "assortment", "month"]


class BaselineModel:
    """The simple guess every model must beat: the store's average sales for that
    weekday and promo status, from training days only.

    That average is already a feature (store_weekday_promo_avg), so there is
    nothing to fit.
    """

    def fit(self, X, y):
        return self

    def predict(self, X):
        return X["store_weekday_promo_avg"].to_numpy()


def log_target(model):
    """Train on log(1 + sales), then turn predictions back into sales.

    Sales are right-skewed (Phase 2); on the log scale the biggest days
    don't dominate the training.
    """
    return TransformedTargetRegressor(regressor=model, func=np.log1p, inverse_func=np.expm1)


def make_models() -> dict:
    """Fresh, untrained copies of the five models."""
    numeric = [c for c in FEATURES if c not in CATEGORICAL]
    ridge = make_pipeline(
        ColumnTransformer([("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
                           ("numbers", StandardScaler(), numeric)]),
        Ridge(alpha=10, solver="lsqr"),
    )
    return {
        "Baseline": BaselineModel(),
        "Ridge": log_target(ridge),
        # Each tree sees 200,000 rows, so the forest trains in about a minute on a laptop.
        "Random Forest": log_target(RandomForestRegressor(
            n_estimators=60, max_samples=200_000, min_samples_leaf=5, max_features=0.6,
            n_jobs=-1, random_state=42)),
        "XGBoost": log_target(XGBRegressor(
            n_estimators=800, max_depth=9, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, tree_method="hist", n_jobs=-1, random_state=42)),
        "LightGBM": log_target(LGBMRegressor(
            n_estimators=800, num_leaves=127, learning_rate=0.05, subsample=0.8,
            subsample_freq=1, colsample_bytree=0.8, n_jobs=-1, random_state=42, verbose=-1)),
    }
