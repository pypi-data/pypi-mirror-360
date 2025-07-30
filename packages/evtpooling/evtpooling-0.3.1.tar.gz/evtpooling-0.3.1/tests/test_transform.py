import numpy as np
import pandas as pd
import pytest

from evtpooling.constants import *
from evtpooling.etl.transform import (
    ExtractError,
    apply_curcdd_preference,
    calculate_daily_loss_returns,
    calculate_weekly_loss_returns,
    clean_categorical_data,
    filter_by_price,
    get_valid_date_coverage,
    handle_missing_data,
    pivot_data,
    validate_data,
)

# Now, since your transform pipeline operates on a pandas DataFrame
# (not on reading CSV files directly), we don't need temporary files anymore.

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def valid_df():
    """Fully valid dataframe fixture"""
    dates = [
        "2008-01-01",
        "2008-01-02",
        "2008-01-03",
        "2008-01-04",
        "2008-01-07",
        "2008-01-08",
        "2008-01-09",
        "2008-01-10",
        "2008-01-11",
        "2008-01-14",
        "2008-01-15",
        "2008-01-16",
    ] * 2
    dates_np = np.array(dates, dtype="datetime64[ns]")

    data = {
        "gvkey": [1] * 12 + [2] * 12,
        "iid": ["01W"] * 12 + ["02W"] * 12,
        "curcdd": ["EUR"] * 12 + ["USD"] * 12,
        "datadate": dates_np,
        "conm": ["CompanyA"] * 12 + ["CompanyB"] * 12,
        "cshtrd": np.random.uniform(low=1.0, high=100.0, size=24).tolist(),
        "prccd": np.random.uniform(low=1.0, high=100.0, size=24).tolist(),
        "prchd": np.random.uniform(low=1.0, high=100.0, size=24).tolist(),
        "prcld": np.random.uniform(low=1.0, high=100.0, size=24).tolist(),
        "trfd": [1.0] * 24,
        "isin": ["AAA"] * 24,
        "costat": ["A"] * 24,
        "ggroup": [10.0] * 24,
        "gind": [100.0] * 24,
        "loc": ["US"] * 24,
    }

    return pd.DataFrame(data)


@pytest.fixture
def invalid_schema_df():
    """Missing required columns"""
    df = pd.DataFrame({"gvkey": [1], "iid": ["01W"], "datadate": pd.to_datetime(["2008-01-01"])})

    return df


@pytest.fixture
def invalid_dtypes_df(valid_df):
    """DataFrame with invalid dtypes"""
    valid_df["prccd"] = valid_df["prccd"].astype(str)  # Change numeric to string

    return valid_df


@pytest.fixture
def incomplete_date_df(valid_df):
    """Missing part of date range"""
    mask = valid_df[DATE_COLUMN] > "2009-01-01"

    return valid_df[mask]


@pytest.fixture
def low_completeness_df(valid_df):
    """Missing many price values"""
    valid_df.loc[0:3, "prccd"] = np.nan

    return valid_df


# --------------------
# Tests
# --------------------


def test_valid_data(valid_df):
    validate_data(valid_df)
    df, _ = get_valid_date_coverage(
        valid_df,
        expected_range=(pd.Timestamp("2008-01-01"), pd.Timestamp("2008-01-16")),
    )
    df, _ = filter_by_price(df)
    df = apply_curcdd_preference(df)
    df = handle_missing_data(df)
    df = clean_categorical_data(df)
    df = calculate_daily_loss_returns(df)
    df = calculate_weekly_loss_returns(df)
    week, day = pivot_data(df)

    assert not day.empty
    assert not week.empty


def test_invalid_schema(invalid_schema_df):
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_data(invalid_schema_df)


def test_invalid_dtypes(invalid_dtypes_df):
    with pytest.raises(TypeError, match="wrong dtype"):
        handle_missing_data(invalid_dtypes_df)


def test_incomplete_date_coverage(incomplete_date_df):
    with pytest.raises(
        ExtractError, match="No stocks have complete date coverage"
    ):  # schema still valid
        get_valid_date_coverage(incomplete_date_df)


def test_low_completeness(low_completeness_df):
    validate_data(low_completeness_df)
    df, dropped = filter_by_price(low_completeness_df)
    assert len(dropped) > 0
    assert df.empty or df.shape[0] < low_completeness_df.shape[0]


def test_missing_prices_fill(valid_df):
    valid_df.loc[0, "prccd"] = np.nan
    df_filled = handle_missing_data(valid_df)
    assert not df_filled["prccd"].isna().any()
