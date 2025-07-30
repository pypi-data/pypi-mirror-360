from inspect import signature

import numpy as np
import pandas as pd
from scipy.integrate import fixed_quad
from scipy.stats import norm

from evtpooling.constants import DEBUG
from evtpooling.utils import calculate_alpha_var, get_alpha_dict

from .hmix import hmix_func, non_parametric_density, precompute_bandwidths, precompute_pdf_matrix


def filter_kwargs(func, kwargs) -> dict[object:object]:
    """
    Filters the keyword arguments to only include those that are valid for the given function.

    Parameters
    ----------
    func : callable
        The function for which to filter the keyword arguments.
    kwargs : dict
        The keyword arguments to filter.

    Returns
    -------
    dict
        A dictionary containing only the keyword arguments that are valid for the function.
    """
    sig = signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}


def hellinger_distance(
    f_x, g_x, bounds: tuple[float, float], n_points: int = 100, **kwargs
) -> float:
    """
    Calculates the Hellinger distance for any two functions f(·) and g(·)

    Parameters
    ----------
    f_x : callable
        The first function for which to calculate the Hellinger distance.
    g_x : callable
        The second function for which to calculate the Helliner distance.
    bounds : tuple[float, float]
        The bounds for the integration.
    n_points : int
        Order of quadrature integration.
    **kwargs : dict
        Remaining input parameters necessary to call f_x and g_x

    Returns
    -------
    integral : float
        The Hellinger distance between f_x and g_x
    """
    lower, higher = bounds

    def integrand(x):
        f_val = f_x(x, **filter_kwargs(f_x, kwargs))
        g_val = g_x(x, **filter_kwargs(g_x, kwargs))

        return (np.sqrt(f_val) - np.sqrt(g_val)) ** 2

    integral, _ = fixed_quad(integrand, lower, higher, n=n_points)

    return integral


