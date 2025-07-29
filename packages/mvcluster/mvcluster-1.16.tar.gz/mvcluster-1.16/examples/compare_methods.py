"""
compare_methods.py

Compares multiple multiview clustering algorithms
on the same dataset using clustering metrics (NMI, ARI, ACC).

Steps:
    1. Load and preprocess a multi-view dataset.
    2. Apply multiple clustering algorithms to generate labels.
    3. Compute and display evaluation metrics.
    4. Optionally visualize clusters from each method.

Usage:
    python compare_methods.py

Dependencies:
    - mvclustlib.algorithms.*
    - mvclustlib.utils.metrics
    - mvclustlib.utils.plot
"""
