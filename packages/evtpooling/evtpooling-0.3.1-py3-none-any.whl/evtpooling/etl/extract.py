import csv

import chardet
import pandas as pd

from ..constants import *


# Define a custom exception for specific errors if certain
# conditions are not met defined below
class ExtractError(Exception):
    """Custom exception for errors during data extraction."""

    pass


def detect_encoding(file_path: str, sample_size: int = 10000) -> str:
    """
    Detect the encoding of a file using chardet.

    Parameters
    ----------
    file_path : str
        Path to the file for which encoding needs to be detected.
    sample_size : int, optional
        Number of bytes to read for encoding detection. Default is 10000 bytes.

    Returns
    -------
    encoding : str
        Detected encoding of the file. If detection fails, returns 'utf-8'.
    """
    with open(file_path, "rb") as f:
        raw = f.read(sample_size)
    result = chardet.detect(raw)
    encoding = result["encoding"]
    cofindence = result["confidence"]
    print(f"Detected encoding: {encoding} with confidence {cofindence}")

    return encoding or "utf-8"


def detect_csv_seperator(file_path: str, sample_size: int = 10000) -> str:
    """
    Detect the separator used in a CSV file.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.
    sample_size : int, optional
        Number of bytes to read for separator detection. Default is 10000 bytes.

    Returns
    -------
    sep : str
        Detected separator character. If detection fails, returns ','.
    """
    with open(file_path, encoding="utf-8") as f:
        sample = f.read(sample_size)
        try:
            dialect = csv.Sniffer().sniff(sample)
            sep = dialect.delimiter
            print(f"Auto-detected separator: '{sep}'")
            return sep
        except csv.Error:
            print("⚠ Sniffer failed, defaulting to ','")
            return ","


def validate_schema(df: pd.DataFrame, required_columns: list[str]):
    """
    Validate that the DataFrame contains all required columns.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.
    required_columns : list of str
        List of required column names.

    Raises
    ------
    ExtractError
        If any required columns are missing from the DataFrame.
    """
    missing_cols = set(required_columns) - set(df.columns)
    if missing_cols:
        raise ExtractError(f"Missing columns: {missing_cols}")


def basic_data_quality_check(df: pd.DataFrame, price_list: list[str] = None):
    """
    Perform basic data quality checks on the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to check.

    Raises
    ------
    ExtractError
        If any price columns contain negative values or if there are missing values.
    """
    if price_list is None:
        price_list = [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW]

    if df.isnull().any().any():
        print("Warning: Missing values found in the DataFrame.")
    if (df[price_list] < 0).any().any():
        raise ExtractError("Negative prices detected")


def extract_file(
    file_path: str,
    sep_file: str = None,
    parse_dates_file: str = DATE_COLUMN,
    header_excel: int = None,
    sample_size: int = 10000,
    price_list: list = None,
) -> pd.DataFrame:
    """Load a file (csv, xlsx, parquet) into a pandas DataFrame.
    If sep is None for CSV, auto-detect separator.

    Parameters
    ----------
    file_path : str
        Path to the file to be loaded. Supported formats: .csv, .xlsx, .parquet.
        (Default value = None)
    sep : str, optional
        Separator for CSV files. If None, the separator will be auto-detected.
        (Default value = None)
    parse_dates : list of str, optional
        List of column names to parse as dates. If None, no columns are parsed.
        (Default value = None)
    header_excel : int, optional
        Row number to use as the header for Excel files.
        If None, the first row is used.
        (Default value = None)
    sample_size : int, optional
        Number of bytes to read for encoding detection and separator detection.
        (Default value = 10000)
    price_list : list of str, optional
        List of price columns to check for data quality.
        If None, defaults to [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW].
        (Default value = None)

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the loaded data.
    """
    if price_list is None:
        price_list = [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW]

    try:
        enconding_file = detect_encoding(file_path, sample_size=sample_size)

        if file_path.endswith(".csv"):
            if sep_file is None:
                sep_file = detect_csv_seperator(file_path, sample_size=sample_size)
            df = pd.read_csv(
                file_path,
                sep=sep_file,
                parse_dates=[parse_dates_file],
                encoding=enconding_file,
            )

        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, parse_dates=[parse_dates_file], header=header_excel)

        elif file_path.endswith(".parquet"):
            df = pd.read_parquet(file_path)

        else:
            raise ValueError("Unsupported file type.")

        print(f"File loaded successfully: {file_path} with shape {df.shape}")

        df[parse_dates_file] = pd.to_datetime(df[parse_dates_file], errors="coerce")
        if df[parse_dates_file].isnull().any():
            raise ExtractError("Some dates could not be parsed.")

        # Validate all columns are present
        validate_schema(df, REQUIRED_COLUMNS)

        # Basic_data_quality_check
        basic_data_quality_check(df, price_list=price_list)

        return df

    except ExtractError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to load file: {e}") from e
