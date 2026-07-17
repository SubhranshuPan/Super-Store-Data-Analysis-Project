# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-07-17

First full release: a profitability-focused rewrite of a 2-year-old EDA project into a
production-shaped analysis project.

### Added
- **Enriched dataset:** merged `Profit`, `Discount` and `Quantity` into the original
  sales-only dataset via a verified Row ID join against a public reference dataset,
  enabling real profitability analysis (see `data/README.md`).
- **Rewritten notebook** (`notebooks/SuperStore_Sales_Analysis.ipynb`): executive
  summary, customer segmentation, CLTV, RFM segmentation, shipping analysis,
  geographic profit/sales mapping, category/sub-category profitability, discount
  impact analysis, time-series trends, and a SARIMA sales forecast.
- **Interactive Streamlit dashboard** (`dashboard/app.py`): filterable KPIs across
  Customers, Products & Profitability, Geography, Time Trends and Forecast tabs.
- **Shared `superstore` package** (`superstore/data.py`, `superstore/forecast.py`):
  single source of truth for data cleaning and forecasting, used by the notebook,
  `scripts/run_analysis.py`, and the dashboard.
- **One-page executive summary PDF** (`reports/Executive_Summary.pdf`).
- **Automated tests** (`tests/`, 9 tests via pytest) covering cleaning and forecasting logic.
- **CI** (`.github/workflows/ci.yml`): lint (ruff) + test (pytest) + smoke-run on every push/PR.
- **Release automation** (`.github/workflows/release.yml`): on every `vX.Y.Z` tag, builds
  a Python wheel/sdist attached to the GitHub Release, and builds + publishes a Docker
  image of the dashboard to the GitHub Container Registry (`ghcr.io`).
- **Docker packaging** (`Dockerfile`): the dashboard can be run as a standalone container.
- Repo hygiene: `requirements.txt` / `requirements-dev.txt`, `.gitignore`, MIT `LICENSE`,
  `pyproject.toml` (packaging + pytest + ruff config).

### Fixed
- Notebook's hardcoded Google Colab file path, which made it unrunnable outside Colab.
- Customer Lifetime Value section, previously a dead comment with no implementation.

### Changed
- README rewritten with real KPIs, embedded chart images, tech stack, run instructions,
  and a project structure overview.