def rmtc_pooling(
    losses: pd.DataFrame,
    k_threshold: int,
    beta: tuple[list[float], list[tuple[float, float]]] = None,
    bounds_int: tuple[float, float] = None,
    max_iter: int = 50,
    threshold: float = 1e-6,
):
    """
    Performs RMTC pooling on the given losses DataFrame.

    Parameters
    ----------
    losses : pd.DataFrame
        DataFrame containing the losses data.
    k_threshold : int
        The threshold for the number of clusters.
    beta : tuple[list[float], list[tuple[float, float]]], optional
        Initial parameters for the mixture model, consisting of a list of mixture
        weights and a list of tuples representing the mean and standard deviation
        of each component. If None, the function will start with a single cluster.
    bounds_int : tuple[float, float], optional
        The bounds for the integration. If None, it will be set based on the data.
    max_iter : int, optional
        The maximum number of iterations for the optimization process. Default is 50.
    threshold : float, optional
        The convergence threshold for the Hellinger distance. Default is 1e-6.

    Returns
    -------
    df_pooling : pd.DataFrame
        DataFrame containing the pooled results with columns for the RMTC alpha and variance.
    beta_list : list[tuple[list[float], list[tuple[float, float]]]]
        List of tuples containing the mixture weights and parameters for each iteration.
    """
    alpha_dict = get_alpha_dict(losses, k_threshold=k_threshold)
    alpha_list = list(alpha_dict.values())

    def flatten_beta(beta: tuple[list[float], list[tuple[float, float]]]) -> np.ndarray:
        """
        Flattens the beta tuple into a single numpy array.

        Parameters
        ----------
        beta : tuple[list[float], list[tuple[float, float]]]
            The beta tuple containing mixture weights and parameters.

        Returns
        -------
        np.ndarray
            A flattened numpy array containing the mixture weights and parameters.
        """
        weights = beta[0]  # list of floats
        params = beta[1]  # list of tuples
        flat_params = [v for pair in params for v in pair]  # flatten tuples

        return np.array(weights + flat_params)

    def compute_tau_p_k(
        beta_k: tuple[list[float], list[tuple[float, float]]],
        beta_k1: tuple[list[float], list[tuple[float, float]]],
        p: int,
    ) -> float:
        """
        Computes the tau_p_k value based on the difference in
        norms of the flattened beta parameters.

        Parameters
        ----------
        beta_k : tuple[list[float], list[tuple[float, float]]]
            The beta parameters for the k-th iteration.
        beta_k1 : tuple[list[float], list[tuple[float, float]]]
            The beta parameters for the (k+1)-th iteration.
        p : int
            The number of dimensions in alpha list.

        Returns
        -------
        float
            The computed tau_p_k value, which is the average change in the parameters.
        """
        norm_k = np.sum(np.abs(flatten_beta(beta_k)))
        norm_k1 = np.sum(np.abs(flatten_beta(beta_k1)))
        tau = (norm_k1 - norm_k) / (p ** (1 / 2))

        if DEBUG:
            print(
                f"tau_p_k={tau:.6f} for p={p} dimensions with norm_k={norm_k} "
                f"and norm_k1={norm_k1}.\n"
            )

        return tau

    def normal_mixture_k(
        x: float, pi_list: list[float], phi_list: list[tuple[float, float]]
    ) -> float:
        """
        Computes the value of a normal mixture model at a given point x.

        Parameters
        ----------
        x : float
            The point at which to evaluate the normal mixture model.
        pi_list : list[float]
            List of mixture weights for each component.
        phi_list : list[tuple[float, float]]
            List of tuples, each containing the mean and standard deviation of a component.

        Returns
        -------
        float
            The value of the normal mixture model at point x.
        """
        val = np.sum(
            [
                pi * norm.pdf(x, loc=mu, scale=sigma)
                for pi, (mu, sigma) in zip(pi_list, phi_list, strict=False)
            ]
        )

        return val

    def expand_pi_phi(
        pi_list: list[float],
        phi_list: list[tuple[float, float]],
        mean_diff: float = 0.25,
        std_diff: float = 0.25,
    ) -> tuple[list[float], list[tuple[float, float]]]:
        """
        Expands the mixture model by adding a new cluster based on the existing parameters.

        Parameters
        ----------
        pi_list : list[float]
            List of mixture weights for each component.
        phi_list : list[tuple[float, float]]
            List of tuples, each containing the mean and standard deviation of a component.
        epsilon_mean : float, optional
            Standard deviation for the new mean, default is 1e-2.
        epsilon_std : float, optional
            Standard deviation for the new standard deviation, default is 1e-2.

        Returns
        -------
        tuple[list[float], list[tuple[float, float]]]
            Updated lists of mixture weights and parameters after adding the new cluster.
        """
        # Validate inputs
        if not mean_diff > 0 or not std_diff > 0:
            raise ValueError("mean_diff and std_diff must be greater than 0.")

        pi = np.array(pi_list)
        phi = np.array(phi_list)

        i_max = np.argmax(pi)
        pi_max = pi[i_max]
        pi[i_max] = pi_max / 2  # shrink old
        pi_new = pi_max / 2  # new cluster weight

        mu_old, std_old = phi[i_max]
        phi[i_max] = (mu_old * (1 - mean_diff), std_old * (1 - std_diff))  # shrink old
        mu_new = mu_old + (1 + mean_diff)
        std_new = max(0.5, std_old * (1 + std_diff))  # avoid std <= 0.5

        phi_new = (mu_new, std_new)

        new_pi_list = list(pi) + [pi_new]
        new_phi_list = list(phi) + [phi_new]

        # Fix any zero weights to at least 0.10
        new_pi_list = [max(p, 0.20) for p in new_pi_list]
        total = sum(new_pi_list)
        new_pi_list = [p / total for p in new_pi_list]

        # Fix any near zero means and standard deviations
        new_phi_list = [(max(mu, 1.5), max(sigma, 0.5)) for mu, sigma in new_phi_list]

        return new_pi_list, new_phi_list

    hd_k = 100
    hd_k1 = 99.0
    tau_p_k = 0.0
    beta_list, pi_list, phi_list = [], [], []
    k = 1
    iteration = 1

    while hd_k - hd_k1 > tau_p_k:
        print(
            "\033[94m\n"
            + "=" * 30
            + "Robust Mixture Tail Clustering Optimization"
            + "=" * 30
            + "\n\033[0m"
        )
        if beta is not None:
            # Validate inputs
            if not (len(beta[0]) == len(beta[1])):
                raise ValueError("Mismatch between number of mixture weights and components.")

            k = len(beta[0])
            print("-" * 30 + f"Initializing HMIX algorithm for {k} clusters" + "-" * 30 + "\n")
            pi_list, phi_list = hmix_func(
                alpha_list=alpha_list,
                num_clusters=k,
                theta=beta,
                threshold=threshold,
                max_iter=max_iter,
                bounds_int=bounds_int,
            )
        else:
            print("-" * 30 + "Initializing HMIX algorithm for 1 cluster" + "-" * 30 + "\n")
            pi_list, phi_list = hmix_func(
                alpha_list=alpha_list,
                num_clusters=k,
                threshold=threshold,
                max_iter=max_iter,
                bounds_int=bounds_int,
            )

        beta_list.append((pi_list, phi_list))
        lower = np.min([mu for mu, _ in phi_list]) - 5 * np.max([sigma for _, sigma in phi_list])
        higher = np.max([mu for mu, _ in phi_list]) + 5 * np.max([sigma for _, sigma in phi_list])

        hd_k = hd_k1

        if iteration == 1:
            hd_k1 = hellinger_distance(
                f_x=normal_mixture_k,
                g_x=non_parametric_density,
                bounds=(lower, higher),
                n_points=100,
                pi_list=pi_list,
                phi_list=phi_list,
                alpha_list=alpha_list,
                theta=(pi_list, phi_list),
                pdf_matrix=precompute_pdf_matrix(alpha_list, phi_list),
                bandwidths=precompute_bandwidths(alpha_list, phi_list),
            )
            tau_p_k = compute_tau_p_k(
                [[0], [(0.0, 0.0)]], beta_list[iteration - 1], len(alpha_list)
            )
        else:
            hd_k1 = hellinger_distance(
                f_x=normal_mixture_k,
                g_x=non_parametric_density,
                bounds=(lower, higher),
                n_points=100,
                pi_list=pi_list,
                phi_list=phi_list,
                alpha_list=alpha_list,
                theta=beta_list[-2],
                pdf_matrix=precompute_pdf_matrix(alpha_list, beta_list[-2][1]),
                bandwidths=precompute_bandwidths(alpha_list, beta_list[-2][1]),
            )
            tau_p_k = compute_tau_p_k(
                beta_list[iteration - 2], beta_list[iteration - 1], len(alpha_list)
            )

        print(
            "\033[96m" + "-" * 30 + "HELLINGER DISTANCE" + "-" * 30 + "\n\n\033[0m"
            f"D^2(f_{k - 1}, ψ_{len(alpha_list)},{k - 1})={hd_k}\n"
            f"D^2(f_{k}, ψ_{len(alpha_list)},{k - 1})={hd_k1}\n"
        )

        if hd_k - hd_k1 <= tau_p_k:
            print("\033[1;92m" + "=" * 30 + "CONVERGENCE REACHED" + "=" * 30 + "\n\033[0m")
            print(
                f"Optimal cluster amount={k - 1} because ΔD^2(f_{k}, ψ_{len(alpha_list)},{k - 1})"
                f"={hd_k - hd_k1:.5f} <= {tau_p_k:.5f}\n"
                f"FINAL PARAMETERS:\n"
                f"π={[round(float(pi), 3) for pi in beta_list[-2][0]]} \nϕ="
                f"{
                    [
                        (round(float(mu), 3), round(float(sigma), 3))
                        for mu, sigma in beta_list[-2][1]
                    ]
                }."
            )
            print("\n" + "=" * 79 + "\n")

            break

        print(
            f"ΔD^2(f_{k}, ψ_{len(alpha_list)},{k - 1})={hd_k - hd_k1:.5f} > "
            f"{tau_p_k:.5f}=τ_{len(alpha_list)}_{k - 1}\n"
        )
        print("\033[36m" + "-" * 30 + "EXPANDING CLUSTER" + "-" * 30 + "\033[0m")

        beta = expand_pi_phi(pi_list, phi_list)

        k += 1
        iteration += 1

    pi_list_final, phi_list_final = beta_list[-2]
    df_pooling = pd.DataFrame(index=alpha_dict.keys())
    cluster_list = [
        np.argmax(
            [
                pi * norm.pdf(alpha, loc=mu, scale=sigma)
                for pi, (mu, sigma) in zip(pi_list_final, phi_list_final, strict=False)
            ]
        )
        for alpha in alpha_list
    ]

    df_pooling["rmtc_alpha"] = [phi_list_final[i][0] for i in cluster_list]
    df_pooling["rmtc_var"] = [
        calculate_alpha_var(
            losses=losses[index], k_threshold=k_threshold, alpha_hat=df_pooling.iloc[i, 0]
        )[1]
        for i, index in enumerate(losses.columns)
    ]

    return df_pooling, beta_list
