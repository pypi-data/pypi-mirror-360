General Purpose Graph Isomorphism Network is a GNN architecture that is able to process graphs with continuous node and edge features.

## Installation

We recommend installing PyTorch and PyTorch Geometric before gpgin-cli to avoid compatibility issues related to CUDA versions and hardware acceleration.

> Note: we recommend using pip rather than conda, as some PyTorch Geometric dependencies are not available via conda.

Refer to:
- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [PyTorch Geometric Installation](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html)

The versions that we used, targeting CUDA-11.8:
```python
torch==2.2.2
torch-geometric==2.5.2
rdkit-pypi==2022.09.5
```

### Install script

This may be useful on a blank python 3.10 virtual environment

```
#!/bin/bash
set -e

# === CONFIGURABLE VARIABLES ===
CUDA_VERSION="cu118"
PYTORCH_VERSION="2.2.2"
TORCHVISION_VERSION="0.17.2"
TORCHAUDIO_VERSION="2.2.2"
TORCH_GEOMETRIC_VERSION="2.5.2"
RDKIT_PYPI_VERSION="2022.09.5"
# === 1. Install PyTorch ===
echo "[1/4] Installing PyTorch with CUDA $CUDA_VERSION..."
pip install torch=="$PYTORCH_VERSION" \
            torchvision=="$TORCHVISION_VERSION" \
            torchaudio=="$TORCHAUDIO_VERSION" \
            --index-url https://download.pytorch.org/whl/$CUDA_VERSION

# === 2. Install PyTorch Geometric core ===
echo "[2/4] Installing PyTorch Geometric $TORCH_GEOMETRIC_VERSION..."
pip install torch_geometric=="$TORCH_GEOMETRIC_VERSION"

# === 3. Install PyTorch Geometric Optional Dependencies ===
echo "[3/4] Installing PyG optional dependencies for CUDA $CUDA_VERSION..."
pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv \
            -f https://data.pyg.org/whl/torch-${PYTORCH_VERSION}+${CUDA_VERSION}.html

# === 4. Install RDKit ===
echo "[4/4] Installing RDKit..."
pip install rdkit-pypi==$RDKIT_PYPI_VERSION

# === Final Step: Install Your CLI Package ===
echo "[✓] Installing your CLI package (gpgin-cli)..."
pip install gpgin-cli

```

## Examples:

Our API expects an SDF file for the `X` field and a line-separated values file for the `y` and `out` field

Training:

```bash
gpgin train \
  -X ./data/gdb9.sdf \
  -y ./data/gdb9_u0.txt \
  --name my_model \
  --batch_size 100 \
  --n_epochs 100 \
  --dataset_name QM9 \
  --target_name u0
# Notes:
# - Models are saved in ~/.gpgin/models
# - Processed datasets are saved in ~/.gpgin/processed
```

Inference:

```bash
gpgin run \
  -X ./data/gdb9.sdf \
  --out ./results/gdb9_u0.txt \
  --name my_model \
  --batch_size 64
```
