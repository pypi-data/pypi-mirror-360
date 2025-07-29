# flake8: noqa: E501

import matplotlib.pyplot as plt
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.manifold import TSNE
import numpy as np


def visualize_clusters(X, labels, method='pca', title='Cluster Visualization', view_index=None):
    """
    Visualize clustering results using PCA, SVD, or t-SNE.

    Args:
        X (array-like or list of arrays): Feature data or multi-view data.
        labels (array-like): Predicted labels.
        method (str): 'pca', 'svd', or 'tsne'.
        title (str): Title of the plot.
        view_index (int or None): If X is multi-view, choose which view to plot (None = concatenate all views).
    """
    if isinstance(X, list):  # Multi-view
        if view_index is not None:
            X_plot = X[view_index]
        else:
            X_plot = np.concatenate(X, axis=1)
    else:
        X_plot = X

    # Dimensionality reduction
    if method == 'pca':
        reducer = PCA(n_components=2)
    elif method == 'svd':
        reducer = TruncatedSVD(n_components=2)
    elif method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42)
    else:
        raise ValueError("Method must be 'pca', 'svd' or 'tsne'")

    reduced = reducer.fit_transform(X_plot)

    # Plotting
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10', s=30, alpha=0.8)
    plt.title(title)
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.colorbar(scatter, label='Cluster ID')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
