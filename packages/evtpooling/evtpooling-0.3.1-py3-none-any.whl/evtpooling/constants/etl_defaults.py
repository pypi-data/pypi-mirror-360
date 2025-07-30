from .constants import *

# Default kwargs for each transform function
DEFAULT_EXTRACT_KWARGS = {
    "sample_size": 10000,
    "sep_file": None,
    "parse_dates_file": DATE_COLUMN,
    "header_excel": None,
    "price_list": [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW],
}

DEFAULT_TRANSFORM_KWARGS = {
    "required_columns": REQUIRED_COLUMNS,
    "expected_col_types": EXPECTED_COL_TYPES,
    "date_column": DATE_COLUMN,
    "id_columns": IDENTIFIER_COLUMNS,
    "expected_range": (START_DATE, END_DATE),
    "price_columns": [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW],
    "threshold_pct": 85.0,
    "curcdd_column": "curcdd",
    "preference": "EUR",
    "price_list": [PRICE_CLOSE_DAY, PRICE_CLOSE_HIGH, PRICE_CLOSE_LOW],
    "cat_columns": CAT_COLUMNS,
    "returns": PRICE_CLOSE_DAY,
    "lag_days": 5,
    "pivot_column": IDENTIFIER_COLUMNS,
}

DEFAULT_LOAD_KWARGS = {
    "sheet_name": "Sheet1",
    "header": True,
    "index": True,
    "file_format": "xlsx",
}

ALL_ALLOWED_KWARGS = (
    set(DEFAULT_EXTRACT_KWARGS) | set(DEFAULT_TRANSFORM_KWARGS) | set(DEFAULT_LOAD_KWARGS)
)
