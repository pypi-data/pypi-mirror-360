# pyright: reportArgumentType=false, reportUnknownMemberType=false, reportMissingTypeStubs=false
from dataexplorer.data.datamodel import (
    apply_filter,
    categorical_comparator,
    datetime_comparator,
    handle_dtype_operation,
    handle_nan_operation,
    numeric_comparator,
    FilterStore,
)
from dataexplorer.data.dataenums import Dtype
from spoofs import debug_error_spoof as debug_spoof
import pandas as pd


def test_dtype_conversion():
    # 6 possible conversions, but only 3 valid conversions
    # Any -> Categorical, Numeric -> Categorical, Categorical -> Datetime.
    data = pd.read_excel("Test.xlsx", engine="calamine")
    # Dates column is default read as categorical in this case.
    assert not datetime_comparator(data["Dates"])
    # Categorical -> Datetime
    assert datetime_comparator(
        handle_dtype_operation(data["Dates"], "Datetime", debug_spoof)
    )
    # Numeric -> Categorical
    assert categorical_comparator(
        handle_dtype_operation(data["Header 1"], "Categorical", debug_spoof)
    )
    # Categorical (empty column) -> Numeric
    assert numeric_comparator(
        handle_dtype_operation(data["Header 2"], "Numeric", debug_spoof)
    )


def test_nan_handling():
    data = pd.read_excel("TestNaN.xlsx", engine="calamine")
    data["Dates"] = handle_dtype_operation(data["Dates"], "Datetime", debug_spoof)
    data = handle_nan_operation(data, "Keep as NaN", "Dates", debug_spoof)
    assert data["Dates"].isna().sum() == 2
    data = handle_nan_operation(data, "Replace with No Data", "Header 3", debug_spoof)
    assert data["Header 3"].str.contains("No Data").sum() == 3
    data = handle_nan_operation(data, "Replace with 0", "Header 2", debug_spoof)
    assert (data["Header 2"] == 0).sum() == len(data)


def test_filtering():
    filter = FilterStore(dtype=Dtype.CATEGORICAL, filter_value=["Hello"])
    data = pd.read_excel("Test.xlsx", engine="calamine")
    data = apply_filter(data, column="Header 3", filterstore=filter)
    assert len(data) == 4
    data = pd.read_excel("Test.xlsx", engine="calamine")
    filter = FilterStore(dtype=Dtype.NUMERIC, filter_value=(10, 100))
    data = apply_filter(data, column="Header 1", filterstore=filter)
    assert len(data) == 2
