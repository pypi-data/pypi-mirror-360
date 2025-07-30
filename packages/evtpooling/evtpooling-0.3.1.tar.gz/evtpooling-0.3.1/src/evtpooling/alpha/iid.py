import warnings

import pandas as pd
from scipy.stats import jarque_bera
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

from evtpooling.constants import *


def normality_test(
    losses: pd.DataFrame,
    drop: bool = False,
    p_threshold: float = 0.05,
    dict_gvkey_conm: dict[int, str] = None,
) -> None:
    """
    Perform the Jarque-Bera test for normality on each stock's loss series in the DataFrame.
    If the p-value > threshold, the null hypothesis of normality is not rejected.
    Optionally drop the stock from the DataFrame if it fails the test.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
        The DataFrame should have a MultiIndex with stock identifiers as the first level.
    drop : bool, optional
        If True, stocks that fail the normality test will be dropped from the DataFrame.
        Default is False.
    p_threshold : float, optional
        The p-value threshold for the Jarque-Bera test.
    dict_gvkey_conm : dict[int, str], optional
        A dictionary mapping stock identifiers (gvkeys) to company names (conms).
        If provided, the names of companies that fail the test will be printed instead of gvkeys.
        Default is None.

    Returns
    -------
    None
        Prints the list of companies that failed to reject the null hypothesis of normality.
        If `drop` is True, those stocks will also be removed from the DataFrame.
    """
    jb_passed = []

    for stock_id in losses.columns:
        warnings.filterwarnings("ignore")

        if isinstance(stock_id, tuple):
            gvkey, _, _ = stock_id
        else:
            gvkey = stock_id

        stock_clean = losses[stock_id].dropna()

        _, jb_test_pval = jarque_bera(stock_clean)

        if jb_test_pval > p_threshold:
            jb_passed.append(gvkey)
            if drop:
                losses.drop(columns=[stock_id], inplace=True)

    if dict_gvkey_conm is not None:
        jb_passed = [dict_gvkey_conm.get(gvkey, gvkey) for gvkey in jb_passed]

    print(
        f"The following companies failed to reject the null hypothesis "
        f"of normality (p-value > {p_threshold}): {jb_passed}"
    )


def autocorrelation_test(
    losses: pd.DataFrame,
    drop: bool = False,
    p_threshold: float = 0.05,
    dict_gvkey_conm: dict[int, str] = None,
) -> None:
    """
    Performs the Ljung-Box test of no autocorelation.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
        The DataFrame should have a MultiIndex with stock identifiers as the first level.
    drop : bool, optional
        If True, stocks that fail the normality test will be dropped from the DataFrame.
        Default is False.
    p_threshold : float, optional
        The p-value threshold for the Jarque-Bera test.
    dict_gvkey_conm : dict[int, str], optional
        A dictionary mapping stock identifiers (gvkeys) to company names (conms).
        If provided, the names of companies that fail the test will be printed instead of gvkeys.
        Default is None.

    Returns
    -------
    None
        Prints the list of companies that reject the null hypothesis of no autocorrelation.
        If `drop` is True, those stocks will also be removed from the DataFrame.
    """
    lb_failed = []

    for stock_id in losses.columns:
        warnings.filterwarnings("ignore")

        if isinstance(stock_id, tuple):
            gvkey, _, _ = stock_id
        else:
            gvkey = stock_id

        stock_clean = losses[stock_id].dropna()

        res = ARIMA(stock_clean, order=(1, 0, 1)).fit()
        lb_test_pval = (
            acorr_ljungbox(res.resid, lags=[5], return_df=False)["lb_pvalue"].iloc[0].round(2)
        )

        if lb_test_pval < p_threshold:
            lb_failed.append(gvkey)
            if drop:
                losses.drop(columns=[stock_id], inplace=True)

    if dict_gvkey_conm is not None:
        lb_failed = [dict_gvkey_conm.get(gvkey, gvkey) for gvkey in lb_failed]

    print(
        f"The following companies rejected the null hypothesis "
        f"of no autocorrelation (p-value < {p_threshold}): {lb_failed}"
    )


def stationarity_test(
    losses: pd.DataFrame,
    drop: bool = False,
    p_threshold: float = 0.05,
    dict_gvkey_conm: dict[int, str] = None,
) -> None:
    """
    Performs the Augmented Dickey-Fuller test for a unit root.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
        The DataFrame should have a MultiIndex with stock identifiers as the first level.
    drop : bool, optional
        If True, stocks that fail the normality test will be dropped from the DataFrame.
        Default is False.
    p_threshold : float, optional
        The p-value threshold for the Jarque-Bera test.
    dict_gvkey_conm : dict[int, str], optional
        A dictionary mapping stock identifiers (gvkeys) to company names (conms).
        If provided, the names of companies that fail the test will be printed instead of gvkeys.
        Default is None.

    Returns
    -------
    None
        Prints the list of companies that failed to reject the null hypothesis of a unit root.
        If `drop` is True, those stocks will also be removed from the DataFrame.
    """
    adf_failed = []

    for stock_id in losses.columns:
        warnings.filterwarnings("ignore")

        if isinstance(stock_id, tuple):
            gvkey, _, _ = stock_id
        else:
            gvkey = stock_id

        stock_clean = losses[stock_id].dropna()
        adf_test_pval = adfuller(stock_clean)[1]

        if adf_test_pval > p_threshold:
            adf_failed.append(gvkey)
            if drop:
                losses.drop(columns=[stock_id], inplace=True)

        if dict_gvkey_conm is not None:
            adf_failed = [dict_gvkey_conm.get(gvkey, gvkey) for gvkey in adf_failed]

    print(
        f"The following companies failed to reject the null hypothesis "
        f"of a unit root (p-value < {p_threshold}): {adf_failed}"
    )
