import numpy as np
import pandas as pd


def calculate_alpha_var(
    losses: pd.Series,
    k_threshold: int,
    threshold: float = 0.99,
    alpha_hat: float = None,
) -> tuple[float, float]:
    """
    Calculate the Hill estimator and Value at Risk (VaR) for given losses.

    Parameters
    ----------
    losses : pd.Series
        A pandas Series containing the loss values.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.
    threshold : float
        The threshold for the Value at Risk calculation, typically between 0 and 1.

    Returns
    -------
    tuple
        A tuple containing:
        - alpha_hat: The Hill estimator value.
        - var_hat: The Value at Risk estimate.
    """
    losses = losses.dropna().sort_values()

    if alpha_hat is None:
        top_k_logs = np.log(losses.iloc[-k_threshold:])  # Log of the largest k values
        log_x_nk = np.log(losses.iloc[-k_threshold - 1])  # Log of the (k+1)-th largest value
        alpha_hat = 1 / (np.mean(top_k_logs) - log_x_nk)  # Hill estimator

    var_hat = losses.iloc[-k_threshold] * (k_threshold / (len(losses) * (1 - threshold))) ** (
        1 / alpha_hat
    )

    return alpha_hat, var_hat


def get_alpha_var_list(
    losses: pd.Series, k_values: np.ndarray | int, threshold: float = 0.99
) -> tuple[list[float], list[float]]:
    """
    Calculate the Hill estimator and Value at Risk (VaR) for given losses.

    Parameters
    ----------
    losses : pd.Series
        A pandas Series containing the loss values.
    k_values : list
        A list of integers representing the range of threshold to compute the Hill estimator.
    threshold : float
        The threshold for the Value at Risk calculation, typically between 0 and 1.

    Returns
    --------
    tuple
        A tuple containing two lists:
        - alpha_hat_list: The Hill estimator values for each k in k_values.
        - var_hat_list: The corresponding Value at Risk estimates.
    """
    # Initialize the list to store the sorted values
    var_hat_list = []
    alpha_hat_list = []

    if isinstance(k_values, int):
        k_values = [k_values]

    for k in k_values:
        alpha_hat, var_hat = calculate_alpha_var(losses, k, threshold)
        alpha_hat_list.append(alpha_hat)
        var_hat_list.append(var_hat)

    return alpha_hat_list, var_hat_list


def get_alpha_dict(losses: pd.DataFrame, k_threshold: int) -> dict[int:float]:
    """
    Calculate the Hill estimator (alpha) for each column in a DataFrame of losses.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.

    Returns
    -------
    dict
        A dictionary where keys are stock identifiers and values are the Hill estimator values.
    """
    if k_threshold >= losses.shape[0]:
        raise ValueError("k_threshold must be less than the number of observations.")

    alpha_dict = {}

    for losses_id in losses.columns:
        losses_clean = losses[losses_id].dropna().sort_values()
        alpha_hat, _ = get_alpha_var_list(losses_clean, k_threshold)

        if isinstance(losses_id, tuple):
            losses_id_dict = losses_id[0]
        else:
            losses_id_dict = losses_id
        alpha_dict[losses_id_dict] = float(alpha_hat[0])

    return alpha_dict


def get_var_dict(losses: pd.DataFrame, k_threshold: int) -> dict[int:float]:
    """
    Calculate the Value at Risk (VaR) for each column in a DataFrame of losses.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing multiple series of loss values, indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the VaR calculation.

    Returns
    -------
    dict
        A dictionary where keys are stock identifiers and values are the VaR estimates.
    """
    if k_threshold >= losses.shape[0]:
        raise ValueError("k_threshold must be less than the number of observations.")

    var_dict = {}

    for losses_id in losses.columns:
        losses_clean = losses[losses_id].dropna().sort_values()
        _, var_hat = get_alpha_var_list(losses_clean, k_threshold)

        if isinstance(losses_id, tuple):
            losses_id_dict = losses_id[0]
        else:
            losses_id_dict = losses_id
        var_dict[losses_id_dict] = float(var_hat[0])

    return var_dict
