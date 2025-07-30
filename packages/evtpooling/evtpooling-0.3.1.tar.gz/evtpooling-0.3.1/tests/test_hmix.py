import numpy as np
import pytest
from scipy.stats import norm

from evtpooling import (
    ExtractError,
    h_theta,
    h_total_int,
    hmix_func,
    integrand_i,
    non_parametric_density,
    optimize_phi_i,
    optimize_pi_i,
    precompute_bandwidths,
    precompute_pdf_matrix,
    state_probability,
)

# --------------------
# Fixtures (mock data)
# --------------------


# Mock dependencies
def mock_state_probability(x, i, theta):
    return 0.5  # constant valid value


def mock_non_parametric_density(x, alpha_list, theta, pdf_matrix, bandwidths):
    return 0.8  # constant valid density


@pytest.fixture
def state_probability_validation():
    pi_list = [0.2, 0.2, 0.6]
    phi_list = [(0.0, 1.0), (3.0, 1.0), (3.0, 2.0)]

    return (pi_list, phi_list)


@pytest.fixture
def precompute_validation():
    alpha_list = [2.0, 5.0]
    phi_list = [(1.0, 2.0), (3.0, 1.0)]

    return alpha_list, phi_list


@pytest.fixture
def validation_data():
    alpha_list = [0.0, 3.0, 9.0]
    pi_list = [0.2, 0.2, 0.6]
    phi_list = [(0.0, 1.0), (3.0, 1.0), (3.0, 2.0)]
    pdf_matrix = precompute_pdf_matrix(alpha_list, phi_list)
    bandwidths = [
        2.283 * len(alpha_list) ** (-0.287) * sigma if sigma > 0 else 0.0
        for sigma in [s for (_, s) in phi_list]
    ]

    return alpha_list, (pi_list, phi_list), pdf_matrix, bandwidths


@pytest.fixture
def known_mixture_data():
    np.random.seed(42)
    # True parameters
    true_pi = [0.6, 0.4]
    true_phi = [(1.8, 0.4), (3.5, 0.5)]

    # Sample data from the known mixture
    n_samples = 200
    n1 = int(n_samples * true_pi[0])
    n2 = n_samples - n1

    samples_1 = np.random.normal(loc=true_phi[0][0], scale=true_phi[0][1], size=n1)
    samples_2 = np.random.normal(loc=true_phi[1][0], scale=true_phi[1][1], size=n2)
    alpha_list = np.concatenate([samples_1, samples_2]).tolist()

    return alpha_list, true_pi, true_phi


# Patch actual implementations with mocks
@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", mock_state_probability)
    monkeypatch.setattr(
        "evtpooling.pooling.hmix.non_parametric_density", mock_non_parametric_density
    )


# --------------------
# Tests
# --------------------


def test_state_probability(state_probability_validation):
    probability = state_probability(0.0, 0, state_probability_validation)

    assert isinstance(probability, float), "The result should be a float."
    assert 0.0 <= probability <= 1.0, "The probability should be between 0 and 1."
    assert probability == pytest.approx(0.667517, rel=1e-5), (
        "The calculated probability for x=0.0 and i=0 does not match the expected value."
    )
    assert state_probability(3.0, 0, state_probability_validation) == pytest.approx(
        0.00442394, rel=1e-5
    ), "The calculated probability for x=3.0 and i=0 does not match the expected value."
    assert state_probability(0.0, 2, state_probability_validation) == pytest.approx(
        0.325066, rel=1e-5
    ), "The calculated probability for x=0.0 and i=2 does not match the expected value."
    assert state_probability(3.0, 2, state_probability_validation) == pytest.approx(
        0.597345, rel=1e-5
    ), "The calculated probability for x=3.0 and i=2 does not match the expected value."


