import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def raw_df():
    """A small synthetic frame shaped like the real dataset, with the same
    quirks (a missing postal code, a duplicate row, dd/mm/yyyy dates)."""
    data = {
        "Row ID": [1, 1, 2, 2],  # intentional exact duplicates to test dedup
        "Order ID": ["CA-2017-0001", "CA-2017-0001", "CA-2017-0002", "CA-2017-0002"],
        "Order Date": ["08/11/2017", "08/11/2017", "01/01/2018", "01/01/2018"],
        "Ship Date": ["11/11/2017", "11/11/2017", "05/01/2018", "05/01/2018"],
        "Ship Mode": ["Second Class", "Second Class", "Standard Class", "Standard Class"],
        "Customer ID": ["CG-1", "CG-1", "DV-2", "DV-2"],
        "Customer Name": ["Claire Gute", "Claire Gute", "Darrin Van Huff", "Darrin Van Huff"],
        "Segment": ["Consumer", "Consumer", "Corporate", "Corporate"],
        "Country": ["United States"] * 4,
        "City": ["Henderson", "Henderson", "Los Angeles", "Los Angeles"],
        "State": ["Kentucky", "Kentucky", "California", "California"],
        "Postal Code": [42420.0, 42420.0, None, None],
        "Region": ["South", "South", "West", "West"],
        "Product ID": ["FUR-BO-1", "FUR-BO-1", "OFF-LA-1", "OFF-LA-1"],
        "Category": ["Furniture", "Furniture", "Office Supplies", "Office Supplies"],
        "Sub-Category": ["Bookcases", "Bookcases", "Labels", "Labels"],
        "Product Name": ["Bookcase", "Bookcase", "Labels", "Labels"],
        "Sales": [261.96, 261.96, 14.62, 14.62],
        "Quantity": [2, 2, 3, 3],
        "Discount": [0.0, 0.0, 0.2, 0.2],
        "Profit": [41.91, 41.91, 6.87, 6.87],
    }
    return pd.DataFrame(data)
