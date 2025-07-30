import logging
import os

import pandas as pd

from ..constants import *
from .extract import extract_file
from .load import load_file
from .transform import transform_data

logger = logging.getLogger(__name__)


def etl_pipeline(
    file_path: str,
    return_week_data: bool = True,
    return_day_data: bool = False,
    save_file: bool = False,
    **kwargs,
) -> pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]:
    """
    ETL pipeline to extract, transform, and load data from a file.

    Parameters
    ----------
    file_path : str
        Path to the input file.
    return_week_data : bool, optional
        If True, returns the weekly data. Default is True.
    return_day_data : bool, optional
        If True, returns the daily data. Default is False.
    save_file : bool, optional
        If True, saves the transformed data to files. Default is False.
    **kwargs : dict
        Additional parameters for extraction and transformation.

    Returns
    -------
    pd.DataFrame | tuple[pd.DataFrame, pd.DataFrame]
        Returns the transformed weekly and/or daily data as DataFrames.
        If both are requested, returns a tuple of (weekly_data, daily_data).
        If neither is requested, returns an empty DataFrame.
    """
    try:
        unexpected_keys = set(kwargs) - ALL_ALLOWED_KWARGS
        if unexpected_keys:
            raise ValueError(f"Unexpected keyword argument(s): {unexpected_keys}")

        # Merge default etl kwargs with user kwargs
        extract_kwargs = {k: kwargs[k] for k in DEFAULT_EXTRACT_KWARGS if k in kwargs}
        extract_final = DEFAULT_EXTRACT_KWARGS.copy()
        extract_final.update(extract_kwargs)

        transform_kwargs = {k: kwargs[k] for k in DEFAULT_TRANSFORM_KWARGS if k in kwargs}
        transform_final = DEFAULT_TRANSFORM_KWARGS.copy()
        transform_final.update(transform_kwargs)

        load_kwargs = {k: kwargs[k] for k in DEFAULT_LOAD_KWARGS if k in kwargs}
        load_final = DEFAULT_LOAD_KWARGS.copy()
        load_final.update(load_kwargs)

        # Extract, transform, and load data
        raw_stock_data = extract_file(file_path, **extract_final)
        clean_data_week, clean_data_day = transform_data(raw_stock_data, **transform_final)
        directory = os.path.dirname(file_path)

        # Save files if requested
        if save_file:
            if return_week_data:
                week_filepath = os.path.join(directory, "losses_week.xlsx")
                load_file(clean_data_week, week_filepath)
            if return_day_data:
                day_filepath = os.path.join(directory, "losses_day.xlsx")
                load_file(clean_data_day, day_filepath)

        logging.info("Successfully extracted, transformed and loaded data.")

        # Determine what to return
        results = []
        if return_week_data:
            results.append(clean_data_week)
        if return_day_data:
            results.append(clean_data_day)

        if len(results) == 1:
            return results[0]
        elif results:
            return tuple(results)
        else:
            return pd.DataFrame()  # fallback: return empty DataFrame if both are False
    # Handle exceptions, log messages
    except Exception as e:
        logging.error(f"Pipeline failed with error: {e}")
        raise


# Configure logging ONLY when run directly (not when imported)
if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
    )
