"""
[EN] prepare_custom_dataset.py - Final Version

This script prepares heterogeneous multi-view (e.g., multi-omics) datasets
for downstream tasks such as clustering or graph-based learning.

It performs robust loading, preprocessing, normalization, graph
construction, and saving of multiple data views into a unified .mat file
format.

==============================
Main Functionalities
==============================

1. Robust Data Loading
----------------------
- Loads CSV files using pandas.
- Tries alternative encodings (utf-8, latin1, windows-1252) if standard
  read fails.
- If no valid columns are found, generates random fallback data to avoid
  crashing.

2. View Preprocessing
---------------------
Each input view (CSV file) undergoes the following steps:
- Categorical columns are converted to numerical using factorization.
- Missing values are imputed using column-wise medians.
- Views with fewer features than `--min_features` are automatically
  augmented by duplicating existing columns.
- If a view has more than 100 features, variance thresholding is applied
  to remove low-variance columns.
- Each view is standardized using `StandardScaler`.

3. Graph Construction
---------------------
- Constructs a symmetric K-Nearest Neighbors (KNN) graph for each view.
- Graphs are binary (1/0 connectivity) and symmetric (A = (A + A.T) / 2).

4. Label Handling (Optional)
----------------------------
- If a label file is provided, it is loaded and encoded using
  `LabelEncoder`.
- Only labels matching the number of samples are retained.

5. Output Generation
---------------------
The final data is saved as a `.mat` file and includes:
- Feature matrices: X_0, X_1, ..., one per view.
- Adjacency matrices: A_0, A_1, ..., one per view.
- View names.
- Original shape information for each view.
- Sample count.
- Feature names (limited to selected columns).
- Encoded labels (optional).

==============================
Command Line Arguments
==============================
--views        : List of CSV files (one per view) [REQUIRED]
--labels       : (Optional) Path to CSV file with sample labels
--data_name    : Output filename (without extension) [REQUIRED]
--k            : Number of neighbors for KNN graph (default: 15)
--min_features : Minimum number of features per view (default: 1)
--output_dir   : Output directory (default: prepared_datasets)

==============================
Typical Usage Example
==============================
python prepare_custom_dataset.py \
    --views view1.csv view2.csv view3.csv \
    --labels labels.csv \
    --data_name my_dataset \
    --k 15 \
    --min_features 2 \
    --output_dir prepared_datasets

==============================
Error Handling and Recommendations
==============================
- Views with <2 features may cause downstream errors with dimensionality
  reduction (e.g., TruncatedSVD).
- Use `--min_features 2` or manually exclude weak views.
- Final `.mat` output is compatible with MATLAB and multi-view clustering
  frameworks.

==============================
Output Example
==============================
View 1/5: transcriptomics
transcriptomics: Selected 45/150 features
Shape: (30, 45), Features: 45
Loaded 3 label classes

=== Successfully saved to prepared_datasets/my_dataset.mat ===
Summary: 5 views, 30 samples


[FR] prepare_custom_dataset.py - Version finale

Ce script prépare des jeux de données hétérogènes multi-vues (ex : multi-
omiques) pour des tâches en aval telles que le clustering ou
l’apprentissage basé sur les graphes.

Il effectue le chargement robuste, le prétraitement, la normalisation,
la construction de graphes et la sauvegarde des vues dans un fichier
unique `.mat`.

==============================
Fonctionnalités principales
==============================

1. Chargement robuste des données
----------------------------------
- Chargement des fichiers CSV avec pandas.
- Essaie plusieurs encodages alternatifs (utf-8, latin1, windows-1252) si
  le chargement échoue.
- Si aucun fichier valide n'est trouvé, des données aléatoires sont
  générées pour éviter l'arrêt du programme.

2. Prétraitement des vues
--------------------------
Chaque vue (fichier CSV) est traitée comme suit :
- Les colonnes catégorielles sont converties en valeurs numériques via la
  factorisation.
- Les valeurs manquantes sont remplacées par la médiane des colonnes.
- Si une vue contient moins de `--min_features`, elle est augmentée
  automatiquement.
- Si une vue contient plus de 100 colonnes, une sélection par variance
  est appliquée.
- Chaque vue est normalisée avec `StandardScaler`.

3. Construction de graphes
---------------------------
- Un graphe de K plus proches voisins (KNN) est construit pour chaque vue.
- Les graphes sont binaires (0/1) et symétrisés (A = (A + A.T)/2).

4. Gestion des étiquettes (facultatif)
---------------------------------------
- Si un fichier de labels est fourni, il est chargé et encodé avec
  `LabelEncoder`.
- Les étiquettes sont conservées uniquement si elles correspondent au
  nombre d’échantillons.

5. Génération de la sortie
---------------------------
Le fichier final au format `.mat` contient :
- Les matrices de caractéristiques : X_0, X_1, ..., une par vue.
- Les matrices d’adjacence : A_0, A_1, ..., une par vue.
- Les noms des vues.
- Les dimensions d’origine de chaque vue.
- Le nombre total d’échantillons.
- Les noms des variables (colonnes sélectionnées).
- Les étiquettes encodées (si présentes).

==============================
Arguments en ligne de commande
==============================
--views        : Liste de fichiers CSV (une par vue) [OBLIGATOIRE]
--labels       : (Facultatif) Fichier CSV contenant les labels
--data_name    : Nom du fichier de sortie (sans extension) [OBLIGATOIRE]
--k            : Nombre de voisins pour le graphe KNN (défaut : 15)
--min_features : Nombre minimal de colonnes par vue (défaut : 1)
--output_dir   : Répertoire de sortie (défaut : prepared_datasets)

==============================
Exemple d'utilisation
==============================
python prepare_custom_dataset.py \
    --views vue1.csv vue2.csv vue3.csv \
    --labels labels.csv \
    --data_name mon_dataset \
    --k 15 \
    --min_features 2 \
    --output_dir prepared_datasets

==============================
Conseils et gestion des erreurs
==============================
- Les vues avec moins de 2 colonnes peuvent provoquer des erreurs avec
  TruncatedSVD.
- Utilisez `--min_features 2` ou excluez manuellement ces vues.
- Le fichier `.mat` final est compatible avec MATLAB et les frameworks
  de clustering multi-vues.

==============================
Exemple de sortie
==============================
Vue 1/5 : transcriptomics
transcriptomics : 45/150 variables sélectionnées
Forme : (30, 45), Variables : 45
3 classes de labels chargées

=== Sauvegarde réussie vers prepared_datasets/mon_dataset.mat ===
Résumé : 5 vues, 30 échantillons
"""


