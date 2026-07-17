# Data Notes

**File:** `superstore_sales.csv` (9,800 order line items, 2015-01-03 to 2018-12-30)

## Source & enrichment

The base file (`Order ID`, `Sales`, customer/product/geography attributes) is a
public Kaggle "Superstore Sales" training split. It does **not** include
`Profit`, `Discount`, or `Quantity`.

Those three columns were sourced from the public reference **"Sample –
Superstore"** dataset (the classic Tableau sample dataset, widely mirrored on
GitHub) and merged in on `Row ID`. Before merging, the join was verified as an
exact 1:1 match for every row — `Product ID`, `Customer Name` and `Sales`
value are identical between the two files for matching `Row ID`s, confirming
they describe the same underlying transactions (the reference file uses
order/ship dates one year earlier, which is expected and doesn't affect the
merge since only `Quantity`/`Discount`/`Profit` were pulled across).

This means every profitability figure in this project (`Profit`, margin,
discount-impact analysis) is real transactional data, not a simulated or
estimated column.

## Columns

| Column | Description |
|---|---|
| Row ID | Row identifier, used as the join key for enrichment |
| Order ID / Order Date / Ship Date / Ship Mode | Order metadata |
| Customer ID / Customer Name / Segment | Customer attributes |
| Country / City / State / Postal Code / Region | Geography |
| Product ID / Category / Sub-Category / Product Name | Product attributes |
| Sales | Revenue for the line item ($) |
| Quantity | Units sold (enriched) |
| Discount | Discount applied, 0-1 (enriched) |
| Profit | Profit for the line item, $ (enriched) |
