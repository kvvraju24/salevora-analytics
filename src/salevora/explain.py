"""Phase 5: explain the forecasts with SHAP values.

A SHAP value says how much one feature pushed one prediction up or down,
compared with the model's average prediction (the base value). XGBoost and
LightGBM compute exact SHAP values for their own trees ("Tree SHAP"), so no
extra package is needed.

The values are in log-sales units, because the models learn log(1 + sales):
base value + all SHAP values = log(1 + predicted sales).
"""
import numpy as np
import pandas as pd
import xgboost as xgb

from salevora.features import FEATURE_LABELS


def shap_values(model, X: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """SHAP value of every feature for every row, plus each row's base value."""
    trees = model.regressor_  # the fitted XGBoost or LightGBM inside log_target()
    if isinstance(trees, xgb.XGBRegressor):
        raw = trees.get_booster().predict(xgb.DMatrix(X), pred_contribs=True)
    else:
        raw = trees.predict(X, pred_contrib=True)
    return pd.DataFrame(raw[:, :-1], index=X.index, columns=X.columns), raw[:, -1]


def explain(model, model_name: str, schedule: pd.DataFrame, X_future: pd.DataFrame,
            is_open: np.ndarray, sample: int = 2_000) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Overall feature importance and one explained forecast per store."""
    # Overall: average size of each feature's push, on a sample of open future days.
    open_X = X_future[is_open]
    contrib, _ = shap_values(model, open_X.sample(min(sample, len(open_X)), random_state=42))
    overall = (contrib.abs().mean()
               .rename("mean_abs_shap").rename_axis("feature").reset_index()
               .assign(label=lambda d: d.feature.map(FEATURE_LABELS), model=model_name)
               .sort_values("mean_abs_shap", ascending=False))

    # Per store: its first open day in the schedule.
    first = schedule[is_open].sort_values(["store_id", "date"]).groupby("store_id").head(1)
    X_first = X_future.loc[first.index]
    contrib, base = shap_values(model, X_first)
    # One row per store per feature. (A plain melt would clash with the
    # feature that is itself called store_id.)
    n = X_first.shape[1]
    per_store = pd.DataFrame({
        "store_id": np.repeat(first.store_id.to_numpy(), n),
        "forecast_date": np.repeat(first.date.to_numpy(), n),
        "feature": np.tile(X_first.columns.to_numpy(), len(first)),
        "feature_value": X_first.to_numpy().ravel(),
        "shap_value": contrib.to_numpy().ravel(),
        "base_value": np.repeat(base, n),
    })
    per_store["label"] = per_store.feature.map(FEATURE_LABELS)
    return overall, per_store
