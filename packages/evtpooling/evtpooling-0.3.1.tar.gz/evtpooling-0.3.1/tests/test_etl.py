import os
import tempfile

import numpy as np
import pandas as pd
import pytest

from evtpooling import etl_pipeline
from evtpooling.constants import *

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def valid_input_file():
    """Generate a valid temporary input file for ETL pipeline."""
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

    df = pd.DataFrame(
        {
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
            "ISIN": ["AAA"] * 24,
            "costat": ["A"] * 24,
            "ggroup": [10.0] * 24,
            "gind": [100.0] * 24,
            "loc": ["US"] * 24,
        }
    )

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
        file_path = tmp.name
        df.to_csv(file_path, index=False)

    yield file_path

    os.remove(file_path)


# --------------------
# Tests
# --------------------


def test_etl_pipeline_runs(valid_input_file):
    """Test that ETL pipeline runs end-to-end without crashing."""
    result_df = etl_pipeline(
        valid_input_file,
        expected_range=(pd.Timestamp("2008-01-01"), pd.Timestamp("2008-01-16")),
        sheet_name="TestSheet",
    )

    # We simply check that the output is still a dataframe
    assert isinstance(result_df, pd.DataFrame)

    # Optionally: check that the pivot table column name becomes equal to the IDENTIFIER_COLUMNS
    assert list(result_df.columns.names) == IDENTIFIER_COLUMNS


def test_etl_pipeline_invalid_file():
    """Test that ETL pipeline raises error when input file is missing."""
    with pytest.raises(RuntimeError, match="Failed to load file"):
        etl_pipeline("non_existing_file.csv")
