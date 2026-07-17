"""Data loading and cleaning for the SuperStore dataset."""
import os

import pandas as pd

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_THIS_DIR)
DEFAULT_DATA_PATH = os.path.join(REPO_ROOT, "data", "superstore_sales.csv")


def load_data(path: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the raw SuperStore CSV."""
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the project's standard cleaning steps.

    - Fill missing Postal Code with 0 and cast to int.
    - Parse Order Date / Ship Date as day-first datetimes.
    - Derive 'Order to Ship Days'.
    - Drop exact duplicate rows.

    Returns a new DataFrame; does not mutate the input.
    """
    df = df.copy()
    df["Postal Code"] = df["Postal Code"].fillna(0).astype(int)
    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True)
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], dayfirst=True)
    df["Order to Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
    df = df.drop_duplicates()
    return df


def load_and_clean(path: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Convenience wrapper: load_data + clean_data in one call."""
    return clean_data(load_data(path))
