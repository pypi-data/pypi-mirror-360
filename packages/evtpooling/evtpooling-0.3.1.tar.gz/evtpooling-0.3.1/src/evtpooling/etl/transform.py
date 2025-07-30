import numpy as np
import pandas as pd
from fuzzywuzzy import process

from ..constants import *


# Define a custom exception for specific errors
# if certain conditions are not met defined below
class ExtractError(Exception):
    """Custom exception for errors during data extraction."""

    pass


def validate_data(
    df: pd.DataFrame,
    required_columns: list[str] = None,
    expected_col_types: dict[str, type] = None,
) -> None:
    """
    Validate the DataFrame against expected columns and types.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to validate.
    expected_col_types : Dict[str, type], optional
        Dictionary mapping column names to expected data types.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    if required_columns is None:
        required_columns = REQUIRED_COLUMNS
    if expected_col_types is None:
        expected_col_types = EXPECTED_COL_TYPES

    # Check for missing columns first
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df.columns = df.columns.str.lower()  # Normalize column names to lowercase

    for col, expected_type in expected_col_types.items():
        if not np.issubdtype(df[col].dtype, expected_type):
            raise TypeError(
                f"Column {col} has wrong dtype: \
                            {df[col].dtype}, expected {expected_type}"
            )

    print("✅ Data validation passed.")


def get_valid_date_coverage(
    df: pd.DataFrame,
    date_column: str = None,
    id_columns: list[str] = None,
    expected_range: tuple[str, str] = None,
) -> tuple[pd.DataFrame, list[tuple]]:
    """
    Filter stocks that have complete date coverage within the expected range.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing stock data.
    date_column : str, optional
        Column name for date. Defaults to DATE_COLUMN.
    id_columns : list[str], optional
        List of identifier columns to group by. Defaults to IDENTIFIER_COLUMNS.
    expected_range : tuple[str, str], optional
        Tuple containing start and end dates as strings.
        Defaults to (START_DATE, END_DATE).

    Returns
    -------
    tuple[pd.DataFrame, list[Tuple]]
        A tuple containing:
        - Filtered DataFrame with valid date coverage.
        - List of dropped stocks with reasons for dropping.
    """
    if date_column is None:
        date_column = DATE_COLUMN
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS
    if expected_range is None:
        expected_range = (START_DATE, END_DATE)

    for col in id_columns + [date_column]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    start_expected = pd.to_datetime(expected_range[0])
    end_expected = pd.to_datetime(expected_range[1])

    df_range = df[(df[date_column] >= start_expected) & (df[date_column] <= end_expected)].copy()

    valid_groups = []
    dropped_stocks = []

    # name is a tuple of id_columns, group is the DataFrame part for that group
    for name, group in df_range.groupby(id_columns):
        min_date = group[date_column].min()
        max_date = group[date_column].max()

        if min_date > start_expected or max_date < end_expected:
            dropped_stocks.append((name, "Date range incomplete"))
        else:
            valid_groups.append(name)

    if not valid_groups:
        print("⚠️ All stocks dropped after date coverage check.")
        raise ExtractError(
            f"No stocks have complete date coverage between {start_expected} and {end_expected}."
        )
    else:
        print("✅ Stocks with valid date coverage found:", len(valid_groups))

    valid_df = df_range[df_range[id_columns].apply(tuple, axis=1).isin(valid_groups)]

    return valid_df, dropped_stocks


def filter_by_price(
    df: pd.DataFrame,
    id_columns: list[str] = None,
    price_columns: list[str] = None,
    threshold_pct: float = 85.0,
) -> tuple[pd.DataFrame, list[tuple]]:
    """
    Filter stocks based on the completeness of price data in specified columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing stock data.
    id_columns : list[str], optional
        List of identifier columns to group by. Defaults to IDENTIFIER_COLUMNS.
    price_columns : list[str], optional
        List of price columns to check for completeness.
        Defaults to [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW].
    threshold_pct : float, optional
        Percentage threshold for completeness. Defaults to 85.0.

    Returns
    -------
    tuple[pd.DataFrame, list[Tuple]]
        A tuple containing:
        - Filtered DataFrame with valid price data.
        - List of dropped stocks with reasons for dropping.
    """
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS
    if price_columns is None:
        price_columns = [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW]

    for col in id_columns + price_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    valid_groups = []
    dropped_stocks = []

    # name is a tuple of id_columns, group is the DataFrame part for that group
    for name, group in df.groupby(id_columns):
        sufficient_data = True
        if len(group) == 0:
            dropped_stocks.append((name, "Empty group"))
            sufficient_data = False
            continue

        for price_col in price_columns:
            completeness = group[price_col].notna().mean() * 100
            if completeness < threshold_pct:
                dropped_stocks.append(
                    (
                        name,
                        f"Insufficient data in{price_col}' ({completeness:.1f}% valid)",
                    )
                )
                sufficient_data = False
                break

        if sufficient_data:
            valid_groups.append(name)

    if not valid_groups:
        print("⚠️ All stocks dropped after completeness check.")
    else:
        print("✅ Stocks with valid price completeness found:", len(valid_groups))

    valid_df = df[df[id_columns].apply(tuple, axis=1).isin(valid_groups)]

    return valid_df, dropped_stocks


def apply_curcdd_preference(
    df: pd.DataFrame,
    id_columns: list[str] = None,
    curcdd_column: str = "curcdd",
    preference: str = "EUR",
    price_columns: list[str] = None,
) -> pd.DataFrame:
    """
    Apply preference for 'curcdd' column to select
    the best stock data based on completeness.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing stock data.
    id_columns : list[str], optional
        List of identifier columns to group by. Defaults to IDENTIFIER_COLUMNS.
    curcdd_column : str, optional
        Column name for currency code. Defaults to 'curcdd'.
    preference : str, optional
        Preferred currency code to filter by. Defaults to 'EUR'.
    price_columns : list[str], optional
        List of price columns to check for completeness.
        Defaults to [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW].

    Returns
    -------
    pd.DataFrame
        DataFrame with the best stock data based on
        completeness and currency preference.
    """
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS
    if price_columns is None:
        price_columns = [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW]

    required_columns = id_columns + price_columns
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    completeness_records = []

    # name is a tuple of id_columns, group is the DataFrame part for that group
    for name, group in df.groupby(id_columns):
        completeness_scores = [group[price_col].notna().mean() * 100 for price_col in price_columns]
        avg_completeness = sum(completeness_scores) / len(completeness_scores)
        completeness_records.append(
            {
                "gvkey": name[0],
                "curcdd": name[1],
                "iid": name[2],
                "completeness": avg_completeness,
            }
        )

    completeness_df = pd.DataFrame(completeness_records)

    # Sort logic: prefer EUR, then highest completeness
    completeness_df["curcdd_preference"] = completeness_df[curcdd_column].ne(preference)
    completeness_df.sort_values(
        by=["gvkey", "curcdd_preference", "completeness"],
        ascending=[True, True, False],
        inplace=True,
    )

    # Select one per (gvkey, iid)
    best_per_gvkey_iid = completeness_df.groupby(["gvkey"]).first().reset_index()

    if best_per_gvkey_iid.empty:
        print("⚠️ No valid groups remaining after curcdd preference applied.")
    else:
        print(
            "✅ Best groups selected based on curcdd preference and completeness:",
            len(best_per_gvkey_iid),
        )

    valid_groups = list(best_per_gvkey_iid[id_columns].itertuples(index=False, name=None))
    final_df = df[df[id_columns].apply(tuple, axis=1).isin(valid_groups)]

    return final_df


def handle_missing_data(
    df: pd.DataFrame, price_list: list[str] = None, id_columns: list[str] = None
) -> pd.DataFrame:
    """
    Handle missing dates in the price columns by filling NaN values with the mean of the group.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the price data.
    price_list : list[str], optional
        List of price columns to fill NaN values for.
    id_columns : list[str], optional
        List of identifier columns to group by when filling NaN values.

    Raises
    ------
    ValueError
        If any required price column is missing from the DataFrame
        or if any identifier column is missing.
    TypeError
        If any price column has a dtype that is not float.

    Returns
    -------
    pd.DataFrame
        DataFrame with NaN values in price columns filled with the mean of the group.
    """

    if price_list is None:
        price_list = [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW]
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS

    # Check identifier columns first
    missing_id_cols = [col for col in id_columns if col not in df.columns]
    if missing_id_cols:
        raise ValueError(f"Missing required identifier columns: {missing_id_cols}")

    for price_col in price_list:
        if price_col not in df.columns:
            raise ValueError(f"Missing required column: {price_col}")

        if not np.issubdtype(df[price_col].dtype, np.floating):
            raise TypeError(
                f"Column {price_col} has wrong dtype: \
                            {df[price_col].dtype}, expected float type"
            )

        df[price_col] = df.groupby(id_columns)[price_col].transform(lambda x: x.fillna(x.mean()))

    return df


def extract_clean_categories(
    df: pd.DataFrame, column: str, threshold_pct_cat: float = 1.0
) -> list[str]:
    """
    Extracts frequent categories from a column by removing
    categories below the threshold percentage.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    column : str
        Column name to analyze.
    threshold_pct : float, optional
        Threshold percentage (0-100) below which categories
        are considered rare.

    Returns
    -------
    list[str]
        List of frequent category labels.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataframe.")

    percentage = df[column].value_counts(normalize=True) * 100
    frequent_categories = percentage[percentage >= threshold_pct_cat].index.tolist()
    frequent_categories = sorted(frequent_categories)

    return frequent_categories


