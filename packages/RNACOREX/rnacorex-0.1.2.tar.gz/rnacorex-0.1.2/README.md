# RNACOREX

**RNACOREX** is a Python package for building Bayesian Network based classification models using miRNA-mRNA post-transcriptional networks. It uses curated interaction databases and conditional mutual information for identifying sets of interactions and model them using Conditional Linear Gaussian Classifiers (CLGs).

## 🚀 Features

- Extracts structural and functional scores from miRNA-mRNA interactions.
- Identify sets of interactions associated to different phenotypes.
- Build CLG classifiers with the sets of interactions.
- Display the post-transcriptional networks.

Package repository is available at: https://github.com/digital-medicine-research-group-UNAV/RNACOREX

## 📦 Installation

**Important:** Engines must be placed in their path `rnacorex\engines` before running the package.

- `DIANA_targets.txt`
- `Tarbase_v9.tsv`
- `Targetscan_targets.txt`
- `MTB_targets_25.txt`
- `gencode.v47.basic.annotation.gtf`

Download engines from: https://tinyurl.com/StructuralEngine (`RNACOREX` folder)

**Important:** `pygraphviz` must be installed separately using conda **before** installing this package:

```bash
conda install -c conda-forge pygraphviz



