"""Explainable AI: which inputs drive the forecasts, overall and for one store (SHAP values)."""
import numpy as np
import plotly.express as px
import streamlit as st

from salevora import ui

st.set_page_config(page_title="Explainable AI", page_icon="📈", layout="wide")
st.title("Explainable AI")

overall = ui.shap_global()
model = overall.model.iloc[0]
st.write(f"SHAP values show how much each input pushed the **{model}** forecast up or down. "
         "The model works in log sales, so each push *multiplies* the forecast: "
         "+0.10 means about 10% higher.")

st.plotly_chart(px.bar(overall.iloc[::-1], x="mean_abs_shap", y="label", orientation="h",
                       title="Average push per input, over 2,000 forecast days",
                       labels={"mean_abs_shap": "Average size of push (log sales)", "label": ""}),
                use_container_width=True)

store_id = ui.store_picker(forecast_only=True, allow_all=False)
values = ui.shap_store(store_id)
day = values.forecast_date.iloc[0]
start = np.expm1(values.base_value.iloc[0])
forecast = np.expm1(values.base_value.iloc[0] + values.shap_value.sum())
top = values.head(8).assign(effect=lambda d: np.expm1(d.shap_value))

st.subheader(f"Store {store_id} on {day:%A %d %B %Y}")
st.write(f"The model starts from its average forecast of **{start:,.0f}**. "
         f"These inputs move it to **{forecast:,.0f}**:")
st.plotly_chart(px.bar(top.iloc[::-1], x="effect", y="label", orientation="h", text_auto="+.0%",
                       color=top.iloc[::-1].effect > 0, color_discrete_map={True: "#2ca02c", False: "#d62728"},
                       title="Biggest effects on this forecast",
                       labels={"effect": "Effect on the forecast", "label": ""})
                .update_layout(showlegend=False).update_xaxes(tickformat="+.0%"),
                use_container_width=True)
st.dataframe(top[["label", "feature_value", "effect"]].rename(columns={
    "label": "Input", "feature_value": "Value", "effect": "Effect"}).style.format({"Effect": "{:+.1%}", "Value": "{:,.2f}"}),
    hide_index=True, use_container_width=True)
st.caption("Explanations describe what the model learned, not proof of cause and effect.")
