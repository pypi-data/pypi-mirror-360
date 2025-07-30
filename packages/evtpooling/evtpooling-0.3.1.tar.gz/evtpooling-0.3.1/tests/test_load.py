import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from evtpooling.etl.load import (
    export_to_csv,
    export_to_excel,
    export_to_parquet,
    export_to_pickle,
    load_file,
)

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def sample_df():
    """Sample dataframe for testing export functions."""
    return pd.DataFrame({"A": np.arange(5), "B": list("abcde"), "C": np.random.rand(5)})


# --------------------
# Tests
# --------------------


def test_export_to_excel(sample_df):
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        filepath = tmp.name

    export_to_excel(sample_df, filepath)
    loaded_df = pd.read_excel(filepath, index_col=0)

    pd.testing.assert_frame_equal(sample_df, loaded_df)
    os.remove(filepath)


def test_export_to_csv(sample_df):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        filepath = tmp.name

    export_to_csv(sample_df, filepath)
    loaded_df = pd.read_csv(filepath, index_col=0)

    # CSV loses index by default, so reset index for comparison
    pd.testing.assert_frame_equal(sample_df.reset_index(drop=True), loaded_df)
    os.remove(filepath)


def test_export_to_parquet(sample_df):
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
        filepath = tmp.name

    export_to_parquet(sample_df, filepath)
    loaded_df = pd.read_parquet(filepath)

    pd.testing.assert_frame_equal(sample_df, loaded_df)
    os.remove(filepath)


def test_export_to_pickle(sample_df):
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
        filepath = tmp.name

    export_to_pickle(sample_df, filepath)
    loaded_df = pd.read_pickle(filepath)

    pd.testing.assert_frame_equal(sample_df, loaded_df)
    os.remove(filepath)


# Loop over these argument combinations and run the test function for each combination.
@pytest.mark.parametrize(
    "file_format, suffix",
    [
        ("xlsx", ".xlsx"),
        ("csv", ".csv"),
        ("parquet", ".parquet"),
        ("pickle", ".pkl"),
    ],
)
def test_load_file(sample_df, file_format, suffix):
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        filepath = tmp.name

    load_file(sample_df, filepath, file_format=file_format)

    if file_format == "xlsx":
        loaded_df = pd.read_excel(filepath, index_col=0)
    elif file_format == "csv":
        loaded_df = pd.read_csv(filepath, index_col=0)
        pd.testing.assert_frame_equal(sample_df.reset_index(drop=True), loaded_df)
        os.remove(filepath)
        return
    elif file_format == "parquet":
        loaded_df = pd.read_parquet(filepath)
    elif file_format == "pickle":
        loaded_df = pd.read_pickle(filepath)

    pd.testing.assert_frame_equal(sample_df, loaded_df)
    os.remove(filepath)


def test_load_file_invalid_format(sample_df):
    with tempfile.NamedTemporaryFile(suffix=".dummy", delete=False) as tmp:
        filepath = tmp.name

    with pytest.raises(ValueError, match="Unsupported file format"):
        load_file(sample_df, filepath, file_format="dummy")

    os.remove(filepath)
