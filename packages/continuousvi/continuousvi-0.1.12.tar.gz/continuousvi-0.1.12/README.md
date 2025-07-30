# ContinuousVI

A Python library for analyzing single-cell RNA-seq data with **continuous covariates** using [scVI](https://docs.scvi-tools.org/).

ContinuousVI extends the popular **single-cell Variational Inference** (scVI) framework to incorporate one or more continuous factors (like pseudotime or aging metrics) while correcting for batch effects. It provides straightforward APIs for:

- **Multiple model training** (with different random seeds/initializations)
- **Generating latent embeddings** (e.g., UMAP, clustering)
- **Regression** against continuous covariates (linear, polynomial, spline)
- **Sampling** from the generative model for gene expression distributions

## 🧬 Key Features

1. **Continuous Covariate Support**: Include a single continuous factor (e.g., pseudotime) alongside batch/cell-type labels.
2. **Multiple Model Training**: Train N scVI models with identical hyperparameters but varying seeds, enabling robust downstream analyses.
3. **Dimensionality Reduction & Clustering**: Obtain latent embeddings, run UMAP or Leiden clustering, and easily visualize results.
4. **Gene Expression Sampling**: Sample expression parameters (px) from the learned generative models for posterior predictive analyses.
5. **Regression Tools**: Regress expression levels against the continuous covariate using OLS, polynomial, or spline models (including advanced multi-sampling approaches for uncertainty estimation).

## 📕 Installation

ContinuousVI will be published on PyPI. Once available, you can install it via:

```bash
pip install continuousvi
```

Or install directly from source:

```bash
git clone https://github.com/<your-org>/continuousvi.git
cd continuousvi
pip install .
```

Pip location: [pip](https://pypi.org/project/continuousvi/)

## 🚀 Quick Usage Example

```python
import scanpy as sc
from continuousvi import ContinuousVI

# Load AnnData
adata = sc.read_h5ad("my_data.h5ad")

# Initialize
vi_setup = ContinuousVI(
    adata=adata,
    batch_key="batch",
    label_key="cell_type",
    continuous_key="pseudotime"
)

# Train multiple models
trained_vi = vi_setup.train(n_train=5, n_latent=30)

# Calculate embeddings (UMAP, clustering)
trained_vi.calc_embeddings(resolution=0.5, n_neighbors=10, n_pcs=30)

# Perform a simple linear regression against the continuous covariate
df_regression = trained_vi.regression(mode="ols")
print(df_regression.head())
```

## 🛠️ Developer Guide

### 🔧 Environment Setup with uv

If you use [uv](https://github.com/hoondong/uv) (a command-line tool for managing Python environments), you can set up a development environment as follows:

```bash
# Clone the repository
git clone https://github.com/<your-org>/continuousvi.git
cd continuousvi

# Create and activate a new uv environment (example name: 'contvi-dev')
uv new env contvi-dev
uv activate contvi-dev

# Install an editable version of ContinuousVI along with dev requirements
pip install -e .[dev]
```

> **Note**: The `[dev]` extra (or similar) could include testing and linting dependencies if specified in `setup.cfg` or `pyproject.toml`.

### 📁 Project Structure

- **`ContinuousVI`**: Sets up your AnnData object and trains multiple scVI models.
- **`TrainedContinuousVI`**: Manages trained models, provides methods for embeddings, regression, and sampling.
- **Utility Methods**: Perform regression (linear, polynomial, spline), advanced regression with multi-sampling, and more.

### 🪄 Contributing

1. Fork the repository and create your feature branch from `main`.
2. Make your changes, ensuring that new code is tested and documented.
3. Create a Pull Request, describing your changes and the reason behind them.

## 📝 License

ContinuousVI is licensed under the MIT License (or the license relevant to your project). Please see the [LICENSE](./LICENSE) file for details.