def comparing_categories(
    dirty_cat_list: pd.Series, clean_cat_list: list[str], threshold: int = 80
) -> None:
    """
    Compare dirty category names with clean category names and replace them based on a threshold.

    Parameters
    ----------
    dirty_cat_list : pd.Series
        Series containing the dirty category names.
    clean_cat_list : pd.Series
        Series containing the clean category names.
    threshold : int, optional
        The minimum similarity score for a match to be considered valid. Default is 80.

    Returns
    -------
    None
        The function modifies the dirty_cat_list in place.
    """
    unique_dirty = dirty_cat_list.astype(str).unique()
    for cat_clean in clean_cat_list:
        matches = process.extract(cat_clean, unique_dirty, limit=len(unique_dirty))

        for potential_matches in matches:
            if potential_matches[1] >= threshold:
                dirty_cat_list.loc[dirty_cat_list == potential_matches[0]] = cat_clean


def clean_categorical_data(df: pd.DataFrame, cat_columns: list[str] = None) -> pd.DataFrame:
    """
    Clean categorical data in the DataFrame by:
    - Stripping whitespace
    - Converting to uppercase
    - Removing non-alphanumeric characters
    - Extracting frequent categories based on a threshold percentage
    - Comparing and replacing dirty categories with clean categories based on a similarity threshold

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing categorical columns to be cleaned.
    cat_columns : list[str], optional
        List of categorical columns to clean. If None, defaults to CAT_COLUMNS.

    Returns
    -------
    pd.DataFrame
        The DataFrame with cleaned categorical columns.
    """
    if cat_columns is None:
        cat_columns = CAT_COLUMNS

    for col in cat_columns:
        df[col] = (
            df[col].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
        )
        clean_cat_list = extract_clean_categories(df, col, threshold_pct_cat=1.0)
        col_series = df[col].copy()  # Safer to work on a copy to avoid modifying the original data
        comparing_categories(col_series, pd.Series(clean_cat_list), threshold=80)
        df[col] = col_series.astype("category")

    return df


