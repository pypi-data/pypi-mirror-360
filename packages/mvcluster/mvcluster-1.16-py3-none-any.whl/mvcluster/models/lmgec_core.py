"""
LMGEC core optimization routines.

This module implements the update rules and alternating optimization loop
used by the Localized Multi-Graph Embedding Clustering algorithm.
Functions:
- update_rule_F: update cluster centroids.
- update_rule_W: update view-specific projection.
- update_rule_G: assign cluster labels.
- train_loop: perform alternating optimization.
"""

import tensorflow as tf  # type: ignore


def update_rule_F(
    XW: tf.Tensor,
    G: tf.Tensor,
    k: int,
) -> tf.Tensor:
    """
    Update centroids by mean of embeddings per cluster.

    :param XW: Tensor [n_samples, emb_dim], embeddings.
    :param G: Tensor [n_samples], cluster assignments.
    :param k: Number of clusters.
    """
    return tf.math.unsorted_segment_mean(XW, G, k)


def update_rule_W(
    X: tf.Tensor,
    F: tf.Tensor,
    G: tf.Tensor,
) -> tf.Tensor:
    """
    Update projection matrix via orthogonal Procrustes.

    :param X: Tensor [n_samples, n_features].
    :param F: Tensor [n_samples, emb_dim], centroids.
    :param G: Tensor [n_samples], cluster assignments.
    """
    M = tf.transpose(X) @ tf.gather(F, G)
    _, U, V = tf.linalg.svd(M, full_matrices=False)
    return U @ tf.transpose(V)


def update_rule_G(
    XW: tf.Tensor,
    F: tf.Tensor,
) -> tf.Tensor:
    """
    Assign samples to nearest centroid.

    :param XW: Tensor [n_samples, emb_dim], embeddings.
    :param F: Tensor [k, emb_dim], centroids.
    """
    cent = F[:, None, ...]  # type: ignore
    dist = tf.reduce_mean(
        tf.math.squared_difference(XW, cent),
        axis=2,
    )
    return tf.math.argmin(dist, axis=0, output_type=tf.int32)


def train_loop(
    Xs: list,
    F: tf.Tensor,
    G: tf.Tensor,
    alphas: list,
    k: int,
    max_iter: int,
    tolerance: float,
) -> tuple:
    """
    Alternating optimization for LMGEC.

    :param Xs: List of view matrices.
    :param F: Tensor [k, emb_dim], initial centroids.
    :param G: Tensor [n_samples], initial labels.
    :param alphas: List of view weights.
    :param k: Number of clusters.
    :param max_iter: Max iterations.
    :param tolerance: Convergence threshold.
    :returns: (G, F, XW_consensus, losses)
    """

    n_views = len(Xs)
    n_samples = Xs[0].shape[0]
    emb_dim = F.shape[1]

    losses = []
    prev = float("inf")

    for _ in range(max_iter):
        loss = 0.0
        XW_cons = tf.zeros((n_samples, emb_dim), tf.float64)

        for v in range(n_views):
            Xv = tf.cast(Xs[v], tf.float64)
            Wv = update_rule_W(Xv, F, G)  # type: ignore
            XWv = tf.matmul(Xv, Wv)
            XW_cons += alphas[v] * XWv

            Fg = tf.gather(F, G)
            recon = tf.matmul(Fg, tf.transpose(Wv))
            loss += alphas[v] * tf.norm(Xv - recon)

        G = update_rule_G(XW_cons, F)
        F = update_rule_F(XW_cons, G, k)

        losses.append(loss.numpy())  # type: ignore
        if abs(prev - loss) < tolerance:
            break
        prev = loss

    return (
        G,
        F,
        XW_cons,  # type: ignore
        tf.convert_to_tensor(losses, tf.float64),  # type: ignore
    )
