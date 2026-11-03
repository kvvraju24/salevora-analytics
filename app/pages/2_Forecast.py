"""Forecast: the 48 days after the history ends, for the whole chain or one store."""
import plotly.graph_objects as go
import streamlit as st

from salevora import ui

st.set_page_config(page_title="Forecast", page_icon="📈", layout="wide")
st.title("Forecast: 1 August – 17 September 2015")
store_id = ui.store_picker(forecast_only=True)
model = st.sidebar.radio("Model", ui.forecast_models())

# Same 856 stores as the forecast, so "All stores" compares like with like.
history = ui.daily_history(store_id, days=56, forecast_stores_only=True)
future = ui.forecast(store_id, model)

figure = go.Figure()
figure.add_scatter(x=history.date, y=history.sales, name="Actual (last 8 weeks)", line={"color": "grey"})
figure.add_scatter(x=future.date, y=future.predicted, name=f"Forecast ({model})", line={"color": "#1f77b4"})
radius = ui.error_range(store_id, model) if store_id else None
if radius:
    upper = future.predicted + radius
    lower = (future.predicted - radius).clip(lower=0).where(future.predicted > 0, 0)
    figure.add_scatter(x=future.date, y=upper.where(future.predicted > 0, 0), line={"width": 0},
                       showlegend=False, hoverinfo="skip")
    figure.add_scatter(x=future.date, y=lower, fill="tonexty", line={"width": 0},
                       fillcolor="rgba(31,119,180,0.15)", name="Typical error range")
figure.update_layout(title="Daily sales", yaxis_title="Sales", hovermode="x unified")
st.plotly_chart(figure, use_container_width=True)

def short(value: float) -> str:
    """240,407,183 -> '240.4 M' so big numbers fit in the metric boxes."""
    return f"{value / 1e6:,.1f} M" if value >= 1e6 else f"{value:,.0f}"


last_48 = ui.daily_history(store_id, days=48, forecast_stores_only=True).sales.sum()
columns = st.columns(3)
columns[0].metric("Forecast total, 48 days", short(future.predicted.sum()),
                  f"{future.predicted.sum() / last_48 - 1:+.1%} vs last 48 days")
columns[1].metric("Forecast per day", short(future.predicted.mean()))
columns[2].metric("Last 48 days of history", short(last_48))

if radius:
    st.caption(f"Shaded band: ±{radius:,.0f}. On the 48 held-out days, 80% of this store's daily errors were "
               "smaller than that. It's a guide, not a guaranteed range. Days at 0 are scheduled closures.")
else:
    st.caption("Error ranges are shown for single stores only: adding up store ranges would overstate how "
               "sure we are about the chain. Days near 0 are Sundays and holidays, when most stores close.")

st.download_button("Download this forecast (CSV)", future.to_csv(index=False),
                   file_name=f"forecast_{'all' if store_id == 0 else store_id}_{model}.csv")
