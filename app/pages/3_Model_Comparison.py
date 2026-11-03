"""Model Comparison: five models scored on the same 48 held-out days."""
import pandas as pd
import plotly.express as px
import streamlit as st

from salevora import ui

st.set_page_config(page_title="Model Comparison", page_icon="📈", layout="wide")
st.title("Model Comparison")

scores = ui.model_scores()
first = scores.iloc[0]
st.write(f"Every model was trained only on days before {first.holdout_start:%d %b %Y}, then asked to "
         f"predict the {first.holdout_rows:,} open store-days from {first.holdout_start:%d %b} to "
         f"{first.holdout_end:%d %b %Y}, which it had never seen. Lower is better.")

table = scores[["model", "wape", "rmspe", "mae", "rmse", "seconds"]].rename(columns={
    "model": "Model", "wape": "WAPE", "rmspe": "RMSPE", "mae": "MAE", "rmse": "RMSE", "seconds": "Seconds"})
st.dataframe(table.style.format({"WAPE": "{:.2%}", "RMSPE": "{:.2%}", "MAE": "{:,.0f}",
                                 "RMSE": "{:,.0f}", "Seconds": "{:.0f}"}),
             hide_index=True, use_container_width=True)
st.caption("WAPE: total error ÷ total sales (big stores count more). RMSPE: average % error (Kaggle's metric). "
           "MAE: average error in sales units. RMSE: like MAE, but big misses count more.")

store_id = ui.store_picker()
series = ui.holdout_series(store_id)
chosen = st.multiselect("Models to show", scores.model.tolist(), default=[first.model, "Baseline"])
# One line for the actual sales, plus one per chosen model.
actual = series.drop_duplicates("date")[["date", "actual"]].rename(columns={"actual": "sales"}).assign(line="Actual")
predicted = series[series.model.isin(chosen)].rename(columns={"predicted": "sales", "model": "line"})
lines = pd.concat([actual, predicted[["date", "sales", "line"]]], ignore_index=True)
st.plotly_chart(px.line(lines, x="date", y="sales", color="line",
                        title="Actual vs predicted sales on the held-out days",
                        labels={"date": "", "sales": "Sales", "line": ""}),
                use_container_width=True)
