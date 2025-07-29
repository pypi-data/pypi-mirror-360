"""
[EN]
This script benchmarks the LMGEC (Localized Multi-View Graph Embedding
Clustering) algorithm on custom multi-view datasets stored in .mat files. It
supports various .mat file formats commonly used to represent multi-view data
with adjacency matrices and feature matrices for each view, along with
optional ground truth cluster labels.

Main features and workflow:

1. Data Loading:
   - Supports multiple data formats within .mat files, including keys such as
     'X_i'/'A_i', 'X1', 'features', 'views', or special cases like 'fea', 'W',
     and 'gnd'.
   - Returns a list of (adjacency matrix, feature matrix) tuples for each view,
     and the ground truth labels.

2. Data Preprocessing:
   - Normalizes adjacency matrices and preprocesses feature matrices for each
     view.
   - Handles sparse and dense matrix formats gracefully.

3. Single Run Clustering Evaluation:
   - Applies LMGEC clustering on the processed multi-view data.
   - Projects and normalizes features before clustering.
   - Computes evaluation metrics: Accuracy, Normalized Mutual Information
   (NMI),Adjusted Rand Index (ARI), and macro-averaged F1 score.

4. Hyperparameter Tuning:
   - Explores combinations of temperature, beta (graph regularization), and
     embedding dimensionality.
   - Runs clustering multiple times with these parameters to identify optimal
     configurations.
   - Saves results to CSV and produces line plots visualizing metric trends vs
     temperature, grouped by beta and embedding dimension.

5. Command-Line Interface:
   - Accepts parameters including path to .mat dataset, expected number of
     clusters, maximum iterations, and convergence tolerance.

Dependencies:
- mvcluster package for LMGEC, clustering metrics, and preprocessing utilities.
- Standard scientific Python packages: numpy, scipy, scikit-learn, pandas,
  matplotlib, seaborn.

Usage example:
    python tune_hyperparams.py --data_file path/to/data.mat --n_clusters 3 \
--max_iter 50 --tolerance 1e-7

[FR]
Ce script évalue l’algorithme LMGEC (Localized Multi-View Graph Embedding
Clustering) sur des jeux de données multi-vues personnalisés au format .mat. Il
prend en charge divers formats .mat utilisés pour représenter des données
multi-vues avec des matrices d’adjacence et des matrices de caractéristiques
pour chaque vue, ainsi que les étiquettes de vérité terrain optionnelles.

Fonctionnalités principales et déroulement :

1. Chargement des données :
- Supporte plusieurs formats de fichiers .mat, incluant les clés 'X_i'/'A_i',
'X1', 'features', 'views', ou des cas spécifiques comme 'fea', 'W' et 'gnd'.
- Retourne une liste de tuples (matrice d’adjacence, matrice de
caractéristiques) pour chaque vue, ainsi que les étiquettes de vérité
terrain.

2. Prétraitement des données :
   - Normalise les matrices d’adjacence et prépare les matrices de
     caractéristiques pour chaque vue.
   - Gère correctement les formats matriciels creux (sparse) et denses.

3. Évaluation d’une exécution de clustering :
   - Applique LMGEC sur les données multi-vues prétraitées.
   - Projette et normalise les caractéristiques avant le clustering.
   - Calcule les métriques d’évaluation : précision (Accuracy), information
     mutuelle normalisée (NMI), indice de Rand ajusté (ARI), et score F1
     macro-moyenné.

4. Recherche d’hyperparamètres :
   - Explore différentes combinaisons de température, beta (régularisation du
     graphe) et dimension d’embedding.
   - Exécute plusieurs fois le clustering avec ces paramètres pour identifier
     les configurations optimales.
   - Sauvegarde les résultats dans un fichier CSV et génère des graphiques
     montrant l’évolution des métriques en fonction de la température, groupés
     par beta et dimension d’embedding.

5. Interface en ligne de commande :
   - Prend en entrée le chemin du fichier .mat, le nombre attendu de clusters,
     le nombre maximal d’itérations, et la tolérance de convergence.

Dépendances :
- Package mvcluster pour LMGEC, métriques de clustering, et utilitaires de
  prétraitement.
- Packages scientifiques Python standards : numpy, scipy, scikit-learn, pandas,
  matplotlib, seaborn.

Exemple d’utilisation :
python tune_hyperparams.py --data_file chemin/vers/data.mat --n_clusters 3 \
--max_iter 50 --tolerance 1e-7
"""


