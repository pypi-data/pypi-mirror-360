# Yorzoi: RNA-seq coverage prediction from DNA sequence

yorzoi is a deep neural network that predicts RNA-seq coverage from DNA sequence in Yeast (S. Cerevisiae). It is available via PyPI and Huggingface (see installation).

## Installation

1. You will need an NVIDIA GPU to run Clex.
2. Create a new virtual environment (e.g.: `python -m venv .venv`) and activate it (e.g. `source .venv/bin/activate`)
3. Clex requires FlashAttention to be installed: https://github.com/Dao-AILab/flash-attention. We recommend downloading a pre-built wheel suitable for your GPU.
4. `pip install yorzoi`

## Quick Start: Make a prediction