def test_precompute_pdf_matrix(precompute_validation):
    alpha_list, phi_list = precompute_validation
    pdf_matrix = precompute_pdf_matrix(alpha_list, phi_list)

    assert pdf_matrix[0][0] == pytest.approx(
        1 / (np.sqrt(2 * np.pi) * 2.0) * np.exp(-0.5 * 0.25), rel=1e-5
    ), "PDF for (1.0, 2.0) at alpha=2.0 does not match expected value."
    assert pdf_matrix[1][0] == pytest.approx(
        1 / (np.sqrt(2 * np.pi) * 2.0) * np.exp(-0.5 * 4.0), rel=1e-5
    ), "PDF for (1.0, 2.0) at alpha=5.0 does not match expected value."
    assert pdf_matrix[0][1] == pytest.approx(
        1 / (np.sqrt(2 * np.pi) * 1.0) * np.exp(-0.5 * 1.0), rel=1e-5
    ), "PDF for (3.0, 1.0) at alpha=2.0 does not match expected value."
    assert pdf_matrix[1][1] == pytest.approx(
        1 / (np.sqrt(2 * np.pi) * 1.0) * np.exp(-0.5 * 4.0), rel=1e-5
    ), "PDF for (3.0, 1.0) at alpha=5.0 does not match expected value."


def test_precompute_bandwidths(precompute_validation):
    alpha_list, phi_list = precompute_validation
    bandwidths = precompute_bandwidths(alpha_list, phi_list)

    assert len(bandwidths) == len(phi_list), "Bandwidths length should match number of components"
    assert np.isclose(bandwidths[0], 2.283 * 2 ** (-0.287) * 2.0, atol=1e-6), (
        "Bandwidth for first component does not match expected value"
    )
    assert np.isclose(bandwidths[1], 2.283 * 2 ** (-0.287) * 1.0, atol=1e-6), (
        "Bandwidth for second component does not match expected value"
    )


def test_non_parametric_density(validation_data, monkeypatch):
    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)

    alpha_list, theta, pdf_matrix, bandwidths = validation_data
    val = non_parametric_density(
        x=2.0, alpha_list=alpha_list, theta=theta, pdf_matrix=pdf_matrix, bandwidths=bandwidths
    )
    lower, higher = min(alpha_list) - max(bandwidths), max(alpha_list) + max(bandwidths)
    zero_list = [lower, higher + 0.01]
    non_zero_list = [lower - 0.01, higher]

    assert theta[0] == [0.2, 0.2, 0.6], "pi_list has changed from expected"
    assert np.isclose(val, 0.0950433545, atol=1e-6), (
        "g_hat should return the expected value for x=2.0"
    )
    assert [
        non_parametric_density(
            x=zero, alpha_list=alpha_list, theta=theta, pdf_matrix=pdf_matrix, bandwidths=bandwidths
        )
        for zero in zero_list
    ] == [0.0, 0.0], (
        "g_hat should return 0.0 for x below the minimum alpha "
        "and above the maximum alpha with bandwidths"
    )
    assert [
        non_parametric_density(
            x=non_zero,
            alpha_list=alpha_list,
            theta=theta,
            pdf_matrix=pdf_matrix,
            bandwidths=bandwidths,
        )
        for non_zero in non_zero_list
    ] != [0.0, 0.0], (
        "g_hat should not return 0.0 for x below the minimum alpha "
        "and above the maximum alpha without bandwidths"
    )


def test_g_hat_edge_case_empty_input(validation_data):
    alpha_list = []
    theta = validation_data[1]
    x = 2.0
    with pytest.raises(ZeroDivisionError):
        non_parametric_density(x, alpha_list, theta, [], [])


def test_integrand_i_basic(validation_data, monkeypatch):
    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)
    monkeypatch.setattr("evtpooling.pooling.hmix.non_parametric_density", non_parametric_density)

    alpha_list, theta, pdf_matrix, bandwidths = validation_data
    val = integrand_i(
        x=2.0,
        i=0,
        alpha_list=alpha_list,
        theta=theta,
        pdf_matrix=pdf_matrix,
        bandwidths=bandwidths,
        normal_params=theta[1][0],
    )

    assert isinstance(val, float)
    assert np.isclose(val, 0.01833589, atol=1e-6)


# Edge test: sigma too small (density should still be finite)
def test_integrand_i_narrow_variance(validation_data):
    alpha_example, _, pdf_matrix, bandwidths = validation_data
    theta = ([1.0], [(2.0, 1e-6)])
    val = integrand_i(
        x=2.0,
        i=0,
        alpha_list=alpha_example,
        theta=theta,
        pdf_matrix=pdf_matrix,
        bandwidths=bandwidths,
        normal_params=theta[1][0],
    )
    assert np.isfinite(val)