import argparse  # noqa: 303 
import itertools
import os
from typing import List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import normalized_mutual_info_score as nmi
from sklearn.metrics import adjusted_rand_score as ari
from scipy.io import loadmat

from mvcluster.cluster.lmgec import LMGEC
from mvcluster.utils.metrics import clustering_accuracy, clustering_f1_score
from mvcluster.utils.preprocess import preprocess_dataset


def load_custom_mat(
    path: str,
) -> Tuple[List[Tuple[np.ndarray, np.ndarray]], Optional[np.ndarray]]:
    """
    Load various possible .mat file formats with views and labels.

    Returns:
        views: list of (A, X) tuples
        labels: ndarray or None
    """
    from scipy.sparse import issparse

    mat = loadmat(path)
    Xs, As = [], []
    labels = None
    if "labels" in mat:
        labels = mat["labels"].squeeze()
    elif "label" in mat:
        labels = mat["label"].squeeze()
    if labels is not None and labels.ndim != 1:
        labels = labels.ravel()
    if labels is not None and not isinstance(labels, np.ndarray):
        labels = np.array(labels)

    # Format 1: X_0, A_0, ...
    i = 0
    while f"X_{i}" in mat and f"A_{i}" in mat:
        Xs.append(mat[f"X_{i}"])
        As.append(mat[f"A_{i}"].astype(np.float32))
        i += 1
    if Xs:
        return list(zip(As, Xs)), labels

    # Format 2: X1, X2, ...
    i = 1
    while f"X{i}" in mat:
        X = mat[f"X{i}"]
        A = np.eye(X.shape[0], dtype=np.float32)
        Xs.append(X)
        As.append(A)
        i += 1
    if Xs:
        return list(zip(As, Xs)), labels

    # Format 3: 'features' or 'views' as array or sparse
    for key in ("features", "views"):
        if key in mat:
            value = mat[key]

            # Case: single sparse matrix
            if issparse(value):
                X = value
                A = np.eye(X.shape[0], dtype=np.float32)
                return [(A, X)], labels

            # Case: list of views
            try:
                raw_views = value[0]
                for view in raw_views:
                    X = view
                    if issparse(X):
                        X = X.tocsr()
                    A = np.eye(X.shape[0], dtype=np.float32)
                    Xs.append(X)
                    As.append(A)
                if Xs:
                    return list(zip(As, Xs)), labels
            except Exception as e:
                raise ValueError(f"Unsupported format under key '{key}': {e}")
    # New case for wiki.mat format with 'fea', 'W', and 'gnd' keys
    if "fea" in mat and "W" in mat:
        X = mat["fea"]
        A = mat["W"].astype(np.float32)
        Xs.append(X)
        As.append(A)
        if "gnd" in mat:
            labels = mat["gnd"].squeeze()
            if labels.ndim != 1:
                labels = labels.ravel()
            if not isinstance(labels, np.ndarray):
                labels = np.array(labels)  # noqa: E291
        return list(zip(As, Xs)), labels

    raise ValueError(
        "Unsupported .mat file structure. "
        "Expected 'X_0'/'A_0', 'X1', 'features', or 'views'."
    )


