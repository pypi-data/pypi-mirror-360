"""
Dataset loader utilities for LMGEC experiments.

This module provides functions to load and preprocess multiple benchmark
datasets stored in MATLAB .mat files. Each function returns adjacency
matrices (As), feature matrices (Xs), and ground-truth labels.

Available datasets:
- acm, dblp, imdb, photos, wiki
- `datagen(dataset)` dispatches to the appropriate loader.
"""

import os
import numpy as np
from scipy import io
from sklearn.neighbors import kneighbors_graph


def _load_mat_file(filename: str) -> dict:
    """
    Load a MATLAB .mat file from the data directory.

    :param filename: Name of the .mat file to load.
    :raises FileNotFoundError: If the file does not exist.
    :returns: Variables loaded from the .mat file.
    """
    data_dir = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "datasets",
            "data_lmgec",
        )
    )
    data_path = os.path.join(data_dir, filename)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"File not found: {data_path}")
    print(f"Loading data file: {data_path}")
    return io.loadmat(data_path)


def acm() -> tuple:
    """
    Load the ACM dataset.

    :returns: Tuple (As, Xs, labels):
        - As: list of adjacency matrices (PAP, PLP).
        - Xs: list with feature matrix.
        - labels: 1D array of ground-truth labels.
    """
    data = _load_mat_file("ACM.mat")
    X = data["features"]
    A = data["PAP"]
    B = data["PLP"]

    Xs = [X.toarray()]
    As = [A.toarray(), B.toarray()]
    labels = data["label"].reshape(-1)
    return As, Xs, labels


def dblp() -> tuple:
    """
    Load the DBLP dataset.

    :returns: Tuple (As, Xs, labels):
        - As: list of adjacency matrices (net_APTPA, net_APCPA, net_APA).
        - Xs: list with feature matrix.
        - labels: 1D array of labels.
    """
    data = _load_mat_file("DBLP.mat")
    X = data["features"]
    A = data["net_APTPA"]
    B = data["net_APCPA"]
    C = data["net_APA"]

    Xs = [X.toarray()]
    As = [A.toarray(), B.toarray(), C.toarray()]
    labels = data["label"].reshape(-1)
    return As, Xs, labels


def imdb() -> tuple:
    """
    Load the IMDB dataset.

    :returns: Tuple (As, Xs, labels):
        - As: list of adjacency matrices (MAM, MDM).
        - Xs: list with feature matrix.
        - labels: 1D array of labels.
    """
    data = _load_mat_file("IMDB.mat")
    X = data["features"]
    A = data["MAM"]
    B = data["MDM"]

    Xs = [X.toarray()]
    As = [A.toarray(), B.toarray()]
    labels = data["label"].reshape(-1)
    return As, Xs, labels


def photos() -> tuple:
    """
    Load Amazon Photos dataset and compute additional view.

    :returns: Tuple (As, Xs, labels):
        - As: list with adjacency matrix.
        - Xs: list of feature matrix and similarity view.
        - labels: 1D array of labels.
    """
    data = _load_mat_file("Amazon_photos.mat")
    X = data["features"]
    A = data["adj"]
    labels = data["label"].reshape(-1)

    X = X.toarray() if hasattr(X, "toarray") else np.asarray(X)
    A = A.toarray() if hasattr(A, "toarray") else np.asarray(A)

    try:
        X2 = X @ X.T
    except Exception as e:
        print(f"Warning: failed to compute X @ X.T: {e}")
        X2 = X

    Xs = [X, X2]
    As = [A]
    return As, Xs, labels


def wiki() -> tuple:
    """
    Load the Wiki dataset and build a KNN graph.

    :returns: Tuple (As, Xs, labels):
        - As: list with adjacency and KNN graph.
        - Xs: list of features and log-transformed features.
        - labels: 1D array of labels.
    :raises ValueError: If adjacency 'W' is missing.
    """
    data = _load_mat_file("wiki.mat")
    X = data["fea"]
    X = X.toarray() if hasattr(X, "toarray") else X
    X = X.astype(float)

    A = data.get("W")
    if A is None:
        raise ValueError("Adjacency matrix 'W' not found in wiki.mat")
    A = A.toarray() if hasattr(A, "toarray") else A

    knn = kneighbors_graph(X, n_neighbors=5, metric="cosine")
    knn = knn.toarray() if hasattr(knn, "toarray") else knn  # type: ignore

    Xs = [X, np.log2(1 + X)]
    As = [A, knn]
    labels = data["gnd"].reshape(-1)
    return As, Xs, labels


def datagen(dataset: str) -> tuple:
    """
    Dispatch to the appropriate dataset loader.

    :param dataset: Name of dataset.
    :returns: Tuple (As, Xs, labels).
    :raises ValueError: If dataset is unknown.
    """
    loaders = {
        "acm": acm,
        "dblp": dblp,
        "imdb": imdb,
        "photos": photos,
        "wiki": wiki,
    }
    try:
        return loaders[dataset]()
    except KeyError:
        raise ValueError(f"Unknown dataset: {dataset}")
