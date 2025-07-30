import numpy as np
import pandas as pd
import pandas.testing as pdt
import pytest
from scipy.stats import t

from evtpooling.alpha import *
from evtpooling.constants import *

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def valid_df():
    """Fully valid dataframe fixture"""
    np.random.seed(567233)

    data = {
        "Student-t": t.rvs(size=500, df=5, loc=0, scale=1),
        "Exponential": np.random.exponential(scale=1, size=500),
        "Uniform": np.random.uniform(low=0, high=1, size=500),
    }

    valid_df = pd.DataFrame(data)
    valid_df.set_index(pd.date_range(START_DATE, periods=500, freq="D"), inplace=True)

    return valid_df


@pytest.fixture
def normal_df():
    """Dataframe fixture with normal distribution"""
    np.random.seed(567233)

    data = {
        "Normal1": np.random.normal(loc=0, scale=1, size=500),
        "Normal2": np.random.normal(loc=5, scale=2, size=500),
        "Normal3": np.random.normal(loc=-3, scale=1.5, size=500),
        "Student-t": t.rvs(size=500, df=5, loc=0, scale=1),
    }

    normal_df = pd.DataFrame(data)
    normal_df.set_index(pd.date_range(START_DATE, periods=500, freq="D"), inplace=True)

    return normal_df


@pytest.fixture
def autocorrelated_unit_root_df():
    """Dataframe with autocorrelated data"""
    np.random.seed(567233)

    data = {
        "Dep1": [x + i for i in range(100) for x in [1, 5, 3, 9, 6]],
        "Dep2": [x + i for i in range(250) for x in [4, 7]],
        "Non-dep": np.random.normal(loc=0, scale=1, size=500),
    }

    autocorrelated_df = pd.DataFrame(data)
    autocorrelated_df.set_index(pd.date_range(START_DATE, periods=500, freq="D"), inplace=True)

    return autocorrelated_df


# --------------------
# Tests
# --------------------


def test_valid_df(valid_df):
    tested_df = valid_df.copy()
    p_value = 0.05
    normality_test(tested_df, drop=True, p_threshold=p_value)
    autocorrelation_test(tested_df, drop=True, p_threshold=p_value)
    stationarity_test(tested_df, drop=True, p_threshold=p_value)

    # Check that valid_df (original fixture) is unchanged
    pdt.assert_frame_equal(valid_df, tested_df)

    assert not tested_df.empty


def test_normal_df(normal_df):
    tested_df = normal_df.copy()
    normality_test(tested_df, drop=True, p_threshold=0.05)

    assert tested_df.shape[1] == 1
    assert "Student-t" in tested_df.columns


def test_autocorrelated_df(autocorrelated_unit_root_df):
    tested_df = autocorrelated_unit_root_df.copy()
    autocorrelation_test(tested_df, drop=True, p_threshold=0.05)

    assert tested_df.shape[1] == 1
    assert "Non-dep" in tested_df.columns


def test_unit_root_df(autocorrelated_unit_root_df):
    tested_df = autocorrelated_unit_root_df.copy()
    stationarity_test(tested_df, drop=True, p_threshold=0.05)
    print(tested_df)

    assert tested_df.shape[1] == 2
    assert "Dep1" and "Non-dep" in tested_df.columns
