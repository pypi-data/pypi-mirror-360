import numpy as np
import pandas as pd
import pytest
from scipy.stats import pareto

from evtpooling import kmeans_pooling

# --------------------
# Fixtures (mock data)
# --------------------


@pytest.fixture
def mock_losses():
    """
    Generate mock losses data for testing KMeans pooling.
    The data consists of Pareto-distributed losses for three different clusters
    """
    data = pd.DataFrame(
        {
            "losses1_2": pareto.rvs(b=2, scale=1, size=830),
            "losses2_2": pareto.rvs(b=2, scale=1, size=830),
            "losses3_2": pareto.rvs(b=2, scale=1, size=830),
            "losses1_3": pareto.rvs(b=3, scale=1, size=830),
            "losses2_3": pareto.rvs(b=3, scale=1, size=830),
            "losses3_3": pareto.rvs(b=3, scale=1, size=830),
            "losses1_4": pareto.rvs(b=4, scale=1, size=830),
            "losses2_4": pareto.rvs(b=4, scale=1, size=830),
            "losses3_4": pareto.rvs(b=4, scale=1, size=830),
        }
    )

    return data


# --------------------
# Tests
# --------------------


def test_kmeans_pooling(mock_losses):
    """Test the kmeans_pooling function to ensure it correctly clusters losses"""
    df_pooling = kmeans_pooling(mock_losses, k_threshold=80, num_clusters=3)

    assert df_pooling["kmeans_alpha"].nunique() == 3

    s_sorted = (df_pooling["kmeans_alpha"]).value_counts(ascending=True).to_numpy()
    expected_sorted = np.array([2, 3, 4])

    assert np.all(np.isclose(s_sorted, expected_sorted, rtol=0.01)), (
        "KMeans alpha values do not match expected clusters"
    )
