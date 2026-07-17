"""
SuperStore Sales & Profitability Dashboard
Run with: streamlit run dashboard/app.py
"""
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from superstore import forecast_monthly_sales, load_and_clean  # noqa: E402

st.set_page_config(page_title="SuperStore Sales Dashboard", layout="wide", page_icon="📊")


@st.cache_data
def load_data():
    # Shared cleaning logic (superstore/data.py) - same rules used by the
    # notebook and scripts/run_analysis.py, so all three stay in sync.
    return load_and_clean()


df = load_data()

st.title("📊 SuperStore Sales & Profitability Dashboard")
st.caption(
    "Interactive companion to the analysis notebook — filter the data on the left "
    "and every chart, KPI and table below updates live."
)

# ---------------------------------------------------------------- Sidebar filters
st.sidebar.header("Filters")

min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input(
    "Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
segments = st.sidebar.multiselect("Segment", sorted(df["Segment"].unique()), default=sorted(df["Segment"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = min_date, max_date

mask = (
    df["Order Date"].between(start, end)
    & df["Segment"].isin(segments)
    & df["Category"].isin(categories)
    & df["Region"].isin(regions)
)
fdf = df[mask]

if fdf.empty:
    st.warning("No data matches the current filters — widen your selection.")
    st.stop()

# ---------------------------------------------------------------- KPI row
total_sales = fdf["Sales"].sum()
total_profit = fdf["Profit"].sum()
margin = (total_profit / total_sales * 100) if total_sales else 0
n_orders = fdf["Order ID"].nunique()
n_customers = fdf["Customer ID"].nunique()
aov = fdf.groupby("Order ID")["Sales"].sum().mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Sales", f"${total_sales:,.0f}")
c2.metric("Total Profit", f"${total_profit:,.0f}")
c3.metric("Profit Margin", f"{margin:.1f}%")
c4.metric("Orders", f"{n_orders:,}")
c5.metric("Avg. Order Value", f"${aov:,.0f}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Customers", "Products & Profitability", "Geography", "Time Trends", "Forecast"]
)

# ---------------------------------------------------------------- Customers
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        seg_sales = fdf.groupby("Segment")["Sales"].sum().reset_index()
        fig = px.pie(seg_sales, names="Segment", values="Sales", title="Sales Share by Segment", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        cust_rev = fdf.groupby(["Segment", "Customer ID"])["Sales"].sum().reset_index()
        cltv = cust_rev.groupby("Segment")["Sales"].mean().reset_index(name="Avg CLTV")
        fig = px.bar(cltv, x="Segment", y="Avg CLTV", title="Average Customer Lifetime Value by Segment", color="Segment")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Customers by Sales")
    top_customers = (
        fdf.groupby(["Customer ID", "Customer Name", "Segment"])["Sales"].sum()
        .sort_values(ascending=False).head(10).reset_index()
    )
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- Products
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        cat = fdf.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        fig = px.bar(cat, x="Category", y=["Sales", "Profit"], barmode="group", title="Sales vs Profit by Category")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        subcat = fdf.groupby(["Category", "Sub-Category"]).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum")
        ).reset_index().sort_values("Profit")
        subcat["Loss-making"] = subcat["Profit"] < 0
        fig = px.bar(
            subcat, x="Profit", y="Sub-Category", orientation="h", color="Loss-making",
            color_discrete_map={True: "#d62728", False: "#2ca02c"},
            title="Profit by Sub-Category",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Discount vs. Average Profit per Order")
    disc_bins = pd.cut(fdf["Discount"], bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0])
    disc_profit = fdf.groupby(disc_bins, observed=True)["Profit"].mean().reset_index()
    disc_profit["Discount"] = disc_profit["Discount"].astype(str)
    fig = px.bar(disc_profit, x="Discount", y="Profit", title="Avg Profit per Order by Discount Band")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- Geography
with tab3:
    state_perf = fdf.groupby("State").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
    all_state_mapping = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
        "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
        "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
        "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
        "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
        "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
        "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    }
    state_perf["Abbreviation"] = state_perf["State"].map(all_state_mapping)

    metric_choice = st.radio("Map metric", ["Sales", "Profit"], horizontal=True)
    fig = px.choropleth(
        state_perf, locations="Abbreviation", locationmode="USA-states", color=metric_choice,
        scope="usa", color_continuous_scale="RdYlGn" if metric_choice == "Profit" else "Blues",
        color_continuous_midpoint=0 if metric_choice == "Profit" else None,
        title=f"Total {metric_choice} by State",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top / Bottom 5 States by Profit")
    col1, col2 = st.columns(2)
    col1.dataframe(state_perf.sort_values("Profit", ascending=False).head(5)[["State", "Sales", "Profit"]],
                    hide_index=True, use_container_width=True)
    col2.dataframe(state_perf.sort_values("Profit").head(5)[["State", "Sales", "Profit"]],
                    hide_index=True, use_container_width=True)

# ---------------------------------------------------------------- Time trends
with tab4:
    granularity = st.radio("Granularity", ["Monthly", "Quarterly", "Yearly"], horizontal=True)
    freq_map = {"Monthly": "ME", "Quarterly": "QE", "Yearly": "YE"}
    trend = fdf.set_index("Order Date").resample(freq_map[granularity]).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    ).reset_index()
    fig = px.line(trend, x="Order Date", y=["Sales", "Profit"], markers=True, title=f"{granularity} Sales & Profit Trend")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Seasonality: Average Sales by Calendar Month")
    seasonality = fdf.groupby(fdf["Order Date"].dt.month_name())["Sales"].mean()
    month_order = ["January", "February", "March", "April", "May", "June", "July",
                    "August", "September", "October", "November", "December"]
    seasonality = seasonality.reindex(month_order)
    fig = px.bar(seasonality.reset_index(), x="Order Date", y="Sales", title="Avg Sales by Month")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- Forecast
with tab5:
    st.subheader("Sales Forecast")
    st.caption(
        "SARIMA model (seasonal ARIMA) trained on the full monthly sales history, forecasting "
        "forward. Filters above don't apply here since a forecast needs the complete, unfiltered "
        "time series to estimate seasonality reliably."
    )
    horizon = st.slider("Months to forecast", min_value=3, max_value=12, value=6)
    with st.spinner("Fitting SARIMA model..."):
        forecast_df = forecast_monthly_sales(df, periods=horizon)

    hist = forecast_df.dropna(subset=["Sales"])
    fut = forecast_df[forecast_df["Sales"].isna()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Sales"], mode="lines+markers", name="Actual"))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["Forecast"], mode="lines",
                              line=dict(dash="dash", color="firebrick"), name="Forecast"))
    if "Lower CI" in fut.columns:
        fig.add_trace(go.Scatter(x=fut.index, y=fut["Upper CI"], mode="lines",
                                  line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=fut.index, y=fut["Lower CI"], mode="lines",
                                  line=dict(width=0), fill="tonexty",
                                  fillcolor="rgba(214,39,40,0.15)", name="80% CI"))
    fig.update_layout(title=f"Monthly Sales: Actual + {horizon}-Month Forecast", yaxis_tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Forecast table (next {horizon} months)")
    st.dataframe(
        fut[["Forecast", "Lower CI", "Upper CI"]].round(0).rename_axis("Month").reset_index(),
        hide_index=True, use_container_width=True,
    )

st.divider()
st.caption(
    "Data: SuperStore order-level sales enriched with Profit/Discount/Quantity "
    "(see data/README.md for methodology). Built with Streamlit + Plotly."
)
