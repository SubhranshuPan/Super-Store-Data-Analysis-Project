import pandas as pd

from superstore.data import DEFAULT_DATA_PATH, clean_data, load_data


def test_clean_data_fills_missing_postal_code(raw_df):
    cleaned = clean_data(raw_df)
    assert cleaned["Postal Code"].isna().sum() == 0
    assert cleaned["Postal Code"].dtype == int


def test_clean_data_parses_dates_dayfirst(raw_df):
    cleaned = clean_data(raw_df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["Order Date"])
    # "08/11/2017" is day-first -> 8th November, not 11th of August
    assert cleaned["Order Date"].iloc[0] == pd.Timestamp("2017-11-08")


def test_clean_data_drops_exact_duplicates(raw_df):
    assert raw_df.duplicated().sum() == 2  # 2 pairs of duplicate rows in the fixture
    cleaned = clean_data(raw_df)
    assert cleaned.duplicated().sum() == 0
    assert len(cleaned) == 2


def test_clean_data_computes_order_to_ship_days(raw_df):
    cleaned = clean_data(raw_df)
    assert "Order to Ship Days" in cleaned.columns
    # Order 08/11/2017 -> Ship 11/11/2017 = 3 days
    assert cleaned["Order to Ship Days"].iloc[0] == 3


def test_clean_data_does_not_mutate_input(raw_df):
    original_dtype = raw_df["Order Date"].dtype
    clean_data(raw_df)
    assert raw_df["Order Date"].dtype == original_dtype  # input untouched


def test_load_data_reads_the_real_dataset():
    df = load_data(DEFAULT_DATA_PATH)
    expected_cols = {"Row ID", "Order ID", "Sales", "Profit", "Discount", "Quantity"}
    assert expected_cols.issubset(set(df.columns))
    assert len(df) == 9800
