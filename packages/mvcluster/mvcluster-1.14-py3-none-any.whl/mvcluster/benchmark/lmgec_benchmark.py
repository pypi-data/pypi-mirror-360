"""
Module for running LMGEC clustering experiments.

This module provides the `run_lmgec_experiment` function to perform clustering
experiments using the LMGEC algorithm across specified datasets. It includes
functionality for preprocessing views, training the model, and computing
evaluation metrics. It also provides a command-line interface for configuring
experiment parameters.
"""

import argparse
from time import time
from itertools import product

import numpy as np
from sklearn.metrics import adjusted_rand_score as ari
from sklearn.metrics.cluster import normalized_mutual_info_score as nmi
from sklearn.preprocessing import StandardScaler

from ..cluster.lmgec import LMGEC
from ..utils.datagen import datagen
from ..utils.metrics import (
    clustering_accuracy,
    clustering_f1_score,
)
from ..utils.preprocess import preprocess_dataset


def run_lmgec_experiment(
    dataset: str,
    temperature: float = 1.0,
    beta: float = 1.0,
    max_iter: int = 10,
    tolerance: float = 1e-7,
    runs: int = 1,
) -> dict:
    """
    Run the LMGEC clustering experiment for a given dataset.

    :param dataset: Name of the dataset to load (e.g., 'acm', 'dblp').
    :param temperature: Temperature parameter for the LMGEC model.
    :param beta: Beta parameter used during preprocessing.
    :param max_iter: Maximum number of iterations for convergence.
    :param tolerance: Convergence threshold for the model.
    :param runs: Number of runs to average the metrics.
    :returns: A dict containing mean and std of evaluation metrics.
    """
    print(f"Running on dataset: {dataset}")
    As, Xs, labels = datagen(dataset)
    k = len(np.unique(labels))
    views = list(product(As, Xs))

    for idx, (A, X) in enumerate(views):
        use_tfidf = dataset in ["acm", "dblp", "imdb", "photos"]
        norm_adj, feats = preprocess_dataset(
            A, X, tf_idf=use_tfidf, beta=int(beta)
        )
        arr = (
            feats.toarray()
            if not isinstance(feats, np.ndarray)
            and hasattr(feats, "toarray")
            else feats
        )
        views[idx] = (np.asarray(norm_adj), arr)

    metrics = {m: [] for m in ["acc", "nmi", "ari", "f1", "loss", "time"]}

    for _ in range(runs):
        t0 = time()
        Hs = [
            StandardScaler(with_std=False).fit_transform(S @ X)
            for S, X in views
        ]

        model = LMGEC(
            n_clusters=k,
            embedding_dim=k + 1,
            temperature=temperature,
            max_iter=max_iter,
            tolerance=tolerance,
        )
        model.fit(Hs)

        metrics["time"].append(time() - t0)
        metrics["acc"].append(clustering_accuracy(labels, model.labels_))
        metrics["nmi"].append(nmi(labels, model.labels_))
        metrics["ari"].append(ari(labels, model.labels_))
        metrics["f1"].append(
            clustering_f1_score(
                labels, model.labels_, average="macro"
            )
        )
        metrics["loss"].append(model.loss_history_[-1])  # type: ignore

    results = {
        "mean": {k: round(np.mean(v), 4) for k, v in metrics.items()},
        "std": {k: round(np.std(v), 4) for k, v in metrics.items()},
    }

    print("ACC & F1 & NMI & ARI:")
    print(
        results["mean"]["acc"],
        results["mean"]["f1"],
        results["mean"]["nmi"],
        results["mean"]["ari"],
        sep=" & ",
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run LMGEC clustering experiments via CLI."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="acm",
        help="Dataset to load (e.g., acm, dblp, imdb, photos, wallomics).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Temperature for the LMGEC model.",
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=1.0,
        help="Beta for preprocessing.",
    )
    parser.add_argument(
        "--max_iter",
        type=int,
        default=10,
        help="Max iterations for convergence.",
    )
    parser.add_argument(
        "--tol",
        type=float,
        default=1e-7,
        help="Tolerance threshold.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs to average.",
    )
    args = parser.parse_args()

    run_lmgec_experiment(
        dataset=args.dataset,
        temperature=args.temperature,
        beta=args.beta,
        max_iter=args.max_iter,
        tolerance=args.tol,
        runs=args.runs,
    )
