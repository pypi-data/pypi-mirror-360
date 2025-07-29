"""
evaluate_with_metrics.py

Computes clustering quality metrics (NMI, ARI, ACC) for a selected multiview
clustering algorithm on a benchmark dataset.

Steps:
    1. Run a clustering method on a dataset.
    2. Compare predicted labels against ground truth.
    3. Compute and print evaluation metrics.

Usage:
    python evaluate_with_metrics.py

Dependencies:
    - mvclustlib.algorithms.lmgec
    - mvclustlib.utils.metrics
"""
