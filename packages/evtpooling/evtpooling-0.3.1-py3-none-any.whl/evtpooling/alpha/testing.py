import numpy as np
import pandas as pd
from scipy.stats import chi2

from evtpooling.utils import get_alpha_var_list


def chenzhou(alpha_list: list[float], common_alpha: float, k_threshold: int) -> tuple[float, float]:
    """
    Perform the Chen & Zhou of common tail indices test to compare a list of Hill estimator values
    against a common alpha.

    Parameters
    ----------
    alpha_list : list[float]
        A list of Hill estimator values (alpha) for different stocks.
    common_alpha : float
        The common alpha value to compare against.
    k_threshold : int
        The number of top losses considered for the Hill estimator calculation.

    Returns
    -------
    tuple
        A tuple containing:
        - chenzhou_statistic: The calculated Chen & Zhou statistic.
        - chenzhou_p_value: The p-value associated with the statistic.
    """
    if common_alpha <= 0:
        raise ValueError("common_alpha must be positive.")

    if len(alpha_list) == 0:
        raise ValueError("alpha_list must not be empty.")

    alpha_array = np.array(alpha_list)
    chenzhou_statistic = np.max(k_threshold * (alpha_array / common_alpha - 1) ** 2)
    x = chenzhou_statistic - 2 * np.log(len(alpha_list)) + np.log(np.log(len(alpha_list)))

    chenzhou_p_value = 1 - np.exp(-(1 / np.sqrt(np.pi)) * np.exp(-x / 2))

    return chenzhou_statistic, chenzhou_p_value


def get_pairwise_df(losses: pd.DataFrame, k_threshold: int) -> pd.DataFrame:
    """
    Calculate the pairwise exceedance probabilities for a DataFrame of losses.
    This function computes the probability that two stocks exceed their respective Value at Risk
    at a given threshold.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.

    Returns
    -------
    pd.DataFrame
        A DataFrame where the index and columns are stock identifiers, and the values are the
        pairwise exceedance probabilities.
    """
    if k_threshold >= losses.shape[0]:
        raise ValueError("k_threshold must be less than the number of observations.")

    df_pairwise = pd.DataFrame()

    losses_dict = {
        col[0] if isinstance(col, tuple) else col: losses[col].dropna() for col in losses.columns
    }

    quantiles = {
        gvkey: get_alpha_var_list(losses1.sort_values(), k_threshold)[1][0]
        for gvkey, losses1 in losses_dict.items()
    }

    gvkeys = list(losses_dict.keys())
    df_pairwise = pd.DataFrame(index=gvkeys, columns=gvkeys)

    for gvkey1 in gvkeys:
        losses1 = losses_dict[gvkey1]
        quant1 = quantiles[gvkey1]

        for gvkey2 in gvkeys:
            losses2 = losses_dict[gvkey2]
            quant2 = quantiles[gvkey2]
            min_len = min(len(losses1), len(losses2))

            exceedances = sum(
                (losses1.iloc[i] > quant1 and losses2.iloc[i] > quant2) for i in range(min_len)
            )
            df_pairwise.loc[gvkey1, gvkey2] = exceedances / k_threshold

    return df_pairwise


def wald_test(
    losses: pd.DataFrame, alpha_list: list[float], common_alpha: float, k_threshold: int
) -> tuple[float, float]:
    """
    Wald test using tail co-exceedance covariance estimator for testing common tail index.

    Parameters
    -----------
    losses : pd.DataFrame
        DataFrame of losses (columns are assets, rows are time).
    alpha_list : list of float
        Tail index estimates (one per asset).
    common_alpha : float
        Hypothesized common tail index (e.g. mean of alpha_list).
    k_threshold : int
        Number of order statistics used.

    Returns
    --------
    wald_statistic : float
        Test statistic.
    wald_p_value : float
        p-value from chi-squared distribution.
    """
    if len(alpha_list) == 0:
        raise ValueError("alpha_list cannot be empty.")
    if common_alpha <= 0:
        raise ValueError("common_alpha must be positive.")
    if k_threshold >= losses.shape[0]:
        raise ValueError("k_threshold must be less than number of observations.")

    alpha_array = np.array(alpha_list)
    zeta = np.sqrt(k_threshold) * (alpha_array / common_alpha - 1)

    # Estimate tail co-exceedance matrix as covariance proxy
    sigma = get_pairwise_df(losses, k_threshold).astype(float).values

    # Force symmetry
    sigma = (sigma + sigma.T) / 2

    # Regularization (optional but helpful if sigma is near-singular)
    eps = 1e-8
    sigma += eps * np.eye(len(sigma))

    try:
        inv_sigma = np.linalg.inv(sigma)
    except np.linalg.LinAlgError as err:
        raise np.linalg.LinAlgError("Covariance matrix is singular, regularization failed") from err

    wald_statistic = zeta.T @ inv_sigma @ zeta
    dof = len(alpha_list) - 1
    wald_p_value = 1 - chi2.cdf(wald_statistic, df=dof)
    wald_p_value = np.clip(wald_p_value, 0, 1)

    return wald_statistic, wald_p_value
