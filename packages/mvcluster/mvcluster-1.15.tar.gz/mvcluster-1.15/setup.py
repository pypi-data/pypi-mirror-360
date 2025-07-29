from setuptools import setup, find_packages

setup(
    name="mvcluster",
    version="1.15",
    packages=find_packages(include=["mvcluster", "mvcluster.*"]),
    install_requires=[
        "numpy",
        "scikit-learn",
        "torch",
        "scipy",
    ],
    include_package_data=True,
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "prepare-arabidopsis=examples.prepare_custom_dataset:main",
            "benchmark-arabidopsis=examples.benchmark_custom_lmgec:main",
            "prepare-aloi=examples.prepare_custom_dataset:main",
            "benchmark-aloi=examples.benchmark_custom_lmgec:main",
            "prepare-mfeat=examples.prepare_custom_dataset:main",
            "benchmark-mfeat=examples.benchmark_custom_lmgec:main",
            "mvcluster-demo=examples.visualize_clusters:main"
        ]
    }
)
