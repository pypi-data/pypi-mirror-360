import copy
import time

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import fixed_quad
from scipy.optimize import minimize
from scipy.stats import norm

from evtpooling.constants import DEBUG


# Define a custom exception for specific errors if certain
# conditions are not met defined below
class ExtractError(Exception):
    """Custom exception for errors during data extraction."""

    pass


def state_probability(
    x: float, i: int, theta: tuple[list[float], list[tuple[float, float]]]
) -> float:
    """
    Calculate the state probability for a given value x and state index i
    using the parameters from a Gaussian Mixture Model (GMM).

    Parameters
    -----------
    x : float
        The value for which the state probability is calculated.
    i : int
        The index of the state for which the probability is calculated.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
          for the corresponding state.

    Returns
    -------
    float
        The state probability for the given value x and state index i.
        Returns 0.0 if the denominator is less than 0.
    """
    x = float(np.asarray(x))  # convert safely

    pi_list, phi_list = theta

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")

    mu_i, sigma_i = phi_list[i]

    numerator = pi_list[i] * norm.pdf(x, loc=mu_i, scale=sigma_i)
    denominator = sum(
        pi * norm.pdf(x, loc=mu, scale=sigma)
        for pi, (mu, sigma) in zip(pi_list, phi_list, strict=False)
    )

    if np.isclose(numerator, 0.0):
        return 0.0

    if np.isclose(denominator, 0.0, atol=1e-16):
        raise ZeroDivisionError(
            "Can't return the state probability as the denominator is (close to zero)"
        )

    return numerator / denominator


def precompute_pdf_matrix(
    alpha_list: list[float], phi_list: list[tuple[list[float, float]]]
) -> list[list[float]]:
    """
    Precompute norm.pdf(x_j, mu_i, sigma_i) for all x_j in alpha_list and i in phi_list
    Returns a matrix [len(alpha_list) x len(phi_list)]

    Parameters
    ----------
    alpha_list : list[float]
        A list of values at which the density is estimated.
    phi_list: list[tuple[float, float]]
        A list of mixing coefficients for each state.

    Returns
    -------
    list[list[float]]
        A matrix where each row corresponds to a value in alpha_list and each column
        corresponds to a state in phi_list, containing the probability density function values.
    """
    pdf_matrix = []
    for x in alpha_list:
        row = [norm.pdf(x, loc=mu, scale=sigma) for (mu, sigma) in phi_list]
        pdf_matrix.append(row)
    return pdf_matrix


def precompute_bandwidths(
    alpha_list: list[float], phi_list: list[tuple[float, float]]
) -> list[float]:
    """
    Precompute bandwidths for each state based on the standard deviations in phi_list.

    Parameters
    ----------
    alpha_list : list[float]
        A list of values at which the density is estimated.
    phi_list : list[tuple[float, float]]
        A list of tuples, each containing the mean and standard deviation
        for the corresponding state.

    Returns
    -------
    list[float]
        A list of bandwidths for each state, calculated as 2.283 * n^(-0.287) * sigma,
        where n is the length of alpha_list and sigma is the standard deviation for each state.
    """
    n = len(alpha_list)

    return [2.283 * n ** (-0.287) * sigma if sigma > 0 else 0.0 for (_, sigma) in phi_list]


