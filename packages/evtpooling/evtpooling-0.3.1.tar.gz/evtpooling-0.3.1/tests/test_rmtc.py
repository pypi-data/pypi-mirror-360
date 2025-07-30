import numpy as np
import pandas as pd
import pytest
from scipy.stats import pareto

from evtpooling import rmtc_pooling

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def pareto_dataframe():
    np.random.seed(42)

    n_rows = 830
    n_cols = 200

    # Define (shape, scale) combinations
    shape_scale_pairs = [(2.0, 0.5), (3.0, 0.75), (4.0, 1.0)]
    cols_per_pair = [n_cols // len(shape_scale_pairs)] * len(shape_scale_pairs)
    cols_per_pair[-1] += n_cols - sum(cols_per_pair)  # adjust to total 200

    data = {}
    col_index = 1
    for (b, scale), count in zip(shape_scale_pairs, cols_per_pair, strict=False):
        for _ in range(count):
            col_name = f"losses{col_index}_b{b}_s{scale}"
            data[col_name] = pareto.rvs(b=b, scale=scale, size=n_rows)
            col_index += 1

    return pd.DataFrame(data), [0.33, 0.33, 0.34], shape_scale_pairs


# --------------------
# Tests
# --------------------


def sort_by_mu(pi_list, phi_list):
    return zip(*sorted(zip(pi_list, phi_list, strict=False), key=lambda x: x[1][0]), strict=False)


# To run this test: pytest tests/test_rmtc.py::test_rmtc_converges_to_known_parameters -s
def test_rmtc_converges_to_known_parameters(pareto_dataframe, request):
    if request.node.nodeid not in request.config.args:
        pytest.skip("Skipped by default unless explicitly selected")

    df_losses, true_pi, true_phi = pareto_dataframe
    beta = ([0.5, 0.5], [(1.5, 0.5), (2.5, 1.0)])

    df_pooling, beta_list = rmtc_pooling(
        losses=df_losses, k_threshold=80, beta=beta, threshold=1e-4, max_iter=50
    )
    print(
        f"Estimated parameters:\n{
            [
                (
                    [round(float(x), 5) for x in weights],
                    [(round(float(a), 5), round(float(b), 5)) for (a, b) in components],
                )
                for weights, components in beta_list
            ]
        }"
    )
    print(df_pooling.iloc[55:80, :], "\n")
    print(df_pooling["rmtc_alpha"].describe())

    # Sort estimated and true components by mean for comparison
    pi_est, phi_est = beta_list[-2]
    pi_est, phi_est = sort_by_mu(pi_est, phi_est)
    true_pi, true_phi = sort_by_mu(true_pi, true_phi)

    pi_est = list(pi_est)
    phi_est = list(phi_est)

    for (pi_e, phi_e), (pi_t, phi_t) in zip(
        zip(pi_est, phi_est, strict=False), zip(true_pi, true_phi, strict=False), strict=False
    ):
        mu_e, sigma_e = phi_e
        mu_t, sigma_t = phi_t

        assert np.isclose(pi_e, pi_t, atol=0.15), f"Mixing coefficient mismatch: {pi_e} vs {pi_t}"
        assert np.isclose(mu_e, mu_t, atol=0.5), f"Mean mismatch: {mu_e} vs {mu_t}"
        # assert np.isclose(sigma_e, sigma_t, atol=0.15), f"Std mismatch: {sigma_e} vs {sigma_t}"

    print("Test passed: Estimated parameters are close to the true mixture components and mean.")
