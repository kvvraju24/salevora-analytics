"""The time-based test split and the four error metrics."""
import numpy as np
import pandas as pd

# Same length as the forecast schedule (test.csv covers 48 days).
HOLDOUT_DAYS = 48


def split_by_date(history: pd.DataFrame, days: int = HOLDOUT_DAYS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Hold out the last `days` days for testing; train on everything before them.

    Never split at random: the model must be tested on days that come after
    everything it learned from, exactly like a real forecast.
    """
    cutoff = history.date.max() - pd.Timedelta(days=days)
    return history[history.date <= cutoff], history[history.date > cutoff]


def metrics(actual, predicted) -> dict:
    """Four ways to measure forecast error (lower is better).

    mae   - average absolute error, in sales units
    rmse  - like MAE but punishes big misses more
    wape  - total absolute error / total sales: big stores count more (headline metric)
    rmspe - average percentage error (Kaggle's metric); days with 0 sales are skipped
    """
    y = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    error = p - y
    nonzero = y > 0
    return {
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error ** 2))),
        "wape": float(np.abs(error).sum() / y.sum()),
        "rmspe": float(np.sqrt(np.mean((error[nonzero] / y[nonzero]) ** 2))),
    }