def test_integrand_i_extract_error(monkeypatch, validation_data):
    alpha_example, theta_example, _, _ = validation_data

    def failing_state_probability(x, i, theta):
        raise ExtractError("Mock failure")

    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", failing_state_probability)

    with pytest.raises(ExtractError, match="Error in computing integrand"):
        integrand_i(
            x=2.0,
            i=0,
            alpha_list=alpha_example,
            theta=theta_example,
            pdf_matrix=[],
            bandwidths=[],
            normal_params=[0, 0],
        )


def test_h_total_int(validation_data, monkeypatch):
    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)
    monkeypatch.setattr("evtpooling.pooling.hmix.non_parametric_density", non_parametric_density)

    alpha_list, theta, _, _ = validation_data
    pdf_matrix = precompute_pdf_matrix(alpha_list, theta[1])
    bandwidths = precompute_bandwidths(alpha_list, theta[1])
    lower, higher = max(0, min(alpha_list) - max(bandwidths)), max(alpha_list) + max(bandwidths)

    plot_param = False
    val_func_list = [
        h_total_int(
            alpha_list=alpha_list,
            i=index,
            theta=theta,
            plot=plot_param,
            normal_params=theta[1][index],
        )
        for index in range(len(theta[1]))
    ]

    def objective(x_grid, i):
        mu, sigma = theta[1][i]
        a_i = np.array([state_probability(x, i, theta) for x in x_grid])
        f_phi = norm.pdf(x_grid, loc=mu, scale=sigma)
        g_n = np.array(
            [non_parametric_density(x, alpha_list, theta, pdf_matrix, bandwidths) for x in x_grid]
        )
        integrand = np.sqrt(a_i * f_phi * g_n)

        return np.trapezoid(integrand, x_grid)

    val_hand_list = [
        objective(np.linspace(lower, higher, 1000), i=index) for index in range(len(theta[1]))
    ]

    assert np.allclose(val_func_list, val_hand_list, atol=1e-3), (
        "h_total_int should return the expected value for the integral"
    )


def test_h_theta(validation_data, monkeypatch):
    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)
    monkeypatch.setattr("evtpooling.pooling.hmix.non_parametric_density", non_parametric_density)

    alpha_list, theta, _, _ = validation_data
    val_func = h_theta(alpha_list=alpha_list, theta=theta)

    h_tot_0 = h_total_int(
        alpha_list=alpha_list, i=0, theta=theta, normal_params=theta[1][0]
    ) * np.sqrt(theta[0][0])
    h_tot_1 = h_total_int(
        alpha_list=alpha_list, i=1, theta=theta, normal_params=theta[1][1]
    ) * np.sqrt(theta[0][1])
    h_tot_2 = h_total_int(
        alpha_list=alpha_list, i=2, theta=theta, normal_params=theta[1][2]
    ) * np.sqrt(theta[0][2])
    val_hand = h_tot_0 + h_tot_1 + h_tot_2

    assert np.isclose(val_func, val_hand, atol=1e-6), (
        "h_theta should return the expected value for the mixture entropy"
    )


def test_h_theta_input_validation_mismatched_components():
    alpha_list = [2.0, 3.0]
    theta = ([0.5, 0.5], [(1.0, 0.5)])  # Only one φ_i

    with pytest.raises(ValueError, match="Mismatch between number of mixture weights"):
        h_theta(alpha_list, theta)


def test_h_theta_input_validation_empty_alpha():
    alpha_list = []
    theta = ([0.5, 0.5], [(1.0, 0.5), (2.0, 0.5)])

    with pytest.raises(ValueError, match="alpha_list must be non-empty"):
        h_theta(alpha_list, theta)