def run_once(
    views: List[Tuple[np.ndarray, np.ndarray]],
    labels: np.ndarray,
    dim: int,
    temp: float,
    beta: float,
    max_iter: int,
    tol: float,
) -> dict:
    """
    Run a single LMGEC clustering evaluation with specified hyperparameters.

    Args:
        views: List of (A, X) tuples:
            A (ndarray): Adjacency matrix (n_samples, n_samples).
            X (ndarray or sparse): Feature matrix (n_samples, n_features).
        labels: Ground truth cluster labels (ndarray).
        dim: Embedding dimensionality.
        temp: Temperature parameter for view weighting.
        beta: Graph regularization parameter.
        max_iter: Max optimization iterations.
        tol: Convergence tolerance.

    Returns:
        dict: Evaluation metrics with keys 'acc', 'nmi', 'ari', 'f1'.
    """
    if labels is None:
        raise ValueError("Ground truth labels are None, cannot compute metrics.")  # noqa: E501

    views_proc = []
    for A, X in views:
        # Note: preprocess_dataset beta param expects float (not int)
        A_norm, X_proc = preprocess_dataset(A, X, beta=beta)  # type: ignore
        if hasattr(X_proc, "toarray"):
            X_proc = X_proc.toarray()
        views_proc.append((A_norm, X_proc))

    # Project features and normalize them
    Hs = [
        StandardScaler(with_std=False).fit_transform(np.asarray(S @ X))
        for S, X in views_proc
    ]

    model = LMGEC(
        n_clusters=len(np.unique(labels)),
        embedding_dim=dim,
        temperature=temp,
        max_iter=max_iter,
        tolerance=tol,
    )
    model.fit(Hs)
    pred = model.labels_

    return {
        "acc": clustering_accuracy(labels, pred), # noqa: E261
        "nmi": nmi(labels, pred),  # noqa: E261
        "ari": ari(labels, pred),
        "f1": clustering_f1_score(labels, pred, average="macro"),  # noqa: E501
    }


def main(args):
    """
    Main function to run hyperparameter tuning.
    """
    views, labels = load_custom_mat(args.data_file)
    if labels is None:
        raise ValueError(
            "Labels not found in dataset. Provide a dataset with ground truth "
            "labels for clustering evaluation."
        )
    if args.n_clusters != len(np.unique(labels)):
        print(
            f"Warning: --n_clusters ({args.n_clusters}) does not match "
            f"number of unique labels ({len(np.unique(labels))})."
        )

    temperatures = [0.1, 0.5, 1.0, 2.0]
    betas = [1.0, 2.0]
    embedding_dims = [3, 4, 5]

    results = []
    for temp, beta, dim in itertools.product(
        temperatures, betas, embedding_dims
    ):
        print(f"Running T={temp}, β={beta}, dim={dim}")
        metrics = run_once(
            views,
            labels,
            dim=dim,
            temp=temp,
            beta=beta,
            max_iter=args.max_iter,
            tol=args.tolerance,
        )
        metrics.update(temperature=temp, beta=beta, embedding_dim=dim)
        results.append(metrics)

    df = pd.DataFrame(results)
    df.to_csv("hyperparam_results.csv", index=False)

    print("\nTop 5 configurations by NMI:")
    print(df.sort_values("nmi", ascending=False).head())

    os.makedirs("plots", exist_ok=True)

    for metric in ("nmi", "ari", "acc", "f1"):
        plt.figure(figsize=(8, 5))
        sns.lineplot(
            data=df,
            x="temperature",
            y=metric,
            hue="embedding_dim",
            style="beta",
            markers=True,
        )
        plt.title(f"{metric.upper()} vs Temperature")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"plots/{metric}_vs_temperature.png")
        plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", type=str, required=True)
    parser.add_argument(
        "--n_clusters", type=int, required=True,
        help="Number of clusters (should match ground truth)"
    )
    parser.add_argument("--max_iter", type=int, default=50)
    parser.add_argument("--tolerance", type=float, default=1e-7)
    args = parser.parse_args()
    main(args)
