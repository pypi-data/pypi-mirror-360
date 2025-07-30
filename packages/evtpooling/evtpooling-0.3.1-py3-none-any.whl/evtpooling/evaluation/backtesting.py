import numpy as np
import pandas as pd
from scipy.stats import norm


def basel_backtesting(
    losses: pd.DataFrame, var_dict: dict[int:float] | dict[tuple:float], confidence: float = 0.99
) -> pd.DataFrame:
    """
    Perform Basel backtesting on a DataFrame of losses against a dictionary of VaR thresholds.
    This function counts the number of violations for each stock and determines the zone
    based on the number of violations relative to the expected number of violations.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing loss values for different stocks,
        indexed by stock identifiers.
    var_dict : dict[int:float] | dict[tuple:float]
        A dictionary where keys are stock identifiers (or tuples of identifiers)
        and values are the corresponding Value at Risk (VaR) thresholds.
    confidence : float, optional
        The confidence level for the Value at Risk calculation, default is 0.99.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the count of violations and the corresponding zone for each stock.
        The zones are categorized as 'green', 'yellow', or 'red' based on the number of violations.
    """
    violation_counts = pd.Series(
        {col: (losses[col].dropna() > var_dict[col]).sum() for col in losses.columns}
    )
    var_col = pd.Series({col: var_dict[col] for col in losses.columns if col in var_dict})

    def determine_zone(
        violation_count: int,
        num_observations: int,
        threshold: float = 0.99,
    ) -> str:
        """
        Determine the zone based on the violation count and number of observations.
        """
        mean = num_observations * (1 - threshold)
        std_dev = np.sqrt(num_observations * threshold * (1 - threshold))

        green_zone_num = int(norm.ppf(0.95) * std_dev + mean)
        red_zone_num = int(norm.ppf(0.99) * std_dev + mean)

        if violation_count <= green_zone_num:
            return "green"
        elif violation_count <= red_zone_num:
            return "yellow"
        else:
            return "red"

    zones = pd.Series(
        {
            col: determine_zone(violation_count, losses[col].dropna().shape[0], confidence)
            for col, violation_count in violation_counts.items()
        }
    )

    violation_df = pd.DataFrame(
        {"VaR": var_col, "violation_count": violation_counts, "zone": zones}
    )
    violation_df["zone"] = violation_df["zone"].astype("category")
    violation_df["zone"] = violation_df["zone"].cat.set_categories(
        ["green", "yellow", "red"], ordered=True
    )

    return violation_df.sort_values(by="zone")


def sener_backtesting(
    losses: pd.DataFrame, var_dict: dict[int:float] | dict[tuple:float], theta: float
) -> pd.DataFrame:
    """
    Compute the Sener backtesting penalty for a DataFrame of
    losses against a dictionary of VaR thresholds.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing loss values for different stocks,
        indexed by stock identifiers.
    var_dict : dict[int:float] | dict[tuple:float]
        A dictionary where keys are stock identifiers (or tuples of identifiers)
        and values are the corresponding Value at Risk (VaR) thresholds.
    theta : float
        A weighting factor between 0 and 1 that determines the balance
        between violation space measure and safe space measure.

    Returns
    -------
    tuple[list[float], list[float]]
        A tuple containing two lists:
        - Individual penalties for each stock.
        - Aggregate penalty across all stocks.
        Each penalty is a tuple of (violation space measure, safe space measure).
    """

    def compute_violation_penalty(losses: pd.Series, var: float) -> float:
        # Step 1: compute violations
        losses_reset = losses.reset_index(drop=True)
        epsilon = losses_reset - var
        epsilon[epsilon <= 0] = np.nan

        # Step 2: find clusters of consecutive violations
        violations = epsilon.dropna()
        violation_indices = violations.index

        clusters = []
        current_cluster = []

        for _, idx in enumerate(violation_indices):
            if not current_cluster:
                current_cluster.append(idx)
            elif idx == current_cluster[-1] + 1:
                current_cluster.append(idx)
            else:
                clusters.append(current_cluster)
                current_cluster = [idx]
        if current_cluster:
            clusters.append(current_cluster)

        # Step 3: compute C_r for each cluster
        cluster_list = []
        for cluster in clusters:
            eps = epsilon.loc[cluster].values
            c_r = np.prod(1 + eps) - 1
            cluster_list.append((cluster[0], c_r, eps))  # store first index for timing

        # Step 4: compute Phi
        phi = 0
        h = len(cluster_list)
        for r in range(h - 1):
            t_r, c_r, eps_r = cluster_list[r]
            for s in range(1, h - r):
                t_rs, _, eps_rs = cluster_list[r + s]
                k = t_rs - t_r
                prod = (np.prod(1 + eps_r) * np.prod(1 + eps_rs)) - 1
                phi += prod / k

        return phi

    def compute_safe_penalty(losses: pd.Series, var: float) -> float:
        return np.sum(var - losses[(losses < var) & (losses > 0)])

    indiv_penalty_list = []
    agg_penalty_list = []

    for col in losses.columns:
        var_col = var_dict.get(col, float("inf"))
        indiv_penalty_list.append(
            (
                compute_violation_penalty(losses[col], var_col),
                compute_safe_penalty(losses[col], var_col),
            )
        )
        agg_penalty_list.append(
            theta * compute_violation_penalty(losses[col], var_col)
            + (1 - theta) * compute_safe_penalty(losses[col], var_col)
        )

    var_col = pd.Series({col: var_dict[col] for col in losses.columns if col in var_dict})
    violation_df = pd.DataFrame(
        {
            "VaR": var_col,
            "violation_penalty": [vio for vio, _ in indiv_penalty_list],
            "safe_penalty": [safe for _, safe in indiv_penalty_list],
            "agg_penalty": agg_penalty_list,
        }
    )

    return violation_df