@pytest.mark.filterwarnings("ignore::scipy.integrate.IntegrationWarning")
def test_h_theta_nan_propagation(monkeypatch, validation_data):
    alpha_list, theta = validation_data[:2]

    # Force integrand to return nan
    def broken_integrand(*args, **kwargs):
        return np.nan

    monkeypatch.setattr("evtpooling.pooling.hmix.integrand_i", broken_integrand)

    with pytest.raises(RuntimeError, match="Non-finite integral for component"):
        h_theta(alpha_list=alpha_list, theta=theta)


def test_optimize_phi(validation_data, monkeypatch):
    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)
    monkeypatch.setattr("evtpooling.pooling.hmix.non_parametric_density", non_parametric_density)

    alpha_list, theta, _, _ = validation_data

    # Test with a valid component index
    mu_opt, sigma_opt = optimize_phi_i(i=0, alpha_list=alpha_list, theta=theta, plot=False)
    print(f"Optimized mu: {mu_opt}, sigma: {sigma_opt}")

    assert np.allclose((mu_opt, sigma_opt), (0.703371250345638, 0.4349562221499336), atol=1e-6), (
        "Optimized parameters for component 0 should match expected values"
    )


def test_optimize_phi_i_improves_h(validation_data):
    alpha_list, theta = validation_data[:2]

    # Original h(θ)
    original_val = h_theta(alpha_list, theta)

    # Optimize component 0
    mu_opt, sigma_opt = optimize_phi_i(i=0, alpha_list=alpha_list, theta=theta)
    new_phi_list = theta[1].copy()
    new_phi_list[0] = (mu_opt, sigma_opt)
    updated_theta = (theta[0], new_phi_list)

    new_val = h_theta(alpha_list, updated_theta)
    print(f"Original h(θ): {original_val}, Optimized h(θ): {new_val}")

    assert new_val >= original_val, "Optimized h(θ) should not decrease"


def test_optimize_phi_i_fails_gracefully(monkeypatch, validation_data):
    alpha_list, theta = validation_data[:2]

    def bad_h_total_int(*args, **kwargs):
        return np.nan

    # Force h_theta to return NaN so optimization fails
    monkeypatch.setattr("evtpooling.pooling.hmix.h_total_int", bad_h_total_int)

    with pytest.raises(RuntimeError, match="Optimization failed"):
        optimize_phi_i(i=0, alpha_list=alpha_list, theta=theta)


def test_optimize_pi_i_returns_finite(validation_data):
    alpha_list, theta = validation_data[:2]

    pi_opt_list = [
        optimize_pi_i(i=i, alpha_list=alpha_list, theta=theta, normal_params_list=theta[1])
        for i in range(len(theta[1]))
    ]

    assert all(isinstance(i, float) for i in pi_opt_list), "Not all elements are floats"
    assert all(0 <= x <= 1 for x in pi_opt_list)
    assert np.sum(pi_opt_list) == pytest.approx(1.0, rel=1e-6), (
        "The optimized mixing coefficients should sum to 1."
    )


def sort_by_mu(pi_list, phi_list):
    return zip(*sorted(zip(pi_list, phi_list, strict=False), key=lambda x: x[1][0]), strict=False)


# To run this test: pytest tests/test_hmix.py::test_hmix_converges_to_known_parameters -s
def test_hmix_converges_to_known_parameters(known_mixture_data, monkeypatch, request):
    if request.node.nodeid not in request.config.args:
        pytest.skip("Skipped by default unless explicitly selected")

    # Unpatch state_probability just for this test
    monkeypatch.setattr("evtpooling.pooling.hmix.state_probability", state_probability)
    monkeypatch.setattr("evtpooling.pooling.hmix.non_parametric_density", non_parametric_density)

    alpha_list, true_pi, true_phi = known_mixture_data
    num_clusters = 2
    # theta_int = ([0.5, 0.5], [(1.0, 0.2), (2.5, 0.5)])  # Initial guess for theta

    pi_est, phi_est = hmix_func(
        alpha_list=alpha_list, num_clusters=num_clusters, threshold=1e-6, max_iter=50, plot=False
    )

    # Sort estimated and true components by mean for comparison
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
        assert np.isclose(sigma_e, sigma_t, atol=0.15), f"Std mismatch: {sigma_e} vs {sigma_t}"

    print("Test passed: Estimated parameters are close to the true mixture components.")