def calculate_daily_loss_returns(
    df: pd.DataFrame, returns: str = None, id_columns: list[str] = None
) -> pd.DataFrame:
    """
    Calculate percentage loss returns for a given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing price data.
    returns : str, optional
        The column name for returns calculation. Defaults to PRICE_CLOSE_DAY.
    id_columns : list[str], optional
        List of identifier columns to group by when calculating returns.
        Defaults to IDENTIFIER_COLUMNS.

    Returns
    -------
    pd.DataFrame
        The DataFrame with a new column for percentage loss returns.
    """
    if returns is None:
        returns = PRICE_CLOSE_DAY
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS

    if returns not in df.columns:
        raise ValueError(f"Missing column: {returns}")
    if not np.issubdtype(df[returns].dtype, np.floating):
        raise TypeError(f"Column {returns} must be numeric")

    df["daily_loss_returns"] = -df.groupby(id_columns)[returns].pct_change().fillna(0) * 100

    return df


def calculate_weekly_loss_returns(
    df: pd.DataFrame,
    date_column: str = None,
    returns: str = None,
    id_columns: list[str] = None,
    lag_days: int = 5,
) -> pd.DataFrame:
    """
    Calculate weekly loss returns for a given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing price data.
    date_column : str, optional
        The column name for date. Defaults to DATE_COLUMN.
    returns : str, optional
        The column name for returns calculation. Defaults to PRICE_CLOSE_DAY.
    id_columns : list[str], optional
        List of identifier columns to group by when calculating returns.
        Defaults to IDENTIFIER_COLUMNS.
    lag_days : int, optional
        Number of days to lag the anchor close price. Defaults to 5.

    Returns
    -------
    pd.DataFrame
        The DataFrame with a new column for weekly loss returns.
    """
    if date_column is None:
        date_column = DATE_COLUMN
    if returns is None:
        returns = PRICE_CLOSE_DAY
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS

    # Column existence checks
    for col in id_columns + [returns, date_column]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    df_copy = df.copy()
    first_day_per_stock = df_copy.groupby(id_columns)[date_column].transform("first")
    df_copy["is_anchor_day"] = df_copy[date_column].dt.weekday == first_day_per_stock.dt.weekday
    df_copy["anchor_close"] = df_copy[returns].where(df_copy["is_anchor_day"])
    df_copy["lagged_anchor_close"] = df_copy.groupby(id_columns)["anchor_close"].transform(
        lambda x: x.shift(lag_days)
    )
    df["weekly_loss_returns"] = (
        -((df_copy[returns] - df_copy["lagged_anchor_close"]) / df_copy["lagged_anchor_close"])
        * 100
    )

    return df


