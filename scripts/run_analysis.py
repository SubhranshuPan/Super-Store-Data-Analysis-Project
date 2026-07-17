"""
Superstore Sales Analysis - core analysis pipeline.
Loads the enriched dataset, cleans it, computes all metrics used in the
notebook / dashboard / README / PDF report, and saves static chart images.

Run: python scripts/run_analysis.py
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid")
PALETTE = "viridis"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data", "superstore_sales.csv")
IMG_DIR = os.path.join(BASE, "assets", "images")
METRICS_PATH = os.path.join(BASE, "reports", "metrics.json")
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)


def money(ax_or_fmt="{x:,.0f}"):
    return mticker.StrMethodFormatter(ax_or_fmt)


def load_and_clean():
    df = pd.read_csv(DATA_PATH)
    df["Postal Code"] = df["Postal Code"].fillna(0).astype(int)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True)
    df["Order to Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    dupes = int(df.duplicated().sum())
    df = df.drop_duplicates()
    return df, dupes


def save(fig, name):
    path = os.path.join(IMG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def main():
    df, dupes = load_and_clean()
    metrics = {"n_rows": len(df), "n_duplicates_removed": dupes}

    # ---- Customer segmentation ----
    seg_counts = df["Segment"].value_counts()
    seg_sales = df.groupby("Segment")["Sales"].sum().sort_values(ascending=False)
    seg_profit = df.groupby("Segment")["Profit"].sum().sort_values(ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].pie(seg_counts, labels=seg_counts.index, autopct="%1.1f%%",
                colors=sns.color_palette(PALETTE, len(seg_counts)))
    axes[0].set_title("Customers by Segment")
    axes[1].bar(seg_sales.index, seg_sales.values, color=sns.color_palette(PALETTE, len(seg_sales)))
    axes[1].set_title("Total Sales by Segment ($)")
    axes[1].yaxis.set_major_formatter(money())
    fig.tight_layout()
    save(fig, "01_segment_overview.png")

    metrics["segment_customer_share"] = seg_counts.to_dict()
    metrics["segment_sales"] = seg_sales.round(2).to_dict()
    metrics["segment_profit"] = seg_profit.round(2).to_dict()

    # ---- Customer Lifetime Value (CLTV) proxy: avg revenue per customer per segment ----
    cust_rev = df.groupby(["Segment", "Customer ID"])["Sales"].sum().reset_index()
    cltv = cust_rev.groupby("Segment")["Sales"].mean().sort_values(ascending=False)
    metrics["avg_cltv_by_segment"] = cltv.round(2).to_dict()

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(cltv.index, cltv.values, color=sns.color_palette(PALETTE, len(cltv)))
    ax.set_title("Average Customer Lifetime Value by Segment")
    ax.set_ylabel("Avg total Sales per customer ($)")
    ax.yaxis.set_major_formatter(money())
    fig.tight_layout()
    save(fig, "02_cltv_by_segment.png")

    # ---- RFM segmentation ----
    snapshot = df["Order Date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("Customer ID").agg(
        Recency=("Order Date", lambda x: (snapshot - x.max()).days),
        Frequency=("Order ID", "nunique"),
        Monetary=("Sales", "sum"),
    ).reset_index()

    r_labels, f_labels, m_labels = range(4, 0, -1), range(1, 5), range(1, 5)
    rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=r_labels).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=f_labels).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"], 4, labels=m_labels).astype(int)
    rfm["RFM_Score"] = rfm["R"] + rfm["F"] + rfm["M"]

    def tier(score):
        if score >= 10:
            return "Champions"
        elif score >= 8:
            return "Loyal Customers"
        elif score >= 6:
            return "Potential Loyalists"
        elif score >= 4:
            return "At Risk"
        return "Lost / Dormant"

    rfm["Customer Tier"] = rfm["RFM_Score"].apply(tier)
    tier_counts = rfm["Customer Tier"].value_counts()
    metrics["rfm_tier_counts"] = tier_counts.to_dict()
    rfm.to_csv(os.path.join(BASE, "reports", "rfm_customer_segments.csv"), index=False)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    order = ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Lost / Dormant"]
    vals = [tier_counts.get(o, 0) for o in order]
    ax.barh(order, vals, color=sns.color_palette(PALETTE, len(order)))
    ax.set_title("Customers by RFM Tier")
    ax.set_xlabel("Number of customers")
    fig.tight_layout()
    save(fig, "03_rfm_tiers.png")

    # ---- Repeat customers / top spenders ----
    order_freq = df.groupby(["Customer ID", "Customer Name"])["Order ID"].nunique().reset_index(name="Total Orders")
    repeat_rate = (order_freq["Total Orders"] > 1).mean()
    metrics["repeat_customer_rate"] = round(float(repeat_rate), 4)

    top_spenders = df.groupby(["Customer ID", "Customer Name"])["Sales"].sum().sort_values(ascending=False).head(10)
    metrics["top_10_customers_by_sales"] = {k[1]: round(v, 2) for k, v in top_spenders.items()}

    # ---- Shipping mode ----
    ship_counts = df["Ship Mode"].value_counts()
    avg_ship_days = df.groupby("Ship Mode")["Order to Ship Days"].mean().round(1)
    metrics["ship_mode_share"] = ship_counts.to_dict()
    metrics["avg_fulfillment_days_by_mode"] = avg_ship_days.to_dict()

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.pie(ship_counts, labels=ship_counts.index, autopct="%1.1f%%",
           colors=sns.color_palette(PALETTE, len(ship_counts)))
    ax.set_title("Orders by Shipping Mode")
    fig.tight_layout()
    save(fig, "04_shipping_mode.png")

    # ---- Geographic ----
    state_sales = df.groupby("State")["Sales"].sum().sort_values(ascending=False)
    state_profit = df.groupby("State")["Profit"].sum().sort_values()
    metrics["top_10_states_by_sales"] = state_sales.head(10).round(2).to_dict()
    metrics["least_profitable_states"] = state_profit.head(5).round(2).to_dict()

    fig, ax = plt.subplots(figsize=(8, 6))
    top15 = state_sales.head(15).sort_values()
    ax.barh(top15.index, top15.values, color=sns.color_palette(PALETTE, len(top15)))
    ax.set_title("Top 15 States by Total Sales")
    ax.xaxis.set_major_formatter(money())
    fig.tight_layout()
    save(fig, "05_top_states_sales.png")

    # ---- Category / Sub-category + profitability ----
    cat_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    cat_profit = df.groupby("Category")["Profit"].sum().sort_values(ascending=False)
    metrics["category_sales"] = cat_sales.round(2).to_dict()
    metrics["category_profit"] = cat_profit.round(2).to_dict()

    subcat = df.groupby(["Category", "Sub-Category"]).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    ).reset_index()
    subcat["Profit Margin %"] = (subcat["Profit"] / subcat["Sales"] * 100).round(1)
    subcat_sorted = subcat.sort_values("Profit")
    metrics["loss_making_subcategories"] = (
        subcat_sorted[subcat_sorted["Profit"] < 0][["Sub-Category", "Sales", "Profit", "Profit Margin %"]]
        .round(2).to_dict(orient="records")
    )
    subcat.to_csv(os.path.join(BASE, "reports", "subcategory_profitability.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["#d62728" if v < 0 else sns.color_palette(PALETTE, 1)[0] for v in subcat_sorted["Profit"]]
    ax.barh(subcat_sorted["Sub-Category"], subcat_sorted["Profit"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_title("Profit by Sub-Category (red = loss-making)")
    ax.xaxis.set_major_formatter(money())
    fig.tight_layout()
    save(fig, "06_subcategory_profit.png")

    # ---- Discount vs profit ----
    disc_bins = pd.cut(df["Discount"], bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0])
    disc_profit = df.groupby(disc_bins)["Profit"].mean()
    metrics["avg_profit_by_discount_band"] = {str(k): round(v, 2) for k, v in disc_profit.items()}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar([str(i) for i in disc_profit.index], disc_profit.values,
           color=sns.color_palette(PALETTE, len(disc_profit)))
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Average Profit per Order by Discount Band")
    ax.set_xlabel("Discount band")
    ax.set_ylabel("Avg profit ($)")
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    save(fig, "07_discount_vs_profit.png")

    # ---- Time trends ----
    yearly = df.groupby(df["Order Date"].dt.year)["Sales"].sum()
    yoy_growth = yearly.pct_change().round(4)
    metrics["yearly_sales"] = {int(k): round(v, 2) for k, v in yearly.items()}
    metrics["yoy_growth_pct"] = {int(k): (None if pd.isna(v) else round(v * 100, 1)) for k, v in yoy_growth.items()}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(yearly.index, yearly.values, marker="o", linewidth=2, color=sns.color_palette(PALETTE, 1)[0])
    ax.set_title("Total Sales by Year")
    ax.yaxis.set_major_formatter(money())
    ax.set_xticks(list(yearly.index))
    fig.tight_layout()
    save(fig, "08_yearly_sales.png")

    monthly = df.set_index("Order Date").resample("ME")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(monthly.index, monthly.values, marker="o", markersize=3, linewidth=1.5,
             color=sns.color_palette(PALETTE, 1)[0])
    ax.set_title("Monthly Sales Trend (all years)")
    ax.yaxis.set_major_formatter(money())
    fig.tight_layout()
    save(fig, "09_monthly_trend.png")

    monthly_seasonality = df.groupby(df["Order Date"].dt.month)["Sales"].mean()
    metrics["avg_sales_by_calendar_month"] = {int(k): round(v, 2) for k, v in monthly_seasonality.items()}

    # ---- Headline KPIs ----
    metrics["total_sales"] = round(float(df["Sales"].sum()), 2)
    metrics["total_profit"] = round(float(df["Profit"].sum()), 2)
    metrics["overall_profit_margin_pct"] = round(float(df["Profit"].sum() / df["Sales"].sum() * 100), 2)
    metrics["total_orders"] = int(df["Order ID"].nunique())
    metrics["total_customers"] = int(df["Customer ID"].nunique())
    metrics["avg_order_value"] = round(float(df.groupby("Order ID")["Sales"].sum().mean()), 2)
    metrics["date_range"] = [str(df["Order Date"].min().date()), str(df["Order Date"].max().date())]

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    print("Metrics written to", METRICS_PATH)
    print(json.dumps({k: metrics[k] for k in ["total_sales", "total_profit", "overall_profit_margin_pct",
                                                "total_orders", "total_customers", "repeat_customer_rate"]}, indent=2))


if __name__ == "__main__":
    main()
