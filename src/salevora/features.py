"""Model inputs (features), built only from information known in advance.

Every feature is known before the day being predicted: the calendar, the
promo and holiday schedule, store details, and sales averages computed from
*training* days only (fit_store_history). Customers is never used: it's
unknown for future days.
"""
import numpy as np
import pandas as pd

HOLIDAYS = {"0": 0, "a": 1, "b": 2, "c": 3}
STORE_TYPES = {"a": 0, "b": 1, "c": 2, "d": 3}
ASSORTMENTS = {"a": 0, "b": 1, "c": 2}
MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dec"}

# Feature name -> label shown in the app.
FEATURE_LABELS = {
    "store_id": "Store",
    "day_of_week": "Day of week",
    "promo": "Promotion",
    "state_holiday": "Public holiday",
    "school_holiday": "School holiday",
    "store_type": "Store type",
    "assortment": "Assortment",
    "competition_distance": "Competitor distance",
    "competition_months": "Months since competitor opened",
    "promo2_active": "Recurring promotion (Promo2) running",
    "year": "Year",
    "month": "Month",
    "day_of_month": "Day of month",
    "week_of_year": "Week of year",
    "store_avg": "Store's average sales",
    "store_weekday_avg": "Store's average for this weekday",
    "store_weekday_promo_avg": "Store's average for this weekday and promo",
}
FEATURES = list(FEATURE_LABELS)


def fit_store_history(train: pd.DataFrame) -> dict:
    """Average sales per store, per store x weekday, and per store x weekday x promo.

    Uses only the rows passed in (the training days), so the days we test on
    never leak into the features. Open days with sales > 0 only.
    """
    sold = train[(train.is_open == 1) & (train.sales > 0)]
    return {
        "overall": sold.sales.mean(),
        "store": sold.groupby("store_id").sales.mean(),
        "store_weekday": sold.groupby(["store_id", "day_of_week"]).sales.mean(),
        "store_weekday_promo": sold.groupby(["store_id", "day_of_week", "promo"]).sales.mean(),
    }


def promo2_active(d: pd.DataFrame) -> np.ndarray:
    """1 when the store's recurring promotion (Promo2) has started and runs that month."""
    iso = d.date.dt.isocalendar()
    year_week = iso.year.astype(int) * 100 + iso.week.astype(int)
    started = year_week >= d.promo2_since_year * 100 + d.promo2_since_week  # False when blank
    month = d.date.dt.month.map(MONTH_NAMES)
    in_interval = np.array([m in str(interval).split(",") for m, interval in zip(month, d.promo_interval)])
    return ((d.promo2 == 1) & started & in_interval).astype(int).to_numpy()


def build_features(rows: pd.DataFrame, stores: pd.DataFrame, history: dict) -> pd.DataFrame:
    """Turn daily rows (history or forecast schedule) into the model's inputs.

    rows needs: store_id, date, day_of_week, promo, state_holiday, school_holiday.
    """
    d = rows.merge(stores, on="store_id", how="left", validate="many_to_one")
    d.index = rows.index
    f = pd.DataFrame(index=rows.index)

    for column in ["store_id", "day_of_week", "promo", "school_holiday"]:
        f[column] = d[column]
    f["state_holiday"] = d.state_holiday.map(HOLIDAYS)
    f["store_type"] = d.store_type.map(STORE_TYPES)
    f["assortment"] = d.assortment.map(ASSORTMENTS)
    # 3 stores have no competitor distance: treat them as far away.
    f["competition_distance"] = d.competition_distance.fillna(100_000)
    months_open = ((d.date.dt.year - d.competition_open_since_year) * 12
                   + d.date.dt.month - d.competition_open_since_month)
    # Before the competitor opened -> 0. Unknown opening date -> -1.
    f["competition_months"] = months_open.clip(lower=0).fillna(-1)
    f["promo2_active"] = promo2_active(d)

    f["year"] = d.date.dt.year
    f["month"] = d.date.dt.month
    f["day_of_month"] = d.date.dt.day
    f["week_of_year"] = d.date.dt.isocalendar().week.astype(int)

    # Training-day averages; a missing group falls back to the wider average.
    f["store_avg"] = d.store_id.map(history["store"]).fillna(history["overall"])
    weekday = history["store_weekday"].reindex(pd.MultiIndex.from_frame(d[["store_id", "day_of_week"]]))
    f["store_weekday_avg"] = pd.Series(weekday.to_numpy(), index=f.index).fillna(f.store_avg)
    promo = history["store_weekday_promo"].reindex(
        pd.MultiIndex.from_frame(d[["store_id", "day_of_week", "promo"]]))
    f["store_weekday_promo_avg"] = pd.Series(promo.to_numpy(), index=f.index).fillna(f.store_weekday_avg)

    return f[FEATURES].astype("float32")
