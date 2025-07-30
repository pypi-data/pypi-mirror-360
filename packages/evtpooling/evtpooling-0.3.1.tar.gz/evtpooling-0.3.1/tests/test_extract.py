import os
import tempfile

import pandas as pd
import pytest

from evtpooling import extract_file
from evtpooling.constants import *
from evtpooling.etl.extract import ExtractError

# Dynamically build header from EXPECTED_COLUMNS
CSV_HEADER = ",".join(EXPECTED_COLUMNS)

# ---------------------------
# Fixtures (test input files)
# ---------------------------


# This tells pytest to create a TEMPORARY CSV file with valid data such that
# it automatically generates it into my test functions
@pytest.fixture
def valid_csv_file():
    content = f"""{CSV_HEADER}
1,CompanyA,IID1,2024-01-01,USD,1000,105,110,90,1.02,US000001,A,10,100,US
1,CompanyB,IID2,2024-01-02,USD,1500,110,115,95,1.05,US000002,A,11,101,GB
"""
    # Create a temporary physical file, make it look like a CSV file, and ensure file survices
    # after with block but then is deleted afterwards
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        f.write(content)
        f.seek(0)
        yield f.name  # yield allows the function to continue instead of return
    os.remove(f.name)


@pytest.fixture
def invalid_schema_csv_file():
    # Remove 'cshtrd' to break schema
    partial_columns = [col for col in REQUIRED_COLUMNS if col != "prcld"]
    header = ",".join(partial_columns)

    content = f"""{header}
1,EUR,IID1,2024-01-01,randomA,110,90
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        f.write(content)
        f.seek(0)
        yield f.name
    os.remove(f.name)


@pytest.fixture
def invalid_date_csv_file():
    content = f"""{CSV_HEADER}
1,CompanyA,IID1,INVALID_DATE,USD,1000,105,110,90,1.02,US000001,A,10,100,US
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        f.write(content)
        f.seek(0)
        yield f.name
    os.remove(f.name)


@pytest.fixture
def negative_price_csv_file():
    content = f"""{CSV_HEADER}
1,CompanyA,IID1,2024-01-01,USD,1000,-105,110,90,1.02,US000001,A,10,100,US
"""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        f.write(content)
        f.seek(0)
        yield f.name
    os.remove(f.name)


# ---------------------------
# Tests
# ---------------------------


def test_valid_csv_file(valid_csv_file):
    df = extract_file(valid_csv_file, parse_dates_file=DATE_COLUMN)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, len(EXPECTED_COLUMNS))
    # Verify that datadate is a pandas datetime dtype like datetime64[ns],
    # datetime64[ns, tz], datetime64[ns, UTC]
    assert pd.api.types.is_datetime64_any_dtype(df[DATE_COLUMN])


def test_invalid_schema_csv_file(invalid_schema_csv_file):
    # match argument makes sure the error message contains "Missing columns"
    with pytest.raises(ExtractError, match="Missing columns"):
        extract_file(invalid_schema_csv_file, parse_dates_file=DATE_COLUMN)


def test_invalid_date_csv_file(invalid_date_csv_file):
    with pytest.raises(ExtractError, match="could not be parsed"):
        extract_file(invalid_date_csv_file, parse_dates_file=DATE_COLUMN)


def test_negative_price_csv_file(negative_price_csv_file):
    with pytest.raises(ExtractError, match="Negative prices detected"):
        extract_file(negative_price_csv_file, parse_dates_file=DATE_COLUMN)