def pivot_data(
    df: pd.DataFrame, date_column=None, id_columns=None, pivot_column=None
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Pivot the DataFrame to create weekly and daily loss returns tables.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing loss returns data.
    date_column : str, optional
        The column name for date. Defaults to DATE_COLUMN.
    id_columns : list[str], optional
        List of identifier columns to pivot by. Defaults to IDENTIFIER_COLUMNS.
    pivot_column : str, optional
        The column name to pivot on. Defaults to the first identifier column in id_columns.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        A tuple containing:
        - DataFrame with weekly loss returns pivoted by date and identifier.
        - DataFrame with daily loss returns pivoted by date and identifier.
    """
    if date_column is None:
        date_column = DATE_COLUMN
    if id_columns is None:
        id_columns = IDENTIFIER_COLUMNS
    if pivot_column is None:
        pivot_column = id_columns

    # Safety: Check columns exist
    required_columns = [date_column, "daily_loss_returns", "weekly_loss_returns"] + (
        pivot_column if isinstance(pivot_column, list) else [pivot_column]
    )
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Ensure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])

    losses_week = df.pivot_table(
        values="weekly_loss_returns", index=date_column, columns=pivot_column
    )
    losses_day = df.pivot_table(
        values="daily_loss_returns", index=date_column, columns=pivot_column
    )

    # OPTIONAL: Sort the values in each column for better readability
    # losses_week_dict_sorted = {col: losses_week[col].dropna().sort_values()
    #                            for col in losses_week.columns}
    # losses_day_dict_sorted = {col: losses_day[col].dropna().sort_values()
    #                           for col in losses_day.columns}

    return losses_week, losses_day


def transform_data(df: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full master transform function for entire ETL pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing stock data.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame]
        A tuple containing:
        - DataFrame with weekly loss returns.
        - DataFrame with daily loss returns.
    """
    # 1️⃣ Validate schema
    validate_data(
        df,
        required_columns=kwargs["required_columns"],
        expected_col_types=kwargs["expected_col_types"],
    )

    # 2️⃣ Date coverage
    df, dropped_dates = get_valid_date_coverage(
        df,
        date_column=kwargs["date_column"],
        id_columns=kwargs["id_columns"],
        expected_range=kwargs["expected_range"],
    )

    # 3️⃣ Price completeness
    df, dropped_completeness = filter_by_price(
        df,
        id_columns=kwargs["id_columns"],
        price_columns=kwargs["price_columns"],
        threshold_pct=kwargs["threshold_pct"],
    )

    # 4️⃣ Currency preference
    df = apply_curcdd_preference(
        df,
        id_columns=kwargs["id_columns"],
        curcdd_column=kwargs["curcdd_column"],
        preference=kwargs["preference"],
        price_columns=kwargs["price_columns"],
    )

    # 5️⃣ Handle missing data
    df = handle_missing_data(df, price_list=kwargs["price_list"], id_columns=kwargs["id_columns"])

    # 6️⃣ Clean categoricals
    df = clean_categorical_data(df, cat_columns=kwargs["cat_columns"])

    # 7️⃣ Daily returns
    df = calculate_daily_loss_returns(
        df, returns=kwargs["returns"], id_columns=kwargs["id_columns"]
    )

    # 8️⃣ Weekly returns
    df = calculate_weekly_loss_returns(
        df,
        date_column=kwargs["date_column"],
        returns=kwargs["returns"],
        id_columns=kwargs["id_columns"],
        lag_days=kwargs["lag_days"],
    )

    # 9️⃣ Pivot final result
    losses_week, losses_day = pivot_data(
        df,
        date_column=kwargs["date_column"],
        id_columns=kwargs["id_columns"],
        pivot_column=kwargs["pivot_column"],
    )

    return losses_week, losses_day
