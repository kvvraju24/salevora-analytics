"""Salevora Analytics: the app's home page.

    streamlit run app/Home.py
"""
import streamlit as st

from salevora import ui

st.set_page_config(page_title="Salevora Analytics", page_icon="📈", layout="wide")
st.title("Salevora Analytics")
st.write("Sales analysis and a 48-day forecast for 1,115 Rossmann drugstores "
         "(Kaggle data, January 2013 – July 2015).")

summary = ui.overview().iloc[0]
scores = ui.model_scores().set_index("model")
best = scores[scores.is_best == 1].index[0]

columns = st.columns(4)
columns[0].metric("Stores", f"{summary.stores:,}")
columns[1].metric("Total sales", f"{summary.total_sales / 1e9:.2f} bn")
columns[2].metric("Sales per open day", f"{summary.sales_per_open_day:,.0f}")
columns[3].metric(f"Forecast error ({best})", f"{scores.loc[best, 'wape']:.1%} WAPE",
                  f"{scores.loc[best, 'wape'] - scores.loc['Baseline', 'wape']:+.1%} vs baseline",
                  delta_color="inverse")

st.markdown("""
**Pages** (left sidebar)

- **Sales Analytics:** monthly trend, weekday and promotion pattern, store types
- **Forecast:** the next 48 days (1 Aug – 17 Sep 2015) for any store, with an error range
- **Model Comparison:** five models tested on the last 48 days of history
- **Explainable AI:** which inputs drive the forecasts, overall and for one store
""")
st.caption("This is historical data: the forecast covers the 48 days after the history ends, "
           "not today's sales. Code: github.com/kvvraju24/salevora-analytics")