def non_parametric_density(
    x: float,
    alpha_list: list[float],
    theta: tuple[list[float], list[tuple[float, float]]],
    pdf_matrix: list[list[float]],
    bandwidths: list[float],
) -> float:
    """
    Compute the non-parametric density estimate at a point x using a Gaussian Mixture Model (GMM).
    This function uses the Epanechnikov kernel for density estimation.

    Parameters
    ----------
    x : float
        The point at which to evaluate the density estimate.
    alpha_list : list[float]
        A list of values at which the density is estimated.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
                    for the corresponding state.
    pdf_matrix : list[list[float]]
        A precomputed matrix of probability density function values for each state
        at each point in alpha_list.
    bandwidths : list[float]
        A list of bandwidths for each state, used in the non-parametric density estimation.

    Returns
    -------
    float
        The estimated density at point x. If the input list is empty, raises ZeroDivisionError.
    Raises:
    ------
    ZeroDivisionError
        If the input list is empty, indicating that no density can be computed.
    """

    def epanechnikov_kernel(x: float) -> float:
        x = np.asarray(x)
        mask = np.abs(x) <= 1
        return 0.75 * (1 - x**2) * mask

    pi_list, phi_list = theta

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")
    if len(alpha_list) == 0:
        raise ZeroDivisionError("The input list is empty, cannot compute density.")

    def compute_term(j_index):
        x_j = alpha_list[j_index]
        total = 0.0
        for i_index in range(len(pi_list)):
            pdf_val = pdf_matrix[j_index][i_index]
            numerator = pi_list[i_index] * pdf_val
            denominator = sum(pi_list[k] * pdf_matrix[j_index][k] for k in range(len(pi_list)))

            if np.isclose(numerator, 0.0, atol=1e-16):
                total += 0.0

            if np.isclose(denominator, 0.0, atol=1e-16):
                raise ZeroDivisionError(
                    "Can't return the state probability as the denominator is (close to zero)"
                )

            aij = numerator / denominator
            cni = bandwidths[i_index]
            u = (x - x_j) / cni
            total += (aij / cni) * epanechnikov_kernel(u)
        return total

    total_sum = sum(compute_term(j) for j in range(len(alpha_list)))

    return total_sum / len(alpha_list)


def integrand_i(
    x,
    i: int,
    alpha_list: list[float],
    theta: tuple[list[float], list[tuple[float, float]]],
    pdf_matrix: list[list[float]],
    bandwidths: list[float],
    normal_params: tuple[float, float],
) -> float:
    """
    Compute the integrand for the Gaussian Mixture Model (GMM) density function.

    Parameters
    ----------
    x : float
        The value at which to evaluate the integrand.
    i : int
        The index of the state for which the integrand is computed.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
          for the corresponding state.
    pdf_matrix : list[list[float]]
        A precomputed matrix of probability density function values for each state
        at each point in alpha_list.
    bandwidths : list[float]
        A list of bandwidths for each state, used in the non-parametric density estimation.
    normal_params : tuple[float, float]
        A tuple containing the mean and standard deviation for the i-th component.

    Returns
    -------
    float
        The value of the integrand at x for state i.
    """
    pi_list, phi_list = theta

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")

    mu_i, sigma_i = normal_params
    x = np.atleast_1d(x)
    out = np.empty_like(x, dtype=float)

    try:
        for idx, x_val in enumerate(x):
            ai = state_probability(x_val, i, theta)
            fx_phi = norm.pdf(x_val, loc=mu_i, scale=sigma_i)
            ghat = non_parametric_density(x_val, alpha_list, theta, pdf_matrix, bandwidths)
            out[idx] = np.sqrt(ai * fx_phi * ghat)

        return out if out.shape[0] > 1 else out[0]
    except ExtractError as e:
        raise ExtractError(f"Error in computing integrand: {e}") from e


