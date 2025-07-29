"""
Initialization utilities for LMGEC clustering.

This module provides functions to initialize cluster assignments,
centroids, and view-specific projection matrices required by the
LMGEC algorithm.

Functions:
- init_G_F: initialize cluster labels and centroids using KMeans.
- init_W: initialize projection matrix via truncated SVD.
"""

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD


def init_G_F(
    XW: np.ndarray,
    k: int,
) -> tuple:  # noqa: E402
    """
    Initialize cluster assignments G and centroids F using KMeans.

    :param XW: Array [n_samples, embedding_dim], data to cluster.
    :param k: Number of clusters.
    :returns: Tuple (G, F) where:
        - G: 1D array of length n_samples, initial cluster labels.
        - F: 2D array [k, embedding_dim], initial cluster centroids.
    :rtype: (np.ndarray, np.ndarray)
    """
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(XW)
    return kmeans.labels_, kmeans.cluster_centers_


def init_W(
    X: np.ndarray,
    f: int,
) -> np.ndarray:
    """
    Initialize projection matrix W using truncated SVD.

    :param X: Array [n_samples, n_features], input data matrix.
    :param f: Target embedding dimension.
    :returns: Projection matrix [n_features, f].
    :rtype: np.ndarray
    """
    n_features = X.shape[1]
    n_components = min(f, n_features)
    svd = TruncatedSVD(n_components=n_components)
    svd.fit(X)
    W = svd.components_.T  # shape: [f, n_components]

    # Pad with zeros if too small
    if n_components < f:
        pad_width = f - n_components
        W = np.pad(W, ((0, 0), (0, pad_width)), mode='constant')

    return W  # always [n_features, f]
