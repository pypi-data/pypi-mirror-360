# Examples Package - Multi-View Dataset Preparation and Clustering Benchmark

This package contains example scripts to:

- Prepare multi-view datasets by combining multiple CSV files representing different feature views and corresponding labels.

- Run clustering benchmarks on the prepared datasets using customizable parameters such as number of clusters, max iterations, and tolerance.

The included examples cover datasets from various domains, including biological data (Arabidopsis), image features (ALOI), and handwritten digit features (MFEAT).

This README provides example commands to process datasets and evaluate clustering methods end-to-end.


# ----------------------------------------------
# 1) Prepare Arabidopsis multi-view dataset
python examples/prepare_custom_dataset.py \
  --views Altitude_Cluster.csv Ecotype.csv Metabolomics_Rosettes.csv Metabolomics_Stems.csv \
          Phenomics_Rosettes.csv Phenomics_Stems.csv Proteomics_Rosettes_CW.csv Proteomics_Stems_CW.csv \
          Temperature.csv Transcriptomics_Rosettes.csv Transcriptomics_Rosettes_CW.csv \
          Transcriptomics_Stems.csv Transcriptomics_Stems_CW.csv \
  --labels Genetic_Cluster.csv \
  --data_name arabidopsis_all_views

# Run benchmark on prepared Arabidopsis dataset
python -m examples.benchmark_custom_lmgec \
  --data_file prepared_datasets/arabidopsis_all_views.mat \
  --n_clusters 10 \
  --max_iter 5 \
  --tolerance 0.0001

# ----------------------------------------------
# 2) Prepare ALOI multi-view dataset
python examples/prepare_custom_dataset.py \
  --views examples/custom_data/aloi/aloi-27d_clean.csv examples/custom_data/aloi/aloi-64d_clean.csv \
          examples/custom_data/aloi/aloi-haralick-1_clean.csv examples/custom_data/aloi/aloi-hsb-3x3x3_clean.csv \
  --labels examples/custom_data/aloi/objs_labels_10_auto_groups.csv \
  --data_name aloi_dataset

# Run benchmark on prepared ALOI dataset
python -m examples.benchmark_custom_lmgec \
  --data_file prepared_datasets/aloi_dataset.mat \
  --n_clusters 10 \
  --max_iter 5 \
  --tolerance 0.0001

# ----------------------------------------------
# 3) Prepare MFEAT multi-view dataset
python examples/prepare_custom_dataset.py \
  --views examples/custom_data/mfeat/mfeat-fac.csv examples/custom_data/mfeat/mfeat-fou.csv \
          examples/custom_data/mfeat/mfeat-kar.csv examples/custom_data/mfeat/mfeat-mor.csv \
          examples/custom_data/mfeat/mfeat-pix.csv examples/custom_data/mfeat/mfeat-zer.csv \
  --labels examples/custom_data/mfeat/mfeat_label.csv \
  --data_name mfeat_dataset

# Run benchmark on prepared MFEAT dataset
python -m examples.benchmark_custom_lmgec \
  --data_file prepared_datasets/mfeat_dataset.mat \
  --n_clusters 10 \
  --max_iter 50 \
  --tolerance 1e-100

# ----------------------------------------------
# (Optional) Additional example run for MFEAT with different parameters
python -m examples.benchmark_custom_lmgec \
  --data_file prepared_datasets/mfeat_dataset.mat \
  --n_clusters 10 \
  --max_iter 5 \
  --tolerance 0.0001

