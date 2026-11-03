"""Sales Analytics: how sales move over time, by weekday and promotion, and by store type."""
import plotly.express as px
import streamlit as st

from salevora import ui

st.set_page_config(page_title="Sales Analytics", page_icon="📈", layout="wide")
st.title("Sales Analytics")
store_id = ui.store_picker()

monthly = ui.monthly_sales(store_id)
st.plotly_chart(px.line(monthly, x="month", y="sales_per_open_day", markers=True,
                        title="Sales per open day, by month",
                        labels={"month": "", "sales_per_open_day": "Sales per open day"}),
                use_container_width=True)
st.caption("Per open day, so closed days and the July–December 2014 gap (180 stores missing) don't distort it.")

left, right = st.columns(2)
weekday = ui.weekday_promo(store_id).assign(
    day=lambda d: d.day_of_week.map(ui.DAY_NAMES),
    promo=lambda d: d.promo.map({0: "No promo", 1: "Promo"}))
left.plotly_chart(px.bar(weekday, x="day", y="avg_sales", color="promo", barmode="group",
                         title="Average sales per open day, by weekday",
                         labels={"day": "", "avg_sales": "Average sales", "promo": ""}),
                  use_container_width=True)
left.caption("Promotions run Monday to Friday only. Higher sales on promo days are an association, not proof of cause.")

if store_id == 0:
    types = ui.store_types()
    right.plotly_chart(px.bar(types, x="store_type", y="sales_per_open_day", text_auto=",.0f",
                              hover_data=["stores", "sales_per_customer"],
                              title="Sales per open day, by store type",
                              labels={"store_type": "Store type", "sales_per_open_day": "Sales per open day"}),
                       use_container_width=True)
    right.dataframe(types.round(2), hide_index=True, use_container_width=True)
else:
    store = ui.stores().set_index("store_id").loc[store_id]
    right.subheader(f"Store {store_id}")
    right.write(f"Type **{store.store_type}**, assortment **{store.assortment}**, "
                f"nearest competitor **{store.competition_distance:,.0f} m** away."
                if store.competition_distance == store.competition_distance  # not NaN
                else f"Type **{store.store_type}**, assortment **{store.assortment}**.")
