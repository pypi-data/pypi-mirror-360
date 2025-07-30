import pandas as pd


def export_to_excel(
    df: pd.DataFrame,
    filepath: str,
    sheet_name: str = "Sheet1",
    header: bool = True,
    index: bool = True,
) -> None:
    """
    Exports a DataFrame to an Excel file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to export.
    filepath : str
        The path where the Excel file will be saved.
    sheet_name : str, optional
        The name of the sheet in the Excel file (default is 'Sheet1').
    header : bool, optional
        Whether to write the column names (default is True).
    index : bool, optional
        Whether to write row indices (default is True).

    Returns
    -------
    None
        This function does not return anything. It writes the DataFrame to an Excel file.
    """
    df.to_excel(filepath, sheet_name=sheet_name, header=header, index=index)
    print(f"✅ Excel file written: {filepath}")


def export_to_csv(df: pd.DataFrame, filepath: str, header: bool = True, index: bool = True) -> None:
    """
    Exports a DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to export.
    filepath : str
        The path where the CSV file will be saved.
    header : bool, optional
        Whether to write the column names (default is True).
    index : bool, optional
        Whether to write row indices (default is True).

    Returns
    -------
    None
        This function does not return anything. It writes the DataFrame to a CSV file.
    """
    df.to_csv(filepath, header=header, index=index)
    print(f"✅ CSV file written: {filepath}")


def export_to_parquet(df: pd.DataFrame, filepath: str, index: bool = True) -> None:
    """
    Exports a DataFrame to a Parquet file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to export.
    filepath : str
        The path where the Parquet file will be saved.
    index : bool, optional
        Whether to write row indices (default is True).

    Returns
    -------
    None
        This function does not return anything. It writes the DataFrame to a Parquet file.
    """
    df.to_parquet(filepath, index=index)
    print(f"✅ Parquet file written: {filepath}")


def export_to_pickle(df: pd.DataFrame, filepath: str) -> None:
    """
    Exports a DataFrame to a Pickle file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to export.
    filepath : str
        The path where the Pickle file will be saved.

    Returns
    -------
    None
        This function does not return anything. It writes the DataFrame to a Pickle file.
    """
    df.to_pickle(filepath)
    print(f"✅ Pickle file written: {filepath}")


def load_file(
    df: pd.DataFrame,
    filepath: str,
    file_format: str = "xlsx",
    sheet_name: str = "Sheet1",
    header: bool = True,
    index: bool = True,
) -> pd.DataFrame:
    """
    Loads a DataFrame to a specified file format.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to load.
    filepath : str
        The path where the file will be saved.
    file_format : str, optional
        The format of the file ('xlsx', 'csv', 'parquet', 'pickle').
        Default 'xlsx'.
    sheet_name : str, optional
        Sheet name for Excel files.
    header : bool, optional
        Write column headers.
    index : bool, optional
        Write index columns.

    Returns
    -------
    pd.DataFrame
        The DataFrame that was written.
    """

    if file_format == "xlsx":
        export_to_excel(df, filepath, sheet_name=sheet_name, header=header, index=index)
    elif file_format == "csv":
        export_to_csv(df, filepath, header=header, index=index)
    elif file_format == "parquet":
        export_to_parquet(df, filepath, index=index)
    elif file_format == "pickle":
        export_to_pickle(df, filepath)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    return df