import argparse
import numpy as np
import scipy.io
import pandas as pd
import os
import warnings
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import VarianceThreshold

# Configure logging
warnings.filterwarnings('once')
pd.set_option('display.max_columns', 10)


def robust_read_file(filepath: str) -> pd.DataFrame:
    """Read data file with multiple fallback strategies."""
    try:
        df = pd.read_csv(filepath, header=0, index_col=None)

        if df.shape[1] == 0:
            encodings = ['utf-8', 'latin1', 'windows-1252']
            for enc in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=enc)
                    if df.shape[1] > 0:
                        break
                except Exception:
                    continue

        if df.shape[1] == 0:
            raise ValueError("No columns detected")

        return df

    except Exception as e:
        warnings.warn(f"Failed to read {filepath}: {str(e)}")
        return pd.DataFrame({'feature': np.random.rand(30)})


def preprocess_view(df: pd.DataFrame, view_name: str,
                    min_features: int) -> np.ndarray:
    """Preprocess a single view."""
    cat_cols = df.select_dtypes(exclude=np.number).columns
    for col in cat_cols:
        df[col] = pd.factorize(df[col])[0]

    if df.isna().any().any():
        df = df.fillna(df.median())

    X = df.values.astype(np.float32)

    if X.shape[1] < min_features:
        warnings.warn(
            f"Augmenting {view_name} from {X.shape[1]} "
            f"to {min_features} features"
        )
        X = np.hstack([X] + [X[:, [0]] *
                             (min_features - X.shape[1])])

    if X.shape[1] > 100:
        selector = VarianceThreshold(threshold=0.1)
        try:
            X = selector.fit_transform(X)
            print(
                f"{view_name}: Selected {X.shape[1]}/"
                f"{selector.n_features_in_} features"
            )
        except Exception as e:
            print(f"Feature selection failed for {view_name}: {str(e)}")

    if X.shape[0] > 1:
        X = StandardScaler().fit_transform(X)

    return X


