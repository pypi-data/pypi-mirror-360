"""
[EN]
This script loads and visualizes multi-view clustering results from custom
multi-view datasets stored in .mat files. It supports various common .mat file
formats for multi-view data with adjacency and feature matrices, optionally
including ground truth cluster labels.

Main features and workflow:

1. Data Loading:
   - Supports .mat formats with keys such as 'X_i'/'A_i', 'X1', 'features',
     'views', and special cases like 'fea', 'W', and 'gnd'.
   - Handles sparse and dense matrices and converts them as needed.
   - Returns a list of (adjacency matrix, feature matrix) tuples for each view,
     along with optional ground truth labels.

2. Data Preprocessing:
   - Normalizes adjacency matrices and preprocesses feature matrices.
   - Supports tf-idf option disabled here and beta parameter usage.
   - Converts sparse matrices to dense format where necessary.

3. Clustering:
   - Uses the LMGEC (Localized Multi-View Graph Embedding Clustering) model
     for clustering.
   - Automatically determines the number of clusters from labels or defaults
     to 3 if no labels are provided.
   - Embedding dimension is set as clusters + 1.

4. Visualization:
   - Visualizes predicted clusters and, if available, ground truth clusters.
   - Uses PCA for dimensionality reduction before plotting.

5. Command-Line Interface:
   - Requires a path to the .mat dataset.
   - Optional flag to run without ground truth labels.

Dependencies:
- mvcluster package (cluster, utils.plot, utils.preprocess modules)
- numpy, scipy, scikit-learn, argparse, warnings

Usage example:
    python visualize_mvclusters.py --data_file path/to/data.mat
    python visualize_mvclusters.py --data_file path/to/data.mat --no_labels

[FR]
Ce script charge et visualise les résultats de clustering multi-vues à partir
de jeux de données multi-vues personnalisés au format .mat. Il supporte
plusieurs formats .mat communs avec matrices d’adjacence et matrices de
caractéristiques, incluant éventuellement des étiquettes de vérité terrain.

Fonctionnalités principales et déroulement :

1. Chargement des données :
- Supporte les formats .mat avec clés telles que 'X_i'/'A_i', 'X1', 'features',
'views', et cas spéciaux comme 'fea', 'W' et 'gnd'.
- Gère les matrices creuses (sparse) et denses en les convertissant si besoin.
- Retourne une liste de tuples
(matrice d’adjacence, matrice de caractéristiques)
pour chaque vue, ainsi que les étiquettes de vérité terrain optionnelles.

2. Prétraitement des données :
- Normalise les matrices d’adjacence et prépare les matrices
de caractéristiques.
- Supporte l’option tf-idf désactivée ici et l’usage du paramètre beta.
- Convertit les matrices creuses en matrices denses si nécessaire.

3. Clustering :
- Utilise le modèle LMGEC (Localized Multi-View Graph Embedding Clustering)
pour le clustering.
- Détermine automatiquement le nombre de clusters à partir des étiquettes,
ou utilise 3 clusters par défaut si aucune étiquette n’est fournie.
- La dimension d’embedding est fixée à clusters + 1.

4. Visualisation :
- Visualise les clusters prédits et, si disponibles, les clusters de vérité
terrain.
- Utilise l’ACP (PCA) pour réduire la dimension avant affichage.

5. Interface en ligne de commande :
- Nécessite le chemin vers le fichier .mat.
- Option pour exécuter sans étiquettes de vérité terrain.

Dépendances :
- Package mvcluster (modules cluster, utils.plot, utils.preprocess)
- numpy, scipy, scikit-learn, argparse, warnings

Exemples d’utilisation :
    python visualize_mvclusters.py --data_file chemin/vers/data.mat
    python visualize_mvclusters.py --data_file chemin/vers/data.mat --no_labels
"""


import argparse
import os
import sys
import numpy as np
import warnings
from sklearn.preprocessing import StandardScaler
from scipy.io import loadmat
from scipy.sparse import issparse, coo_matrix

# Add the parent directory to the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from mvcluster.cluster import LMGEC
    from mvcluster.utils.plot import visualize_clusters
    from mvcluster.utils.preprocess import preprocess_dataset
except ImportError as e:
    raise ImportError(f"Failed to import required modules: {e}")


