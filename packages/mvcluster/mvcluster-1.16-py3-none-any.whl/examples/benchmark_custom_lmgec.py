"""
[EN]
Benchmark the LMGEC clustering algorithm on a custom multi-view dataset
stored in .mat format.

This script performs the following steps:

1. Load the multi-view dataset from a .mat file, where data is organized
   as pairs of adjacency matrices (A_i) and feature matrices (X_i) for
   each view, plus optional ground truth labels.

2. Preprocess each view by normalizing adjacency matrices and preparing
   feature matrices, converting sparse formats to dense if necessary.

3. Run the LMGEC clustering algorithm multiple times (specified by the
   'runs' parameter) with given hyperparameters, fitting the model on
   the preprocessed feature representations.

4. Evaluate clustering performance using metrics including Accuracy,
   Normalized Mutual Information (NMI), Adjusted Rand Index (ARI),
   F1 score, final loss value, and runtime.

5. Aggregate and print the average and standard deviation of these metrics
   over all runs to assess the algorithm’s stability and performance.

Command-line arguments allow flexible configuration of the dataset path,
number of clusters, number of runs, and algorithm-specific hyperparameters
such as temperature, beta (preprocessing), maximum iterations, and
convergence tolerance.

The script depends on external modules from the mvcluster package for the
LMGEC implementation, metrics, and preprocessing utilities.

Usage example:
    python benchmark_custom_lmgec.py --data_file path/to/data.mat
    --n_clusters 3 --runs 5 --temperature 1.0 --beta 1.0

[FR]
Évaluation de l'algorithme de clustering LMGEC sur un jeu de données
multi-vues personnalisé au format .mat.

Ce script réalise les étapes suivantes :

1. Chargement du jeu de données multi-vues depuis un fichier .mat, où les
   données sont organisées en paires de matrices d’adjacence (A_i) et
   matrices de caractéristiques (X_i) pour chaque vue, ainsi que les
   étiquettes de vérité terrain optionnelles.

2. Prétraitement de chaque vue en normalisant les matrices d’adjacence et
   en préparant les matrices de caractéristiques, en convertissant les
   formats creux en denses si nécessaire.

3. Exécution de l’algorithme de clustering LMGEC plusieurs fois (paramètre
   'runs') avec les hyperparamètres spécifiés, en ajustant le modèle sur
   les représentations prétraitées.

4. Évaluation de la performance du clustering à l’aide de métriques telles
   que la précision (Accuracy), l’information mutuelle normalisée (NMI),
   l’indice de Rand ajusté (ARI), le score F1, la valeur finale de la perte,
   et le temps d’exécution.

5. Agrégation et affichage de la moyenne et de l’écart-type de ces métriques
   sur toutes les exécutions pour mesurer la stabilité et l’efficacité de
   l’algorithme.

Les arguments en ligne de commande permettent de configurer le chemin du jeu
de données, le nombre de clusters, le nombre d’exécutions, ainsi que des
hyperparamètres spécifiques tels que la température, beta (prétraitement),
le nombre maximal d’itérations, et la tolérance de convergence.

Le script dépend de modules externes du package mvcluster pour
l’implémentation de LMGEC, les métriques et les outils de prétraitement.

Exemple d’utilisation :
    python benchmark_custom_lmgec.py --data_file chemin/vers/data.mat
    --n_clusters 3 --runs 5 --temperature 1.0 --beta 1.0

"""


import argparse
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np  # noqa: E402
import scipy.io  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402, E501
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score  # noqa: E402, E501

from mvcluster.cluster.lmgec import LMGEC  # noqa: E402
from mvcluster.utils.metrics import clustering_accuracy, clustering_f1_score  # noqa: E402, E501
from mvcluster.utils.preprocess import preprocess_dataset  # noqa: E402


def load_custom_mat(path):
    """Load .mat file with keys: X_0, A_0, X_1, A_1, ..., labels."""
    mat = scipy.io.loadmat(path)
    Xs, As = [], []
    i = 0
    while f"X_{i}" in mat and f"A_{i}" in mat:
        Xs.append(mat[f"X_{i}"])
        As.append(mat[f"A_{i}"].astype(np.float32))
        i += 1
    labels = mat["labels"].squeeze() if "labels" in mat else None
    return As, Xs, labels


def run_custom_lmgec_experiment(
    file_path,
    n_clusters,
    beta=1.0,
    temperature=1.0,
    max_iter=10,
    tolerance=1e-7,
    runs=5,
):
    As, Xs, labels = load_custom_mat(file_path)
    views = list(zip(As, Xs))
    for i, (A, X) in enumerate(views):
        norm_adj, feats = preprocess_dataset(A, X, beta=beta)
        if hasattr(feats, "toarray"):
            feats = feats.toarray()
        views[i] = (norm_adj, feats)

    metrics = {m: [] for m in ["acc", "nmi", "ari", "f1", "loss", "time"]}
    for _ in range(runs):
        start = time.time()
        Hs = [
            StandardScaler(with_std=False).fit_transform(S @ X) for S, X in views]  # noqa: E501

        model = LMGEC(
            n_clusters=n_clusters,
            embedding_dim=n_clusters + 1,
            temperature=temperature,
            max_iter=max_iter,
            tolerance=tolerance,
        )
        model.fit(Hs)

        duration = time.time() - start
        preds = model.labels_

        metrics["time"].append(duration)
        metrics["acc"].append(clustering_accuracy(labels, preds))
        metrics["nmi"].append(
            normalized_mutual_info_score(labels, preds)  # type: ignore
        )  # type: ignore
        metrics["ari"].append(adjusted_rand_score(labels, preds))  # noqa: E501
        metrics["f1"].append(
            clustering_f1_score(labels, preds, average="macro")  # type: ignore
        )  # type: ignore
        metrics["loss"].append(model.loss_history_[-1])

    print("\n=== Averaged Metrics over", runs, "runs ===")
    for key in metrics:
        mean = np.mean(metrics[key])
        std = np.std(metrics[key])
        print(f"{key.upper()}: {mean:.4f} ± {std:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark LMGEC on a custom multi-view dataset"
    )
    parser.add_argument(
        "--data_file",
        type=str,
        required=True,
        help="Path to .mat file containing X_i, A_i, labels",
    )
    parser.add_argument(
        "--n_clusters",
        type=int,
        required=True,
        help="Number of clusters in ground truth",
    )
    parser.add_argument(
        "--runs", type=int, default=5, help="Number of runs to average metrics"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Temperature parameter for LMGEC",
    )
    parser.add_argument(
        "--beta", type=float, default=1.0,
        help="Beta for graph-feature preprocessing"
        )
    parser.add_argument("--max_iter", type=int, default=10)
    parser.add_argument("--tolerance", type=float, default=1e-7)

    args = parser.parse_args()

    run_custom_lmgec_experiment(
        file_path=args.data_file,
        n_clusters=args.n_clusters,
        beta=args.beta,
        temperature=args.temperature,
        max_iter=args.max_iter,
        tolerance=args.tolerance,
        runs=args.runs,
    )
