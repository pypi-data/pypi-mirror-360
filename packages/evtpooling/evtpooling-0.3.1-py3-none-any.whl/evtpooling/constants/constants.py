import numpy as np
import pandas as pd

DATE_COLUMN = "datadate"
PRICE_CLOSE_DAY = "prccd"
PRICE_CLOSE_HIGH = "prchd"
PRICE_CLOSE_LOW = "prcld"
START_DATE = pd.Timestamp("2008-01-04")
END_DATE = pd.Timestamp("2023-12-29")
DEBUG = False

CAT_COLUMNS = ["costat", "ggroup", "gind", "loc"]
EXPECTED_COLUMNS = [
    "gvkey",
    "conm",
    "iid",
    "datadate",
    "curcdd",
    "cshtrd",
    "prccd",
    "prchd",
    "prcld",
    "trfd",
    "isin",
    "costat",
    "ggroup",
    "gind",
    "loc",
]
EXPECTED_COL_TYPES = {
    "gvkey": np.integer,
    "iid": np.object_,
    "datadate": np.datetime64,
    "conm": np.object_,
    "curcdd": np.object_,
    "cshtrd": np.floating,
    "prccd": np.floating,
    "prchd": np.floating,
    "prcld": np.floating,
    "trfd": np.floating,
    "isin": np.object_,
    "costat": np.object_,
    "ggroup": np.floating,
    "gind": np.floating,
    "loc": np.object_,
}
IDENTIFIER_COLUMNS = ["gvkey", "curcdd", "iid"]
REQUIRED_COLUMNS = [
    "gvkey",
    "curcdd",
    "iid",
    "datadate",
    "conm",
    "prccd",
    "prchd",
    "prcld",
]