def load_custom_mat(path):
    """
    Load .mat file supporting multiple multiview formats.

    Args:
        path (str): Path to the .mat file

    Returns:
        tuple: (list of (A, X) tuples, labels array or None)

    Raises:
        ValueError: If the file structure is unsupported
    """
    mat = loadmat(path)
    Xs, As = [], []
    # Try to get labels (optional)
    labels = None
    for label_key in ['labels', 'label', 'gt', 'ground_truth']:
        if label_key in mat:
            labels = mat[label_key].squeeze()
            break

    # Try X_0/A_0 format
    i = 0
    while f"X_{i}" in mat and f"A_{i}" in mat:
        X = mat[f"X_{i}"]
        A = mat[f"A_{i}"].astype(np.float32)
        if issparse(X):
            X = X.toarray()
        if issparse(A):
            A = A.toarray()
        Xs.append(X)
        As.append(A)
        i += 1
    if Xs:
        return list(zip(As, Xs)), labels

    # Try X1 format (with identity adjacency)
    i = 1
    while f"X{i}" in mat:
        X = mat[f"X{i}"]
        if issparse(X):
            X = X.toarray()
        A = np.eye(X.shape[0], dtype=np.float32)
        Xs.append(X)
        As.append(A)
        i += 1
    if Xs:
        return list(zip(As, Xs)), labels

    # Try features/views format
    for key in ["features", "views", "data"]:
        if key in mat:
            value = mat[key]
            try:
                if isinstance(value, coo_matrix):
                    X = value.toarray()
                    A = np.eye(X.shape[0], dtype=np.float32)
                    return [(A, X)], labels
                elif value.shape == (1,):
                    # Handle cell array format
                    for view in value[0]:
                        X = view.toarray() if issparse(view) else view
                        A = np.eye(X.shape[0], dtype=np.float32)
                        Xs.append(X)
                        As.append(A)
                else:
                    # Handle matrix directly
                    X = value.toarray() if issparse(value) else value
                    A = np.eye(X.shape[0], dtype=np.float32)
                    Xs.append(X)
                    As.append(A)
                if Xs:
                    return list(zip(As, Xs)), labels
            except Exception as e:
                warnings.warn(f"Failed to process key '{key}': {str(e)}")
                continue
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
                labels = np.array(labels)
        return list(zip(As, Xs)), labels

    raise ValueError(
        "Unsupported .mat structure. Expected formats:\n"
        "1. X_0/A_0, X_1/A_1,...\n"
        "2. X1, X2,... (with identity adjacency)\n"
        "3. 'features' or 'views' key with data"
    )


def main():
    """Main function to run the visualization pipeline."""
    parser = argparse.ArgumentParser(
        description="Visualize multiview clustering results."
    )
    parser.add_argument(
        "--data_file",
        type=str,
        required=True,
        help="Path to the .mat multiview dataset"
    )
    parser.add_argument(
        "--no_labels",
        action="store_true",
        help="Run even if dataset has no ground truth labels"
    )
    args = parser.parse_args()

    # Configuration parameters
    temperature = 1.0
    beta = 1.0
    max_iter = 10
    tolerance = 1e-7

    # Load and preprocess data
    views, labels = load_custom_mat(args.data_file)

    if labels is None and not args.no_labels:
        raise ValueError(
            "Dataset must include 'labels' for visualization. "
            "Use --no_labels to run without ground truth."
        )

    # Process each view
    processed_views = []
    for A, X in views:
        # Convert to dense arrays if sparse
        if issparse(A):
            A = A.toarray()  # type: ignore
        if issparse(X):
            X = X.toarray()

        # Ensure proper dimensions
        A = np.asarray(A, dtype=np.float32)
        X = np.asarray(X, dtype=np.float32)

        if X.ndim == 1:
            X = X.reshape(-1, 1)
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            A = np.eye(X.shape[0], dtype=np.float32)

        # Preprocess
        norm_adj, feats = preprocess_dataset(A, X, tf_idf=False, beta=int(beta))  # noqa: E501
        if issparse(feats):
            feats = feats.toarray()
        processed_views.append((np.asarray(norm_adj), np.asarray(feats)))

    # Create feature matrices for each view
    Hs = []
    for S, X in processed_views:
        if X.ndim < 2:
            X = X.reshape(-1, 1)
        if S.ndim < 2:
            S = S.reshape(-1, 1)

        # Standardize features
        H = StandardScaler(with_std=False).fit_transform(S @ X)
        Hs.append(H)

    # Cluster the data
    k = len(np.unique(labels)) if labels is not None else 3
    model = LMGEC(
        n_clusters=k,
        embedding_dim=k + 1,
        temperature=temperature,
        max_iter=max_iter,
        tolerance=tolerance,
    )
    pred_labels = model.fit_predict(Hs)  # type: ignore

    # Visualize results
    X_concat = np.hstack([X for _, X in processed_views])
    visualize_clusters(
        X_concat, pred_labels, method='pca',
        title='Predicted Clusters (LMGEC)'
    )

    if labels is not None:
        visualize_clusters(
            X_concat, labels, method='pca',
            title='Ground Truth Clusters'
        )


if __name__ == "__main__":
    # Suppress runtime warnings about imports
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    main()
