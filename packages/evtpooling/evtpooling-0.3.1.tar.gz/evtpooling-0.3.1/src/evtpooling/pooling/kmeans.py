import colorsys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans

from evtpooling.utils import calculate_alpha_var, get_alpha_dict


def kmeans_clustering(
    losses: pd.DataFrame, k_threshold: int, k_range: np.ndarray, plot_inertia: bool = False
) -> None:
    """
    Perform KMeans clustering on the 1D loss data and plot the inertia for each k value.

    Parameters
    ----------
    losses : pd.DataFrame
        A DataFrame containing loss values indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.
    k_range : np.ndarray
        An array of integers representing the range of k values for clustering.
    plot_inertia : bool, optional
        If True, plot the inertia for each k value. Default is False.

    Returns
    -------
    None
        This function computes the inertia for KMeans clustering across a range of k values"""
    np.random.seed(567233)
    intertias = []

    alpha_dict = get_alpha_dict(losses, k_threshold=k_threshold)
    samples = np.array(list(alpha_dict.values())).reshape(-1, 1)

    for k in k_range:
        model = KMeans(n_clusters=k).fit(samples)
        intertias.append(model.inertia_)

    if plot_inertia:
        sns.set_style("whitegrid")
        g = sns.relplot(
            x=k_range, y=intertias, kind="line", linestyle="-", marker="o", height=8, aspect=1.5
        )
        ax = g.ax
        ax.set_xlabel("Number of Clusters (k)", fontsize=14)
        ax.set_ylabel("Inertia", fontsize=14)
        ax.set_title("KMeans Inertia vs Number of Clusters", fontsize=16)
        ax.tick_params(axis="x", labelsize=12)
        ax.tick_params(axis="y", labelsize=12)
        ax.set_xticks(k_range)
        plt.tight_layout()
        plt.show()


def kmeans_plot(
    losses: pd.DataFrame, k_threshold: int, k_range: np.ndarray, plot_inertia: bool = False
) -> None:
    """
    For each k in k_range, perform KMeans clustering on the 1D loss data
    and plot the clustered points and centroids with distinct colors.

    Parameters
    ----------
    losses : pd.DataFrame
        A DataFrame containing loss values indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.
    k_range : np.ndarray
        An array of integers representing the range of k values for clustering.
    plot_inertia : bool, optional
        If True, plot the inertia for each k value. Default is False.

    Returns
    -------
    None
    This function displays an interactive plot where the user can navigate through
    the clustering results using the left and right arrow keys.
    It also calls `kmeans_clustering` to compute and plot inertia if `plot_inertia` is True.
    """
    alpha_dict = get_alpha_dict(losses, k_threshold=k_threshold)
    data = np.array(list(alpha_dict.values())).reshape(-1, 1)

    # Precompute all clustering results
    clustering_results = []
    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42).fit(data)
        labels = model.predict(data)
        centroids = model.cluster_centers_
        clustering_results.append((k, labels, centroids))

    # Initialize plot
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.15)
    plt.ion()

    max_k = max(k_range)
    hues = np.linspace(0, 1, max_k + 1)[:-1]
    colors = [colorsys.hsv_to_rgb(h, 0.8, 0.8) for h in hues]

    scatter_plots = []
    centroid_plots = []
    for i in range(max_k):
        (scatter,) = ax.plot([], [], "x", color=colors[i], label=f"Cluster {i + 1}", markersize=10)
        (centroid,) = ax.plot([], [], "o", color=colors[i], markeredgecolor="k", markersize=12)
        scatter_plots.append(scatter)
        centroid_plots.append(centroid)

    ax.set_xlim(data.min() - 0.1, data.max() + 0.1)
    ax.tick_params(axis="x", labelsize=16)
    ax.tick_params(axis="y", labelsize=16)
    ax.set_ylim(-0.5, 0.5)

    current_index = 0

    def update_plot(idx):
        k, labels, centroids = clustering_results[idx]
        ax.set_title(f"KMeans Clustering (k = {k})", fontsize=16)

        for i in range(max_k):
            if i < k:
                cluster_points = data[labels == i].flatten()
                scatter_plots[i].set_data(cluster_points, np.zeros_like(cluster_points))
                centroid_plots[i].set_data([centroids[i, 0]], [0])
            else:
                scatter_plots[i].set_data([], [])
                centroid_plots[i].set_data([], [])

        fig.canvas.draw()

    def on_key(event):
        nonlocal current_index
        if event.key == "right":
            current_index = (current_index + 1) % len(k_range)
            update_plot(current_index)
        elif event.key == "left":
            current_index = (current_index - 1) % len(k_range)
            update_plot(current_index)

    fig.canvas.mpl_connect("key_press_event", on_key)

    update_plot(current_index)
    plt.ioff()
    plt.show(block=False)  # Keep last figure open until user closes it

    kmeans_clustering(
        losses=losses, k_threshold=k_threshold, k_range=k_range, plot_inertia=plot_inertia
    )


def kmeans_pooling(losses: pd.DataFrame, k_threshold: int, num_clusters: int) -> pd.DataFrame:
    """
    Perform KMeans clustering on the 1D loss data and return a DataFrame with
    the clustered alpha values and their VaR.

    Parameters
    ----------
    losses : pd.DataFrame
        A DataFrame containing loss values indexed by stock identifiers.
    k_threshold : int
        The number of top losses to consider for the Hill estimator calculation.
    num_clusters : int
        The number of clusters to form in the KMeans algorithm.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the KMeans clustered alpha values and their corresponding VaR.
    """
    alpha_dict = get_alpha_dict(losses, k_threshold=k_threshold)
    data = np.array(list(alpha_dict.values())).reshape(-1, 1)

    model = KMeans(n_clusters=num_clusters, random_state=42).fit(data)
    labels = model.predict(data)
    centroids = model.cluster_centers_
    df_pooling = pd.DataFrame(index=alpha_dict.keys())

    df_pooling["kmeans_alpha"] = [centroids[labels[i]][0] for i in range(len(alpha_dict))]
    df_pooling["kmeans_var"] = [
        calculate_alpha_var(
            losses=losses[index], k_threshold=k_threshold, alpha_hat=centroids[labels[i]][0]
        )[1]
        for i, index in enumerate(losses.columns)
    ]

    return df_pooling
