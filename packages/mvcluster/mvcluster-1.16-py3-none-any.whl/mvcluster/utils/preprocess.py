"""
Dataset preprocessing utilities for LMGEC experiments.

This module provides functions to normalize adjacency matrices and feature
matrices, with optional TF-IDF transformation. Adjacency normalization adds
self-loops scaled by a beta parameter and row-normalizes the result.

Functions:
- preprocess_dataset: normalize adjacency and features.
"""

import scipy.sparse as sp
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.feature_extraction.text import TfidfTransformer


def preprocess_dataset(
    adj: sp.spmatrix,
    features: np.ndarray,
    tf_idf: bool = False,
    beta: float = 1.0,
) -> tuple:
    """
    Preprocess adjacency and feature matrices for clustering.

    The adjacency matrix is augmented with self-loops scaled by beta, then
    row-normalized. Features are either TF-IDF transformed or L2-normalized.

    :param adj: Sparse adjacency matrix [n_samples, n_samples].
    :param features: Dense or sparse features [n_samples, n_features].
    :param tf_idf: If True, apply TF-IDF; otherwise apply L2 normalization.
    :param beta: Scaling factor for self-loop augmentation.
    :returns: (adj_normalized, features_processed)
    :rtype: (sp.spmatrix, np.ndarray or sp.spmatrix)
    """
    # Add self-loops scaled by beta
    adj = adj + beta * sp.eye(adj.shape[0], format="csr")

    # Compute row sums and inverse for normalization
    rowsum = np.array(adj.sum(1)).flatten()  # type: ignore
    r_inv = np.power(rowsum, -1, where=rowsum != 0)
    r_inv[np.isinf(r_inv)] = 0.0
    r_mat_inv = sp.diags(r_inv)

    # Row-normalize adjacency
    adj_normalized = r_mat_inv.dot(adj)

    # Process features: TF-IDF or L2 normalization
    if tf_idf:
        transformer = TfidfTransformer(norm="l2")
        features_processed = transformer.fit_transform(features)
    else:
        features_processed = normalize(features, norm="l2")

    return adj_normalized, features_processed