def dm_test(
    losses: pd.DataFrame,
    var_dict1: dict[int:float] | dict[tuple:float],
    var_dict2: dict[int:float] | dict[tuple:float],
) -> pd.DataFrame:
    """
    Perform the Diebold-Mariano test to compare two VaR models based on their loss distributions.
    Note that the var_dict1 is the benchmark model and var_dict2 is the alternative model and
    this function assumes an alternative hypothesis that the second model is better than the first.

    Parameters
    ----------
    losses : pd.DataFrame
        A pandas DataFrame containing loss values for different stocks,
        indexed by stock identifiers.
    var_dict1 : dict[int:float] | dict[tuple:float]
        A dictionary where keys are stock identifiers (or tuples of identifiers)
        and values are the corresponding Value at Risk (VaR) thresholds for the first model.
    var_dict2 : dict[int:float] | dict[tuple:float]
        A dictionary where keys are stock identifiers (or tuples of identifiers)
        and values are the corresponding Value at Risk (VaR) thresholds for the second model.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the results of the Diebold-Mariano test, including:
        - VaR1: VaR thresholds from the first model.
        - VaR2: VaR thresholds from the second model.
        - DM_stat: Diebold-Mariano statistic for each stock.
        - p_value: p-value for the DM statistic.
        - differential_mean: Mean of the loss differences.
        - differential_std: Standard deviation of the loss differences.
    """
    # Validate inputs
    if not set(var_dict1) == set(var_dict2):
        raise KeyError("Both VaR dictionaries must have the same keys.")

    dm_stat_list, p_value_list, loss_mean_list, loss_std_list = [], [], [], []

    for stock in losses:
        clean_stock = losses.loc[losses[stock] > 0, stock].dropna()

        if clean_stock.empty:
            raise ValueError(f"Losses for {stock.name} contain no positive values.")

        var_col1 = var_dict1.get(losses[stock].name, float("inf"))
        var_col2 = var_dict2.get(losses[stock].name, float("inf"))

        loss1 = [
            (loss - var_col1) ** 2 if loss >= var_col1 else var_col1 - loss for loss in clean_stock
        ]
        loss2 = [
            (loss - var_col2) ** 2 if loss >= var_col2 else var_col2 - loss for loss in clean_stock
        ]

        loss_diff = np.array(loss1) - np.array(loss2)
        loss_mean = np.mean(loss_diff)
        loss_std = np.std(loss_diff, ddof=1)

        if loss_std == 0:
            dm_stat = float("inf")  # Handle case where std is zero
        else:
            dm_stat = loss_mean / loss_std
            f"{dm_stat:.3f}"

        p_value = 1 - norm.cdf(dm_stat)

        loss_mean_list.append(float(loss_mean))
        loss_std_list.append(float(loss_std))
        dm_stat_list.append(round(dm_stat, 3))
        p_value_list.append(float(p_value))

    var_col1 = pd.Series({col: var_dict1[col] for col in losses.columns if col in var_dict1})
    var_col2 = pd.Series({col: var_dict2[col] for col in losses.columns if col in var_dict2})

    dm_df = pd.DataFrame(
        {
            "VaR1": var_col1,
            "VaR2": var_col2,
            "DM_stat": dm_stat_list,
            "p_value": p_value_list,
            "differential_mean": loss_mean_list,
            "differential_std": loss_std_list,
        }
    )
    dm_df[["p_value", "differential_mean", "differential_std"]] = dm_df[
        ["p_value", "differential_mean", "differential_std"]
    ].round(decimals=3)

    # Disable scientific notation for all floats
    pd.set_option("display.float_format", "{:.3f}".format)

    return dm_df.sort_values(by="DM_stat", ascending=False)
