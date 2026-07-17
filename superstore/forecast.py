"""Lightweight sales forecasting on top of the monthly sales trend.

Uses a seasonal ARIMA (SARIMAX) model - a small, dependency-light choice
that works well for a single, fairly regular monthly series like this one,
without needing the heavier Prophet stack.
"""
import warnings

import pandas as pd


def _monthly_series(df: pd.DataFrame) -> pd.Series:
    return df.set_index("Order Date").resample("ME")["Sales"].sum()


def forecast_monthly_sales(df: pd.DataFrame, periods: int = 6) -> pd.DataFrame:
    """Forecast total monthly Sales `periods` months beyond the data's range.

    Returns a DataFrame indexed by month with columns:
    Sales (actuals, NaN for forecast months), Forecast, Lower CI, Upper CI.
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    monthly = _monthly_series(df)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            monthly,
            order=(1, 1, 1),
            seasonal_order=(1, 1, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fit = model.fit(disp=False)
        pred = fit.get_forecast(steps=periods)

    forecast_index = pd.date_range(
        monthly.index[-1] + pd.offsets.MonthEnd(1), periods=periods, freq="ME"
    )
    forecast_mean = pd.Series(pred.predicted_mean.values, index=forecast_index)
    ci = pred.conf_int(alpha=0.2)
    lower = pd.Series(ci.iloc[:, 0].values, index=forecast_index)
    upper = pd.Series(ci.iloc[:, 1].values, index=forecast_index)

    out = pd.DataFrame({
        "Sales": monthly.reindex(monthly.index.union(forecast_index)),
        "Forecast": pd.Series(index=monthly.index, dtype=float).reindex(monthly.index.union(forecast_index)),
    })
    out.loc[monthly.index, "Forecast"] = monthly.values  # so the line connects visually
    out.loc[forecast_index, "Forecast"] = forecast_mean.values
    out.loc[forecast_index, "Lower CI"] = lower.values
    out.loc[forecast_index, "Upper CI"] = upper.values
    return out
