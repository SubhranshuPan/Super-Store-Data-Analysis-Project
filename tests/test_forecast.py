from superstore.data import load_and_clean
from superstore.forecast import forecast_monthly_sales


def test_forecast_shape_and_columns():
    df = load_and_clean()
    result = forecast_monthly_sales(df, periods=6)

    assert {"Sales", "Forecast", "Lower CI", "Upper CI"}.issubset(result.columns)

    forecast_only = result[result["Sales"].isna()]
    assert len(forecast_only) == 6
    assert forecast_only["Forecast"].isna().sum() == 0
    assert forecast_only["Lower CI"].isna().sum() == 0
    assert forecast_only["Upper CI"].isna().sum() == 0


def test_forecast_confidence_interval_brackets_the_point_forecast():
    df = load_and_clean()
    result = forecast_monthly_sales(df, periods=3)
    forecast_only = result[result["Sales"].isna()]

    assert (forecast_only["Lower CI"] <= forecast_only["Forecast"]).all()
    assert (forecast_only["Forecast"] <= forecast_only["Upper CI"]).all()


def test_forecast_respects_requested_horizon():
    df = load_and_clean()
    for periods in (3, 6, 9):
        result = forecast_monthly_sales(df, periods=periods)
        assert result["Sales"].isna().sum() == periods