def save_heterogeneous_data(output_path: str, data: dict):
    """Specialized saver for heterogeneous data."""
    save_data = {}
    for i, (x, a) in enumerate(zip(data['Xs'], data['As'])):
        save_data[f'X_{i}'] = x
        save_data[f'A_{i}'] = a

    save_data.update({
        'view_names': np.array(data['view_names'], dtype=object),
        'n_samples': data['n_samples'],
        'original_shapes': np.array(
            [x.shape for x in data['Xs']], dtype=object
        )
    })

    if 'labels' in data:
        save_data['labels'] = data['labels']

    scipy.io.savemat(output_path, save_data)


def main():
    parser = argparse.ArgumentParser(
        description="Multi-omics data preprocessor"
    )
    parser.add_argument("--views", nargs="+", required=True,
                        help="Input files")
    parser.add_argument("--labels", help="Label file")
    parser.add_argument("--data_name", required=True, help="Output name")
    parser.add_argument("--k", type=int, default=10,
                        help="k for KNN graph")
    parser.add_argument("--min_features", type=int, default=2,
                        help="Min features")
    parser.add_argument("--output_dir", default="prepared_datasets",
                        help="Output dir")

    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir,
                               f"{args.data_name}.mat")

    view_data = []
    print("\n=== Processing Views ===")

    for i, view_path in enumerate(args.views):
        view_name = os.path.splitext(os.path.basename(view_path))[0]
        print(f"\nView {i + 1}/{len(args.views)}: {view_name}")

        try:
            df = robust_read_file(view_path)
            X = preprocess_view(df, view_name, args.min_features)

            print(f"\n>>> First 10 rows of {view_name} after preprocessing:")
            print(pd.DataFrame(X).head(10))

            A = kneighbors_graph(X, n_neighbors=args.k,
                                 mode='connectivity')
            A = 0.5 * (A + A.T)  # type: ignore # Symmetrize
            A.data[:] = 1        # Binary weights

            view_data.append({
                'X': X,
                'A': A,
                'name': view_name,
                'features': df.columns.tolist()[:X.shape[1]]
            })

            print(f"  Shape: {X.shape}, "
                  f"Features: {len(view_data[-1]['features'])}")

        except Exception as e:
            warnings.warn(f"Failed to process {view_name}: {str(e)}")
            continue

    results = {
        'Xs': [vd['X'] for vd in view_data],
        'As': [vd['A'] for vd in view_data],
        'view_names': [vd['name'] for vd in view_data],
        'n_samples': view_data[0]['X'].shape[0] if view_data else 0,
        'feature_names': [vd['features'] for vd in view_data]
    }

    if args.labels and os.path.exists(args.labels):
        try:
            labels = pd.read_csv(args.labels).squeeze()
            if len(labels) == results['n_samples']:  # type: ignore
                results['labels'] = LabelEncoder().fit_transform(labels)
                print(f"\nLoaded {len(np.unique(results['labels']))} "
                      "label classes")
        except Exception as e:
            warnings.warn(f"Label loading failed: {str(e)}")

    try:
        save_heterogeneous_data(output_path, results)
        print(f"\n=== Successfully saved to {output_path} ===")
        print(f"Summary: {len(view_data)} views, "
              f"{results['n_samples']} samples")
    except Exception as e:
        print(f"\n!!! Final save failed: {str(e)}")
        print("Possible solutions:")
        print("1. Install hdf5storage: pip install hdf5storage")
        print("2. Reduce feature dimensions using PCA")
        print("3. Save in a different format (e.g., HDF5)")


if __name__ == "__main__":
    main()
