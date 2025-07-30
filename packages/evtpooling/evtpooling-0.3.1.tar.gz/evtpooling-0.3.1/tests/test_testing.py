import numpy as np
import pandas as pd
import pytest

from evtpooling import chenzhou, get_pairwise_df, wald_test
from evtpooling.utils import get_alpha_dict


@pytest.fixture
def dummy_losses():
    np.random.seed(42)
    data = {
        "A": np.random.pareto(a=3.0, size=200) + 1,
        "B": np.random.pareto(a=2.5, size=200) + 1,
        "C": np.random.pareto(a=2.8, size=200) + 1,
    }
    return pd.DataFrame(data)


# --------------------
# Tests
# --------------------


def test_get_alpha_dict(dummy_losses):
    alpha_dict = get_alpha_dict(dummy_losses, k_threshold=50)
    assert isinstance(alpha_dict, dict)
    assert len(alpha_dict) == 3
    assert all(v > 0 for v in alpha_dict.values())
    for key, value in alpha_dict.items():
        assert isinstance(key, str)
        assert isinstance(value, float)


def test_get_alpha_dict_too_large_k(dummy_losses):
    with pytest.raises(
        ValueError, match="k_threshold must be less than the number of observations"
    ):
        get_alpha_dict(dummy_losses, k_threshold=1000)


def test_chenzhou():
    alpha_list = [1.5, 1.6, 1.55, 1.52]
    common_alpha = np.mean(alpha_list)
    stat, pval = chenzhou(alpha_list, common_alpha, k_threshold=50)
    assert isinstance(stat, float)
    assert isinstance(pval, float)
    assert 0 <= pval <= 1


@pytest.mark.parametrize(
    "alpha_list, common_alpha",
    [
        ([], 1.5),
        ([1.2, 1.3], 0),  # zero common_alpha
    ],
)
def test_chenzhou_invalid_inputs(alpha_list, common_alpha):
    with pytest.raises(ValueError):
        chenzhou(alpha_list, common_alpha, k_threshold=50)


def test_get_pairwise_df(dummy_losses):
    df = get_pairwise_df(dummy_losses, k_threshold=50)
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == df.shape[1]
    assert df.index.equals(df.columns)
    np.testing.assert_array_less(df.values, np.ones(df.shape) + 1e-6)
    np.testing.assert_array_less(-1e-6 * np.ones(df.shape), df.values)  # All values > 0


def test_pairwise_df_invalid_k(dummy_losses):
    with pytest.raises(
        ValueError, match="k_threshold must be less than the number of observations."
    ):
        get_pairwise_df(dummy_losses, k_threshold=500)


def test_wald_test(dummy_losses):
    alpha_list = [1.5, 1.6, 1.55]
    common_alpha = np.mean(alpha_list)
    stat, pval = wald_test(dummy_losses, alpha_list, common_alpha, k_threshold=50)
    assert isinstance(stat, float)
    assert isinstance(pval, float)
    assert 0 <= pval <= 1


def test_wald_test_invalid_inputs(dummy_losses):
    with pytest.raises(ValueError):
        wald_test(dummy_losses, [], common_alpha=1.5, k_threshold=50)
    with pytest.raises(ValueError):
        wald_test(dummy_losses, [1.5, 1.6], common_alpha=0, k_threshold=50)
