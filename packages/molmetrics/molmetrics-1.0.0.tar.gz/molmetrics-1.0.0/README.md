molmetrics
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/Weeks-UNC/molmetrics/workflows/CI/badge.svg)](https://github.com/Weeks-UNC/molmetrics/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/Weeks-UNC/molmetrics/branch/main/graph/badge.svg)](https://codecov.io/gh/Weeks-UNC/molmetrics/branch/main)
[![PyPI version](https://img.shields.io/pypi/v/molmetrics.svg)](https://pypi.org/project/molmetrics/)


A package for calculating QED scores, molecular descriptors, and optimized geometry descriptors for libraries of small molecules.

## Installation

You can install the latest release of molmetrics from PyPI using pip:

```bash
pip install molmetrics
```

For the best experience, it is recommended to use a virtual environment (such as `venv` or `conda`).

### Conda environment (recommended for reproducibility)

A sample conda environment file is provided at `devtools/conda-envs/test_env.yaml`. To create and activate the environment:

```bash
conda env create -f devtools/conda-envs/test_env.yaml
conda activate molmetrics-test
```

This will install all required dependencies for development and testing.

## Command line options

        -h, --help            show this help message and exit
        -d DIRECTORY, --directory DIRECTORY
                            Path to a directory containing input files (.sdf, .csv, .xlsx, .pkl).
        -f FILE [FILE ...], --file FILE [FILE ...]
                            Path(s) to input file(s) (.sdf, .csv, .xlsx, .pkl). Example: -f file1.sdf file2.csv
        -o OUT, --out OUT     Path to output directory. (Default=directory of input file)
        -c COLUMN, --column COLUMN
                            Name/substring of column containing SMILES strings. (Default=SMILES)
        -s [SUBSTRUCTURES ...], --substructures [SUBSTRUCTURES ...]
                            Provide SMARTS substructure to remove before calculating properties. Use 'diazirine_handle' to
                            remove diazarne FFF handles. (Default=None)
        -p, --properties      Adds QED properties to outputs. (Default=False)
        -md, --moldescriptors
                            Adds selected molecular descriptors to outputs. (Default=False)
        -g, --geometry        Adds NPR1, NPR2, and geometry descriptor to outputs. NOTE: This feature is resource intensive,
                            using the --conformers argument to decrease the required resources. (Default=False)
        -rs RANDOM_SEED, --random_seed RANDOM_SEED
                            Random seed for ETKDGv3 conformer generation. (Default=1789)
        -ft FORCE_TOLERANCE, --force_tolerance FORCE_TOLERANCE
                            Optimizer force tolerance for ETKDGv3 conformer optimization. Use 0.0135 for faster
                            performance. (Default=0.001)
        -pt PRUNE_THRESH, --prune_thresh PRUNE_THRESH
                            RMSD (Å) threshold for filtering conformers during ETKDGv3 generation. Conformers below this
                            threshold are discarded to reduce redundancy. (Default=0.1)
        -cf NUM_CONFORMERS, --num_conformers NUM_CONFORMERS
                            Number of conformers to generate using ETKDGv3. (Default=1000)
        -er ENERGY_RANGE, --energy_range ENERGY_RANGE
                            Energy range in kcal/mol for Boltzmann averaging. (Default=3.0)
        -ni, --no_img         Include 3D molecule images from the output XLSX. (Default=False)

## Output files

Molmetrics generates 4 output files.
        
        XXX_qed.xlsx        # Spreadsheet of all molecular properties calculated with 2D and 3D molecular visualizations.
        XXX_qed.html        # Spreadsheet of all molecular properties calculated with 2D and 3D molecular visualizations.
        XXX_conformers.pkl  # Saved RDKIT mol objects with embedded and optimized conformers.
        XXX_qed.sdf         # Optimized conformer of molecule with embedded molecular properties.

## Copyright

Copyright (c) 2025, Seth D. Veenbaas