def h_total_int(
    alpha_list: list[float],
    i: int,
    theta: tuple[list[float], list[tuple[float, float]]],
    normal_params: tuple[float, float],
    bounds: tuple[float, float] = None,
    plot: bool = False,
) -> float:
    """
    h_total_int computes the integral of the GMM density function
    for the i-th component over the specified bounds.

    Parameters
    ----------
    alpha_list : list[float]
        A list of values at which the density is estimated.
    i : int
        The index of the component for which the integral is computed.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
          for the corresponding state.
    normal_params : tuple[float, float]
        A tuple containing the mean and standard deviation for the i-th component.
    bounds : tuple[float, float], optional
        The bounds for the integration. If None, defaults to (min(alpha_list), max(alpha_list)).
    plot : bool, optional
        If True, plots the integrand function for the i-th component.

    Returns
    -------
    float
        The value of the integral for the i-th component.
    """
    # Validate inputs
    if not alpha_list or any(a < 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only non-negative values.")

    pi_list, phi_list = theta
    pdf_matrix = precompute_pdf_matrix(alpha_list, phi_list)
    bandwidths = precompute_bandwidths(alpha_list, phi_list)

    if bounds is None:
        lower, higher = max(0, min(alpha_list) - max(bandwidths)), max(alpha_list) + max(bandwidths)
    else:
        lower, higher = bounds

    try:
        integral_i, _ = fixed_quad(
            integrand_i,
            lower,
            higher,
            args=(i, alpha_list, theta, pdf_matrix, bandwidths, normal_params),
            n=100,
        )

        if DEBUG:
            print(
                f"Integrated component {i} with μ={normal_params[0]:.3f} "
                f"and σ={normal_params[1]:.3f}"
                f" with result: {integral_i:.6f}"
            )

        if plot:
            x_range = np.linspace(lower, higher, 100)
            y_vals = []

            for x_val in x_range:
                y = integrand_i(x_val, i, alpha_list, theta, pdf_matrix, bandwidths)
                y_vals.append(y)

            plt.plot(x_range, y_vals, label=f"Component {i}")
            plt.title(f"Integrand_i(x) Profile (Component {i})")
            plt.xlabel("x")
            plt.ylabel("integrand_i(x)")
            plt.grid(True)
            plt.legend()
            plt.show()

        if not np.isfinite(integral_i):
            raise ArithmeticError(f"Non-finite integral for component {i}: {integral_i}")

        return integral_i

    except Exception as e:
        raise RuntimeError(f"Failed to compute integral for component {i}: {e}") from e


def h_theta(
    alpha_list: list[float],
    theta: tuple[list[float], list[tuple[float, float]]],
    bounds: tuple[float, float] = None,
) -> float:
    """
    Compute the value of h(theta) for the Gaussian Mixture Model (GMM).

    Parameters
    ----------
    alpha_list : list[float]
        A list of values at which the density is estimated.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
          for the corresponding state.
    bounds : tuple[float, float], optional
        The bounds for the integration. If None, defaults to (min(alpha_list), max(alpha_list)).

    Returns
    -------
    float
        The value of h(theta), which is the integral of the GMM density function
        over the specified range, weighted by the mixing coefficients.
    """
    # Validate inputs
    if not alpha_list or any(a < 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only non-negative values.")

    pi_list, phi_list = theta
    bandwidths = precompute_bandwidths(alpha_list, phi_list)

    if bounds is None:
        bounds = max(0, min(alpha_list) - max(bandwidths)), max(alpha_list) + max(bandwidths)

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")
    if not alpha_list or any(a < 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only positive values.")

    h_total = 0.0

    for i in range(len(pi_list)):
        try:
            integral_i = h_total_int(alpha_list, i, theta, theta[1][i], bounds)
            weighted_term = np.sqrt(pi_list[i]) * integral_i
            if not np.isfinite(weighted_term):
                raise ArithmeticError(f"Non-finite integral for component {i}: {weighted_term}")
            h_total += weighted_term

        except Exception as e:
            raise RuntimeError(f"Failed to compute integral for component {i}: {e}") from e

    return h_total


def optimize_phi_i(
    i: int,
    alpha_list: list[float],
    theta: tuple[list[float], list[tuple[float, float]]],
    bounds_arg: tuple[float, float] = None,
    plot: bool = False,
) -> tuple[float, float]:
    """
    Optimize the parameters (mu, sigma) for the i-th component of the Gaussian Mixture Model (GMM)
    using the h_theta function.

    Parameters
    ----------
    i : int
        The index of the component to optimize.
    alpha_list : list[float]
        A list of values at which the density is estimated.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
            for the corresponding state.
    bounds_arg : tuple[float, float], optional
        The bounds for the optimization of mu_i and sigma_i. Default is (0, max(alpha_list)).
    plot : bool, optional
        If True, plots a 3D graph of the integrand function for the
        i-th component during optimization.

    Returns
    -------
    tuple[float, float]
        The optimized parameters (mu_i*, sigma_i*) for the i-th component.

    Raises:
    ------
    ValueError
        If the number of mixture weights does not match the number of components,
        or if alpha_list is empty or contains non-positive values.
    RuntimeError
        If the optimization fails for the i-th component.
    """
    pi_list, phi_list = theta
    bandwidths = precompute_bandwidths(alpha_list, phi_list)

    if bounds_arg is None:
        bounds_arg = max(0, min(alpha_list) - max(bandwidths)), max(alpha_list) + max(bandwidths)

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")
    if not alpha_list or any(a < 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only positive values.")

    def objective(normal_params):
        sigma = normal_params[1]
        if sigma <= 0:
            return np.inf
        return -h_total_int(
            alpha_list=alpha_list, i=i, theta=theta, normal_params=normal_params, bounds=bounds_arg
        )

    # Initial guess
    mu0, sigma0 = phi_list[i]

    if DEBUG:
        start = time.time()

    result = minimize(objective, x0=[mu0, sigma0], bounds=[bounds_arg, (0.001, 5)])

    if not result.success:
        raise RuntimeError(f"Optimization failed for component {i}: {result.message}")

    if DEBUG:
        print(
            f"Integration took {time.time() - start:.2f} seconds with result"
            f" μ={result.x[0]:.3f} and σ={result.x[1]:.3f}"
        )

    if plot:
        lower, higher = bounds_arg

        # 3D surface plot over mu and sigma
        mu_vals = np.linspace(1.0, 5.0, 10)
        sigma_vals = np.linspace(0.1, 2.0, 10)
        mu_mesh, sigma_mesh = np.meshgrid(mu_vals, sigma_vals)
        z_mesh = np.zeros_like(mu_mesh)

        for row in range(mu_mesh.shape[0]):
            for col in range(mu_mesh.shape[1]):
                mu = mu_mesh[row, col]
                sigma = sigma_mesh[row, col]

                phi_copy = copy.deepcopy(phi_list)
                theta_copy = (pi_list, phi_copy)

                try:
                    val = fixed_quad(
                        integrand_i,
                        lower,
                        higher,
                        args=(
                            i,
                            alpha_list,
                            theta_copy,
                            precompute_pdf_matrix(alpha_list, phi_copy),
                            precompute_bandwidths(alpha_list, phi_copy),
                            (mu, sigma),
                        ),
                        n=50,
                    )[0]
                    z_mesh[row, col] = val
                except Exception:
                    z_mesh[row, col] = np.nan

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        surf = ax.plot_surface(mu_mesh, sigma_mesh, z_mesh, cmap="viridis", edgecolor="none")
        ax.set_xlabel("mu")
        ax.set_ylabel("sigma")
        ax.set_zlabel("h_total_int")
        ax.set_title(f"h_total_int(mu, sigma) for component {i}")
        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.tight_layout()
        plt.show()

    return result.x  # returns (mu_i*, sigma_i*)


def optimize_pi_i(
    i: int,
    alpha_list: list[float],
    theta: tuple[list[float, list[tuple[float, float]]]],
    normal_params_list: list[tuple[float, float]],
    bounds: tuple[float, float] = None,
) -> float:
    """
    Optimize the mixing coefficient pi_i for the i-th component of the Gaussian Mixture Model (GMM)
    using the h_total_int function.

    Parameters
    ----------
    i : int
        The index of the component for which to optimize the mixing coefficient.
    alpha_list : list[float]
        A list of values at which the density is estimated.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
            for the corresponding state.
    normal_params_list : list[tuple[float, float]]
        A list of tuples, each containing the mean and standard deviation
        for the corresponding component in the GMM.
    bounds : tuple[float, float], optional
        The bounds for the optimization of pi_i. Default is (1.0, 10.0).

    Returns
    -------
    float
        The optimized mixing coefficient pi_i* for the i-th component.
    """
    pi_list, phi_list = theta

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")
    if not alpha_list or any(a < 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only positive values.")

    nominator = h_total_int(alpha_list, i, theta, normal_params_list[i], bounds) ** 2
    denominator = sum(
        h_total_int(alpha_list, j, theta, normal_params_list[j], bounds) ** 2
        for j in range(len(pi_list))
    )

    try:
        return nominator / denominator
    except ZeroDivisionError as e:
        raise ZeroDivisionError("The denominator is zero, cannot compute pi_i.") from e


def hmix_func(
    alpha_list: list[float],
    num_clusters: int,
    theta: tuple[list[float], list[tuple[float, float]]] = None,
    threshold: float = 1e-6,
    max_iter: int = 50,
    bounds_int: tuple[float, float] = None,
    plot: bool = False,
) -> tuple[list[float], list[tuple[float, float]]]:
    """
    Perform hierarchical mixture optimization on the given parameters.

    Parameters
    ----------
    alpha_list : list[float]
        A list of values at which the density is estimated.
    num_clusters : int
        The number of clusters to optimize.
    theta : tuple[list[float], list[tuple[float, float]]]
        A tuple containing:
        - pi_list: A list of mixing coefficients for each state.
        - phi_list: A list of tuples, each containing the mean and standard deviation
          for the corresponding state.
    threshold : float, optional
        The convergence threshold for the optimization. Default is 1e-6.
    max_iter : int, optional
        The maximum number of iterations for the optimization. Default is 1000.
    bounds_int : tuple[float, float], optional
        The bounds for the integration. If None, defaults to (min(alpha_list), max(alpha_list)).
    plot : bool, optional
        If True, plots a 3D graph integrand function for each component during optimization.

    Returns
    -------
    tuple[list[float], list[tuple[float, float]]]
        The optimized parameters (pi_list, phi_list) after hierarchical mixture optimization.
    """
    if theta is None:
        # Initialize theta with equal weights and random means and standard deviations
        pi_list = [1.0 / num_clusters] * num_clusters
        phi_list = [
            (np.random.uniform(1, 4), np.random.uniform(0.5, 1)) for _ in range(num_clusters)
        ]
        theta = (pi_list, phi_list)
    else:
        # Ensure theta is a tuple of lists
        if (
            not isinstance(theta, tuple)
            or len(theta) != 2
            or not all(isinstance(lst, list) for lst in theta)
            or num_clusters != len(theta[0])
        ):
            raise ValueError("Θ must be a tuple of two lists with the same length as num_clusters.")

    print(
        "\033[93m"
        + "=" * 30
        + "Starting Hierarchical Mixture Optimization"
        + "=" * 30
        + "\n\033[0m"
    )
    pi_list, phi_list = copy.deepcopy(theta)
    print(
        f"\033[1mINITIAL PARAMETERS:\n\033[0m"
        f"π={[round(float(pi), 3) for pi in pi_list]}\n"
        f"ϕ={[(round(float(mu), 3), round(float(sigma), 3)) for mu, sigma in phi_list]}\n"
    )

    # Validate inputs
    if not (len(pi_list) == len(phi_list)):
        raise ValueError("Mismatch between number of mixture weights and components.")
    if not alpha_list or any(a <= 0 for a in alpha_list):
        raise ValueError("alpha_list must be non-empty and contain only positive values.")

    h_theta_t = 0.0
    h_theta_t1 = 0.0
    t = 1

    while t < max_iter:
        lower = max(0, min(alpha_list) - max(precompute_bandwidths(alpha_list, phi_list)))
        higher = max(alpha_list) + max(precompute_bandwidths(alpha_list, phi_list))

        h_theta_t = h_theta(alpha_list, (pi_list, phi_list), bounds_int)

        print(
            "\033[95m" + f"Iteration {t}\033[0m: h(Θ) = {h_theta_t:.8f}, h(Θ_t1) = {h_theta_t1:.8f}"
            f" with: \nπ={[round(float(pi), 3) for pi in pi_list]}\nϕ="
            f"{[(round(float(mu), 3), round(float(sigma), 3)) for mu, sigma in phi_list]}\n"
            f"bounds=({lower:.3f}, {higher:.3f})"
        )
        print("-" * 70 + "\n")

        if abs(h_theta_t - h_theta_t1) <= threshold:
            print("\033[92m=" * 30 + "CONVERGENCE REACHED" + "=" * 30 + "\n\033[0m")
            print(
                f"Iteration {t} with Δh(Θ)={h_theta_t - h_theta_t1:.8f}\n"
                f"\033[1mFINAL PARAMETERS:\n\033[0m"
                f"π={[round(float(pi), 3) for pi in pi_list]} \nϕ="
                f"{[(round(float(mu), 3), round(float(sigma), 3)) for mu, sigma in phi_list]}.\n"
            )
            print("=" * 79 + "\n")

            return pi_list, phi_list

        for i in range(num_clusters):
            # Optimize the parameters for each component
            if DEBUG:
                print(
                    f"Optimizing component {i} with initial parameters: "
                    f"μ={phi_list[i][0]:.3f}, σ={phi_list[i][1]:.3f}"
                    f" and π={pi_list[i]:.3f}"
                )
                pi_list_plot = copy.deepcopy(pi_list)
                print(f"Current π: {[round(float(pi), 3) for pi in pi_list_plot]}\n")

            mu_opt, sigma_opt = optimize_phi_i(i, alpha_list, theta, bounds_arg=bounds_int)

            print("-" * 70)
            print(
                f"Optimization result for component {i}: μ_opt={mu_opt:.3f}, σ_opt={sigma_opt:.3f}"
            )
            print("-" * 70 + "\n")

            # Update the phi parameters for i-th component
            phi_list[i] = (mu_opt, sigma_opt)

            if plot:
                # 3D surface plot over mu and sigma
                mu_vals = np.linspace(1.0, 5.0, 10)
                sigma_vals = np.linspace(0.1, 2.0, 10)
                mu_mesh, sigma_mesh = np.meshgrid(mu_vals, sigma_vals)
                z_mesh = np.zeros_like(mu_mesh)

                for row in range(mu_mesh.shape[0]):
                    for col in range(mu_mesh.shape[1]):
                        mu = mu_mesh[row, col]
                        sigma = sigma_mesh[row, col]

                        phi_copy = copy.deepcopy(phi_list)
                        theta_copy = (pi_list_plot, phi_copy)

                        try:
                            val = fixed_quad(
                                integrand_i,
                                lower,
                                higher,
                                args=(
                                    i,
                                    alpha_list,
                                    theta_copy,
                                    precompute_pdf_matrix(alpha_list, phi_copy),
                                    precompute_bandwidths(alpha_list, phi_copy),
                                    (mu, sigma),
                                ),
                                n=50,
                            )[0]
                            z_mesh[row, col] = val
                        except Exception:
                            z_mesh[row, col] = np.nan

                fig = plt.figure(figsize=(10, 7))
                ax = fig.add_subplot(111, projection="3d")
                surf = ax.plot_surface(
                    mu_mesh, sigma_mesh, z_mesh, cmap="viridis", edgecolor="none"
                )
                ax.set_xlabel("mu")
                ax.set_ylabel("sigma")
                ax.set_zlabel("h_total_int")
                ax.set_title(f"h_total_int(mu, sigma) for component {i}")
                fig.colorbar(surf, shrink=0.5, aspect=5)
                plt.tight_layout()
                plt.show()

        # Optimize the mixing coefficient pi_i
        print("=" * 30 + "Optimizing mixing coefficients" + "=" * 30 + "\n")
        for i in range(num_clusters):
            try:
                pi_list[i] = optimize_pi_i(i, alpha_list, theta, phi_list, bounds_int)
                print(f"Optimized π_{i}: {pi_list[i]:.6f}\n")
            except ZeroDivisionError as e:
                print(f"ZeroDivisionError during optimization of pi_i for component {i}: {e}")
                pi_list[i] = 0.0
        print("=" * 30 + "End of optimization" + "=" * 30 + "\n")

        total = sum(pi_list)
        if not np.isclose(total, 1.0):
            print("\033[91m" + "=" * 30 + "Warning!!!" + "=" * 30 + "\n\033[0m")
            print(f"Mixing coefficients do not (exactly) sum to 1. Normalizing: {total:.3f}")
            print(f"Before normalization: π={[round(float(pi), 5) for pi in pi_list]}" + "\n")
            print("\033[91m" + "=" * 70 + "\n\033[0m")
            pi_list = [pi / total for pi in pi_list]

        # Update the parameters for the next iteration
        h_theta_t1 = h_theta_t
        theta = (pi_list, phi_list)
        t += 1

        if t == max_iter:
            print("\033[91m" + "=" * 30 + "Warning!!!" + "=" * 30 + "\n\033[0m")
            print(f"Maximum iterations {max_iter} reached without convergence.\n")
            print(
                f"Final parameters: π={[float(pi) for pi in pi_list]}, "
                f"ϕ={[(float(mu), float(sigma)) for mu, sigma in phi_list]}"
            )

            return pi_list, phi_list

    print("\033[93m" + "=" * 32 + "RESULTS" + "=" * 32 + "\n\033[0m")
    print(f"Converged after {t} iterations with h(Θ) = {h_theta_t} and h(Θ_t-1) = {h_theta_t1}\n")
    print(
        f"Final parameters: π={[float(pi) for pi in pi_list]}, "
        f"ϕ={[(float(mu), float(sigma)) for mu, sigma in phi_list]}\n"
    )
    print("=" * 71 + "\n")

    return pi_list, phi_list
